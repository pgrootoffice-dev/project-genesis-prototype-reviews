#!/usr/bin/env python3
"""Render the non-Canonical Layered Semantic Motion B tests.

Every output starts from the complete locked JPEG. “Layers” are constrained
source-region duplicates, existing-path responses, and local light changes;
there is no background reconstruction, generative fill, or new object.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from render_motion import (
    HEIGHT,
    SECTION4_FLOWS,
    WIDTH,
    clamp,
    disc,
    draw_path_range,
    encode_scene,
    glow,
    phase,
    sampled_path,
    smooth,
)


SECTION0_PATH = [
    (167, 516), (235, 546), (302, 604), (346, 704),
    (392, 830), (463, 941), (536, 982),
]


def blend_source_pixel(
    frame: bytearray,
    base: bytes,
    x: int,
    y: int,
    source_x: int,
    source_y: int,
    alpha: float,
) -> None:
    if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
        return
    source_x = max(0, min(WIDTH - 1, source_x))
    source_y = max(0, min(HEIGHT - 1, source_y))
    target = (y * WIDTH + x) * 3
    source = (source_y * WIDTH + source_x) * 3
    inverse = 1.0 - clamp(alpha)
    frame[target] = int(frame[target] * inverse + base[source] * alpha)
    frame[target + 1] = int(frame[target + 1] * inverse + base[source + 1] * alpha)
    frame[target + 2] = int(frame[target + 2] * inverse + base[source + 2] * alpha)


def source_ellipse_layer(
    frame: bytearray,
    base: bytes,
    *,
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    shift_x: int,
    shift_y: int,
    strength: float,
    feather: float = 0.22,
) -> None:
    """Overlay only source pixels inside a feathered region.

    The unchanged full source remains underneath, so a layer never exposes a
    hole or asks the renderer to invent missing background.
    """
    if strength <= 0:
        return
    left, right = max(0, int(cx - rx)), min(WIDTH, int(cx + rx) + 1)
    top, bottom = max(0, int(cy - ry)), min(HEIGHT, int(cy + ry) + 1)
    inner = 1.0 - feather
    for y in range(top, bottom):
        vertical = (y - cy) / ry
        for x in range(left, right):
            distance = math.sqrt(((x - cx) / rx) ** 2 + vertical ** 2)
            if distance >= 1.0:
                continue
            edge = 1.0 if distance <= inner else 1.0 - smooth((distance - inner) / feather)
            blend_source_pixel(frame, base, x, y, x - shift_x, y - shift_y, strength * edge)


def path_at(points: list[tuple[float, float]], position: float) -> tuple[float, float]:
    path = sampled_path(points)
    return path[int(clamp(position) * (len(path) - 1))]


def layered_section0(base: bytes, now: float) -> bytes:
    frame = bytearray(base)

    # Order 1 — World wakes. The one-pixel source-region offset is a quiet
    # depth cue, not a camera move; the background stays locked.
    world_awake = phase(now, 0.45, 1.30)
    source_ellipse_layer(
        frame, base, cx=83, cy=286, rx=286, ry=332,
        shift_x=1, shift_y=-1, strength=0.075 * world_awake,
    )
    glow(frame, 167, 516, 0.62 * world_awake, radius=17)

    # Order 2 — Connection advances on the existing trajectory. A broad,
    # extremely weak wake lets the intervening space respond before the
    # narrower path accent; the hero is not just a travelling point.
    connection = phase(now, 1.20, 3.70)
    draw_path_range(frame, SECTION0_PATH, 0.0, connection, (63, 112, 170), 0.030, 13.0)
    draw_path_range(frame, SECTION0_PATH, 0.0, connection, (255, 150, 42), 0.25, 1.15)
    if 0.0 < connection < 1.0:
        x, y = path_at(SECTION0_PATH, connection)
        glow(frame, x, y, 0.21, radius=7)

    # Order 3 — The family side receives the meaning. The source-defined home
    # region gains a one-pixel depth separation, followed by a local warmth.
    arrival = phase(now, 3.45, 4.42)
    source_ellipse_layer(
        frame, base, cx=590, cy=1024, rx=112, ry=91,
        shift_x=-1, shift_y=0, strength=0.085 * arrival,
    )
    disc(frame, 586, 1017, 33, (255, 187, 88), 0.018 * arrival)
    glow(frame, 585, 1017, 0.29 * arrival, color=(255, 174, 63), radius=14)
    return bytes(frame)


def layered_section4(base: bytes, now: float) -> bytes:
    frame = bytearray(base)

    # Five main semantic layers: locked background, Flow A, Flow B,
    # Verification Points, Meaning Core. Flow groups deliberately start apart.
    group_starts = {0: 0.42, 2: 0.68, 1: 0.96, 3: 1.18, 4: 1.40}
    for index, (points, color, _old_start) in enumerate(SECTION4_FLOWS):
        start = group_starts[index]
        collected = phase(now, start, start + 1.45)
        verified = phase(now, start + 1.42, start + 1.82)
        if collected <= 0:
            continue

        # Order 1 — gather with restrained depth differences. The groups use
        # different corridor widths/opacities and never move in unison.
        group_a = index in {0, 2}
        depth_width = 8.5 if group_a else 11.0
        depth_alpha = 0.030 if group_a else 0.022
        draw_path_range(frame, points, 0.0, collected, color, depth_alpha, depth_width)
        tail = max(0.0, collected - (0.14 if group_a else 0.11))
        draw_path_range(frame, points, tail, collected, color, 0.28 * (1.0 - 0.62 * verified), 1.35)

        # Order 2 — verify sequentially. Before verification, the travelling
        # point retains a sub-pixel-feeling normal offset; afterwards the
        # confirmed segment settles on the original path.
        path = sampled_path(points)
        position = int(collected * (len(path) - 1))
        x, y = path[position]
        if verified < 0.5:
            y += math.sin(now * 3.2 + index * 0.9) * 0.9
        glow(frame, x, y, 0.14 * (1.0 - verified), color=color, radius=6)

        checkpoint_x, checkpoint_y = path[int(0.62 * (len(path) - 1))]
        check_hold = verified * (1.0 - 0.70 * phase(now, start + 1.95, start + 2.30))
        glow(frame, checkpoint_x, checkpoint_y, 0.18 * check_hold, color=(255, 187, 75), radius=6)

        # Only a confirmed flow receives the quiet, uniform route toward the
        # core. Unconfirmed paths retain the moving/wavering head above.
        organized_end = 0.62 + 0.34 * verified
        draw_path_range(frame, points, 0.62, organized_end, color, 0.12 * verified, 1.15)

    # Order 3 — read/interpret. One non-oscillating response, then a stable hold.
    core_arrival = phase(now, 3.55, 4.18)
    core_settle = phase(now, 4.18, 4.48)
    core_strength = core_arrival * (1.0 - 0.48 * core_settle)
    glow(frame, 361, 696, 0.35 * core_strength, color=(255, 178, 67), radius=21)
    disc(frame, 361, 696, 34, (63, 150, 188), 0.017 * core_arrival)
    return bytes(frame)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    source = root / "assets" / "source"
    master = root / "output" / "master"

    encode_scene(
        source / "section-0-working-lock.jpg",
        master / "section-0-layered-semantic-motion.mp4",
        5.4,
        layered_section0,
        "null",
    )
    encode_scene(
        source / "section-4-working-lock.jpg",
        master / "section-4-layered-semantic-motion.mp4",
        5.6,
        layered_section4,
        "null",
    )


if __name__ == "__main__":
    main()
