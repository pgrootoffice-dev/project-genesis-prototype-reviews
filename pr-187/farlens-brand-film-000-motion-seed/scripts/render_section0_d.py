#!/usr/bin/env python3
"""Render Section 0 D from independent, source-registered PNG layers."""

from __future__ import annotations

import argparse
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path

from render_motion import HEIGHT, WIDTH, FPS, clamp, disc, draw_path_range, glow, phase
from render_section0_c import SECTION0_LOCKED_LINE_PATH, linear_path


@dataclass
class Layer:
    rgb: bytes
    alpha: bytes
    spans: list[list[tuple[int, int]]]
    pixels: list[int]


def decode_rgba(path: Path) -> bytes:
    result = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgba", "-"],
        check=True,
        stdout=subprocess.PIPE,
    )
    expected = WIDTH * HEIGHT * 4
    if len(result.stdout) != expected:
        raise RuntimeError(f"unexpected RGBA size for {path}: {len(result.stdout)}")
    return result.stdout


def make_layer(rgba: bytes, predicate=None) -> Layer:
    rgb = bytearray(WIDTH * HEIGHT * 3)
    alpha = bytearray(WIDTH * HEIGHT)
    pixels = []
    rows: list[list[tuple[int, int]]] = [[] for _ in range(HEIGHT)]
    for index in range(WIDTH * HEIGHT):
        x, y = index % WIDTH, index // WIDTH
        source = index * 4
        destination = index * 3
        rgb[destination:destination + 3] = rgba[source:source + 3]
        selected = rgba[source + 3] > 0 and (predicate is None or predicate(x, y))
        if selected:
            alpha[index] = rgba[source + 3]
            pixels.append(index)
    for y in range(HEIGHT):
        x = 0
        while x < WIDTH:
            if alpha[y * WIDTH + x] == 0:
                x += 1
                continue
            start = x
            while x < WIDTH and alpha[y * WIDTH + x] == 255:
                x += 1
            if x > start:
                rows[y].append((start, x))
            while x < WIDTH and alpha[y * WIDTH + x] != 0:
                x += 1
    return Layer(bytes(rgb), bytes(alpha), rows, pixels)


def load_layers(root: Path) -> dict[str, Layer]:
    directory = root / "assets/layers/section-0-d"
    files = {
        "background": "01-background.png",
        "earth": "02-earth.png",
        "clouds": "03-clouds.png",
        "line": "04-connection-line.png",
        "traveler": "05-traveling-light.png",
        "hill": "06-hill.png",
        "house": "07-house.png",
        "trees": "08-trees.png",
        "window": "09-window-glow.png",
    }
    return {name: make_layer(decode_rgba(directory / filename)) for name, filename in files.items()}


def sublayer(layer: Layer, left: int, top: int, right: int, bottom: int) -> Layer:
    rgba = bytearray(WIDTH * HEIGHT * 4)
    for index in layer.pixels:
        y, x = divmod(index, WIDTH)
        if left <= x < right and top <= y < bottom:
            rgba[index * 4:index * 4 + 3] = layer.rgb[index * 3:index * 3 + 3]
            rgba[index * 4 + 3] = layer.alpha[index]
    return make_layer(bytes(rgba))


def coordinate_layer(layer: Layer, predicate) -> Layer:
    rgba = bytearray(WIDTH * HEIGHT * 4)
    for index in layer.pixels:
        y, x = divmod(index, WIDTH)
        if predicate(x, y):
            rgba[index * 4:index * 4 + 3] = layer.rgb[index * 3:index * 3 + 3]
            rgba[index * 4 + 3] = layer.alpha[index]
    return make_layer(bytes(rgba))


def filtered_layer(layer: Layer, predicate) -> Layer:
    rgba = bytearray(WIDTH * HEIGHT * 4)
    for index in layer.pixels:
        r, g, b = layer.rgb[index * 3:index * 3 + 3]
        if predicate(r, g, b):
            rgba[index * 4:index * 4 + 3] = bytes((r, g, b))
            rgba[index * 4 + 3] = layer.alpha[index]
    return make_layer(bytes(rgba))


def tint(layer: Layer, red: float, green: float, blue: float) -> Layer:
    rgba = bytearray(WIDTH * HEIGHT * 4)
    factors = (red, green, blue)
    for index in layer.pixels:
        for channel in range(3):
            rgba[index * 4 + channel] = round(clamp(layer.rgb[index * 3 + channel] * factors[channel], 0, 255))
        rgba[index * 4 + 3] = layer.alpha[index]
    return make_layer(bytes(rgba))


def warp_canopy(layer: Layer, amount: float, top: int, base_y: int) -> Layer:
    rgba = bytearray(WIDTH * HEIGHT * 4)
    height = max(1, base_y - top)
    for index in layer.pixels:
        y, x = divmod(index, WIDTH)
        weight = clamp((base_y - y) / height)
        target_x = round(x + amount * weight)
        if not (0 <= target_x < WIDTH):
            continue
        target = y * WIDTH + target_x
        rgba[target * 4:target * 4 + 3] = layer.rgb[index * 3:index * 3 + 3]
        rgba[target * 4 + 3] = layer.alpha[index]
    return make_layer(bytes(rgba))


def paste(frame: bytearray, layer: Layer, dx: int = 0, dy: int = 0, opacity: float = 1.0) -> None:
    opacity = clamp(opacity)
    if opacity <= 0:
        return
    if opacity >= 0.999 and dx == 0 and dy == 0:
        for y, row in enumerate(layer.spans):
            for start, end in row:
                frame[(y * WIDTH + start) * 3:(y * WIDTH + end) * 3] = layer.rgb[(y * WIDTH + start) * 3:(y * WIDTH + end) * 3]
        return
    for index in layer.pixels:
        source_y, source_x = divmod(index, WIDTH)
        x, y = source_x + dx, source_y + dy
        if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
            continue
        alpha = layer.alpha[index] / 255.0 * opacity
        destination = (y * WIDTH + x) * 3
        source = index * 3
        inverse = 1.0 - alpha
        for channel in range(3):
            frame[destination + channel] = round(frame[destination + channel] * inverse + layer.rgb[source + channel] * alpha)


def background_variants(layer: Layer) -> list[bytes]:
    variants = []
    for index in range(48):
        frame = bytearray(layer.rgb)
        amount = index / 47
        cx = 335 + 85 * amount
        cy = 390 + 30 * math.sin(amount * math.pi)
        disc(frame, cx, cy, 290, (13, 35, 76), 0.018 + 0.006 * math.sin(amount * math.pi))
        variants.append(bytes(frame))
    return variants


class Section0DRenderer:
    def __init__(self, root: Path):
        self.layers = load_layers(root)
        self.backgrounds = background_variants(self.layers["background"])
        self.cloud_one = sublayer(self.layers["clouds"], 0, 35, 200, 145)
        self.cloud_two = sublayer(self.layers["clouds"], 190, 285, 350, 375)
        self.tree_main = coordinate_layer(
            self.layers["trees"],
            lambda x, y: 610 <= x < WIDTH and 945 <= y < 1058 and (y < 1002 or x < 660),
        )
        self.tree_bushes = coordinate_layer(
            self.layers["trees"],
            lambda x, y: 660 <= x < WIDTH and 1002 <= y < 1070,
        )
        self.motion_traveler = coordinate_layer(
            filtered_layer(
                self.layers["traveler"],
                lambda r, g, b: (r > 185 and g > 92 and r - b > 42)
                or (r > 215 and g > 185 and b > 115),
            ),
            lambda x, y: (x - 167) ** 2 + (y - 516) ** 2 <= 14 ** 2,
        )
        self.tree_main_variants = {amount: warp_canopy(self.tree_main, amount, 945, 1052) for amount in range(-3, 4)}
        self.tree_bush_variants = {amount: warp_canopy(self.tree_bushes, amount, 1002, 1057) for amount in range(-2, 3)}
        self.hill_variants = [tint(self.layers["hill"], 1.0 + 0.042 * i / 12, 1.0 + 0.018 * i / 12, 1.0 - 0.020 * i / 12) for i in range(13)]
        self.house_variants = [tint(self.layers["house"], 1.0 + 0.028 * i / 12, 1.0 + 0.014 * i / 12, 1.0 - 0.012 * i / 12) for i in range(13)]
        self.window_variants = [tint(self.layers["window"], 0.94 + 0.34 * i / 24, 0.94 + 0.25 * i / 24, 0.94 + 0.10 * i / 24) for i in range(25)]

    def motion_frame(self, now: float) -> bytes:
        frozen = min(now, 4.30)
        background_index = min(47, round(47 * frozen / 4.30))
        frame = bytearray(self.backgrounds[background_index])

        travel = phase(frozen, 1.10, 4.20)
        arrival = phase(frozen, 3.90, 4.30)
        if travel > 0:
            x, y = linear_path(SECTION0_LOCKED_LINE_PATH, travel)
            disc(frame, x, y, 54, (28, 49, 86), 0.028 * (1.0 - arrival))

        paste(frame, self.layers["earth"])
        wake = phase(frozen, 0.05, 0.48) * (1.0 - phase(frozen, 0.72, 1.10))
        glow(frame, 167, 516, 1.35 * wake, radius=24)

        cloud_progress = clamp((frozen - 0.30) / 4.00)
        cloud_opacity = 0.97 + 0.03 * (0.5 + 0.5 * math.sin(frozen * 2.15))
        paste(frame, self.cloud_one, dx=round(16 * cloud_progress), opacity=cloud_opacity)
        paste(frame, self.cloud_two, dx=round(-22 * cloud_progress), opacity=1.0 - 0.02 * math.sin(frozen * 1.75) ** 2)

        warmth = phase(frozen, 3.30, 4.30)
        paste(frame, self.hill_variants[min(12, round(warmth * 12))])

        tree_phase = clamp((frozen - 2.60) / 0.70)
        main_amount = round(3 * math.sin(tree_phase * 2 * math.pi)) if 0 < tree_phase < 1 else 0
        bush_phase = clamp((frozen - 2.68) / 0.62)
        bush_amount = round(2 * math.sin(bush_phase * 2 * math.pi)) if 0 < bush_phase < 1 else 0
        paste(frame, self.tree_main_variants[main_amount])
        paste(frame, self.tree_bush_variants[bush_amount])

        house_reaction = phase(frozen, 3.30, 4.22)
        house_shift = -round(math.sin(house_reaction * math.pi)) if house_reaction < 1 else 0
        paste(frame, self.house_variants[min(12, round(warmth * 12))], dy=house_shift)

        if frozen < 0.30:
            window_level = 0.18
        else:
            breath = 0.5 + 0.5 * math.sin((frozen - 0.30) * math.tau / 1.85)
            base_level = 0.10 + 0.32 * breath
            window_level = base_level * (1.0 - arrival) + arrival
        paste(frame, self.window_variants[min(24, round(window_level * 24))])

        paste(frame, self.layers["line"])
        if travel > 0:
            draw_path_range(frame, SECTION0_LOCKED_LINE_PATH, max(0.0, travel - 0.11), travel, (255, 167, 65), 0.22, 1.05)
            x, y = linear_path(SECTION0_LOCKED_LINE_PATH, travel)
            origin_x, origin_y = SECTION0_LOCKED_LINE_PATH[0]
            paste(
                frame,
                self.motion_traveler,
                dx=round(x - origin_x),
                dy=round(y - origin_y),
                opacity=1.0 - arrival,
            )
            glow(frame, x, y, 0.34 * (1.0 - arrival), color=(255, 166, 63), radius=7)
            disc(frame, x, y, 2.2, (255, 244, 205), 0.88 * (1.0 - arrival))
        return bytes(frame)

    def breakdown_frame(self, now: float) -> bytes:
        frame = bytearray(self.layers["background"].rgb)
        order = ["earth", "clouds", "hill", "trees", "house", "window", "line", "traveler"]
        for index, name in enumerate(order, start=1):
            # A hard, paced reveal keeps semi-transparent mask boundaries from
            # being mistaken for defects in the layer assets themselves.
            if now >= index * 0.60 - 0.18:
                paste(frame, self.layers[name])
        return bytes(frame)


def encode(destination: Path, duration: float, renderer) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    process = subprocess.Popen(
        [
            "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "-", "-an",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(destination),
        ],
        stdin=subprocess.PIPE,
    )
    assert process.stdin is not None
    for frame_number in range(round(duration * FPS)):
        process.stdin.write(renderer(frame_number / FPS))
    process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError(f"ffmpeg failed for {destination}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    renderer = Section0DRenderer(root)
    encode(root / "output/master/section-0-layer-first-motion.mp4", 5.4, renderer.motion_frame)
    encode(root / "output/master/section-0-layer-breakdown.mp4", 5.4, renderer.breakdown_frame)


if __name__ == "__main__":
    main()
