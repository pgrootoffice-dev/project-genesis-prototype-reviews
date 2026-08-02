#!/usr/bin/env python3
"""Deterministic FARLENS Motion Seed renderer.

The locked JPEG is always the base frame. Motion is limited to small additive
RGB overlays and, where specified, a sub-1.2% FFmpeg zoom/pan. No generative
model, image synthesis service, or source-layer reconstruction is used.
"""

from __future__ import annotations

import argparse
import math
import subprocess
from pathlib import Path

WIDTH, HEIGHT, FPS = 720, 1280, 30


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def smooth(value: float) -> float:
    value = clamp(value)
    return value * value * (3.0 - 2.0 * value)


def phase(now: float, start: float, end: float) -> float:
    return smooth((now - start) / (end - start))


def decode_rgb(path: Path) -> bytes:
    result = subprocess.run(
        [
            "ffmpeg", "-v", "error", "-i", str(path), "-frames:v", "1",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
        ],
        check=True,
        stdout=subprocess.PIPE,
    )
    expected = WIDTH * HEIGHT * 3
    if len(result.stdout) != expected:
        raise RuntimeError(f"unexpected decoded size for {path}: {len(result.stdout)}")
    return result.stdout


def blend_pixel(frame: bytearray, x: int, y: int, color: tuple[int, int, int], alpha: float) -> None:
    if alpha <= 0 or x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
        return
    alpha = clamp(alpha)
    offset = (y * WIDTH + x) * 3
    inverse = 1.0 - alpha
    frame[offset] = int(frame[offset] * inverse + color[0] * alpha)
    frame[offset + 1] = int(frame[offset + 1] * inverse + color[1] * alpha)
    frame[offset + 2] = int(frame[offset + 2] * inverse + color[2] * alpha)


def disc(frame: bytearray, cx: float, cy: float, radius: float, color: tuple[int, int, int], alpha: float) -> None:
    if radius <= 0 or alpha <= 0:
        return
    left, right = int(cx - radius), int(cx + radius) + 1
    top, bottom = int(cy - radius), int(cy + radius) + 1
    radius_sq = radius * radius
    for y in range(top, bottom):
        for x in range(left, right):
            distance_sq = (x - cx) ** 2 + (y - cy) ** 2
            if distance_sq <= radius_sq:
                edge = 1.0 - math.sqrt(distance_sq) / radius
                blend_pixel(frame, x, y, color, alpha * smooth(edge))


def glow(frame: bytearray, x: float, y: float, strength: float, color=(255, 162, 58), radius: float = 18.0) -> None:
    disc(frame, x, y, radius, color, 0.18 * strength)
    disc(frame, x, y, radius * 0.48, color, 0.30 * strength)
    disc(frame, x, y, max(1.3, radius * 0.12), (255, 236, 180), 0.78 * strength)


def sampled_path(points: list[tuple[float, float]], subdivisions: int = 22) -> list[tuple[float, float]]:
    output: list[tuple[float, float]] = []
    for index in range(len(points) - 1):
        x0, y0 = points[index]
        x1, y1 = points[index + 1]
        for step in range(subdivisions):
            amount = step / subdivisions
            eased = amount * amount * (3 - 2 * amount)
            output.append((x0 + (x1 - x0) * eased, y0 + (y1 - y0) * eased))
    output.append(points[-1])
    return output


def draw_path_range(
    frame: bytearray,
    points: list[tuple[float, float]],
    start: float,
    end: float,
    color: tuple[int, int, int],
    alpha: float,
    width: float = 1.5,
) -> None:
    path = sampled_path(points)
    first = int(clamp(start) * (len(path) - 1))
    last = int(clamp(end) * (len(path) - 1))
    if last <= first:
        return
    for x, y in path[first:last + 1]:
        disc(frame, x, y, width, color, alpha)


def suppress_locked_text(frame: bytearray, amount: float) -> None:
    """Temporarily dim only the bright source pixels that form the locked wordmark.

    This preserves the surrounding background pixel-for-pixel and avoids inventing a
    replacement plate, mask shape, font, position, or tracking.
    """
    amount = clamp(amount)
    if amount <= 0:
        return
    for y in range(954, 989):
        for x in range(248, 477):
            offset = (y * WIDTH + x) * 3
            red, green, blue = frame[offset], frame[offset + 1], frame[offset + 2]
            luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
            if luminance < 42:
                continue
            selection = smooth((luminance - 42) / 55)
            factor = 1.0 - amount * selection
            frame[offset] = int(red * factor)
            frame[offset + 1] = int(green * factor)
            frame[offset + 2] = int(blue * factor)


def render_section0(base: bytes, now: float) -> bytes:
    frame = bytearray(base)
    point_birth = phase(now, 0.55, 1.25)
    line_progress = phase(now, 1.05, 3.55)
    window_warmth = phase(now, 3.15, 4.15)

    glow(frame, 167, 516, point_birth, radius=20)
    path = [(167, 516), (235, 546), (302, 604), (346, 704), (392, 830), (463, 941), (536, 982)]
    draw_path_range(frame, path, 0, line_progress, (255, 146, 35), 0.48, 1.35)
    if line_progress > 0:
        travel = sampled_path(path)
        x, y = travel[int(line_progress * (len(travel) - 1))]
        glow(frame, x, y, 0.36 * (1.0 - phase(now, 3.55, 4.15)), radius=8)

    if window_warmth > 0:
        glow(frame, 585, 1017, 0.24 * window_warmth, color=(255, 174, 63), radius=15)
    return bytes(frame)


SECTION4_FLOWS = [
    ([(0, 365), (85, 472), (244, 529), (330, 590), (368, 656)], (73, 142, 255), 0.55),
    ([(0, 554), (115, 617), (252, 663), (350, 700)], (255, 171, 55), 0.90),
    ([(720, 268), (662, 383), (556, 439), (474, 535), (388, 640)], (52, 126, 255), 1.25),
    ([(720, 460), (617, 490), (536, 568), (480, 670), (383, 716)], (55, 210, 192), 1.60),
    ([(720, 505), (650, 554), (607, 651), (532, 729), (409, 786), (362, 704)], (255, 180, 58), 1.95),
]


def render_section4(base: bytes, now: float) -> bytes:
    frame = bytearray(base)
    for points, color, start in SECTION4_FLOWS:
        travel = phase(now, start, start + 1.75)
        if travel <= 0:
            continue
        head = travel
        tail = max(0.0, head - 0.13)
        opacity = 0.42 * (1.0 - phase(now, start + 1.55, start + 2.30))
        draw_path_range(frame, points, tail, head, color, opacity, 1.45)
        path = sampled_path(points)
        x, y = path[int(head * (len(path) - 1))]
        glow(frame, x, y, opacity * 0.75, color=color, radius=7)
        checkpoint = phase(now, start + 0.72, start + 0.95) * (1.0 - phase(now, start + 1.55, start + 2.1))
        check_x, check_y = path[int(0.62 * (len(path) - 1))]
        glow(frame, check_x, check_y, 0.24 * checkpoint, color=(255, 188, 74), radius=6)

    organized = phase(now, 3.55, 4.05) * (1.0 - 0.42 * phase(now, 4.20, 4.72))
    glow(frame, 361, 696, 0.26 * organized, color=(255, 178, 67), radius=22)
    return bytes(frame)


def render_final(base: bytes, now: float) -> bytes:
    frame = bytearray(base)
    text_reveal = phase(now, 0.95, 2.75)
    suppress_locked_text(frame, 0.94 * (1.0 - text_reveal))

    point_stop = phase(now, 0.30, 1.70)
    # Quietly suppress the locked point only during the short approach, then restore it.
    suppression = 0.72 * (1.0 - phase(now, 1.20, 1.75))
    if suppression > 0:
        disc(frame, 406, 646, 10, (0, 12, 39), suppression)
    moving_x = 392 + 14 * point_stop
    glow_strength = 0.24 * (1.0 - phase(now, 1.65, 2.25))
    glow(frame, moving_x, 646, glow_strength, radius=8)
    if now < 1.8:
        draw_path_range(frame, [(388, 646), (398, 646), (406, 646)], max(0, point_stop - 0.35), point_stop, (235, 126, 31), 0.18, 0.8)
    return bytes(frame)


def encode_scene(source: Path, destination: Path, duration: float, renderer, video_filter: str) -> None:
    base = decode_rgb(source)
    frames = round(duration * FPS)
    destination.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-v", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "-",
        "-an", "-vf", video_filter,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(destination),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    assert process.stdin is not None
    try:
        for frame_number in range(frames):
            now = frame_number / FPS
            process.stdin.write(renderer(base, now))
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError(f"ffmpeg failed while encoding {destination}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    source = root / "assets" / "source"
    master = root / "output" / "master"

    section0_zoom = (
        "zoompan="
        "z='if(lte(on,18),1,if(lte(on,126),1+0.006*(1-cos(PI*(on-18)/108)),1.012))':"
        "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=720x1280:fps=30"
    )
    section4_drift = (
        "zoompan=z='1.006':"
        "x='iw/2-(iw/zoom/2)+if(lte(on,135),1.5*(on/135),1.5)':"
        "y='ih/2-(ih/zoom/2)':d=1:s=720x1280:fps=30"
    )
    encode_scene(source / "section-0-working-lock.jpg", master / "section-0-motion-test.mp4", 5.4, render_section0, section0_zoom)
    encode_scene(source / "section-4-working-lock.jpg", master / "section-4-motion-test.mp4", 5.6, render_section4, section4_drift)
    encode_scene(source / "final-working-lock.jpg", master / "final-motion-test.mp4", 5.4, render_final, "null")


if __name__ == "__main__":
    main()
