#!/usr/bin/env python3
"""Render Section 0 Motion C — source-safe Path-Follow Traveling Light."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from render_motion import disc, draw_path_range, encode_scene, glow, phase
from render_layered_semantic import source_ellipse_layer


# Center coordinates sampled from the orange pixels in the locked JPEG.
# They are data for following the existing line, not a replacement line.
SECTION0_LOCKED_LINE_PATH = [
    (167, 516), (186, 526), (208, 535), (226, 545), (242, 555), (255, 565),
    (267, 575), (279, 585), (288, 595), (296, 605), (304, 615), (311, 625),
    (318, 635), (323, 645), (328, 655), (334, 665), (338, 675), (342, 685),
    (346, 695), (350, 705), (358, 725), (365, 745), (372, 765), (380, 785),
    (387, 805), (396, 825), (405, 845), (415, 865), (428, 885), (441, 905),
    (458, 925), (478, 945), (497, 960), (513, 969), (528, 978), (536, 982),
]


def linear_path(points: list[tuple[float, float]], position: float) -> tuple[float, float]:
    """Return constant-distance position along the traced source polyline."""
    position = max(0.0, min(1.0, position))
    lengths = [
        math.hypot(right[0] - left[0], right[1] - left[1])
        for left, right in zip(points, points[1:])
    ]
    total = sum(lengths)
    target = position * total
    covered = 0.0
    for index, length in enumerate(lengths):
        if covered + length >= target:
            amount = 0.0 if length == 0 else (target - covered) / length
            x0, y0 = points[index]
            x1, y1 = points[index + 1]
            return x0 + (x1 - x0) * amount, y0 + (y1 - y0) * amount
        covered += length
    return points[-1]


def render_section0_c(base: bytes, now: float) -> bytes:
    frame = bytearray(base)
    frozen_now = min(now, 4.30)

    # Beat 1 — the existing navy color plane changes by less than a visible
    # object. It freezes with every other layer at 4.30s.
    background_presence = phase(frozen_now, 0.00, 0.40)
    background_variation = 0.50 + 0.50 * math.sin(frozen_now * 1.35)
    disc(
        frame, 430, 420, 285, (12, 31, 66),
        0.010 * background_presence * background_variation,
    )

    # Beat 2 — two source-cloud regions separate at different rates. Earth,
    # continents, silhouette, and camera remain fixed underneath.
    cloud_one = phase(frozen_now, 0.40, 0.96)
    cloud_two = phase(frozen_now, 0.55, 1.10)
    source_ellipse_layer(
        frame, base, cx=91, cy=92, rx=96, ry=42,
        shift_x=1, shift_y=0, strength=0.13 * cloud_one,
    )
    source_ellipse_layer(
        frame, base, cx=268, cy=333, rx=62, ry=33,
        shift_x=-1, shift_y=0, strength=0.10 * cloud_two,
    )
    origin_awake = phase(frozen_now, 0.40, 1.10)
    origin_departure = phase(frozen_now, 1.10, 1.46)
    glow(frame, 167, 516, 0.38 * origin_awake * (1.0 - 0.55 * origin_departure), radius=15)

    # Beats 3–4 — the sole hero actually moves over the traced source line.
    travel = phase(frozen_now, 1.10, 3.90)
    arrival = phase(frozen_now, 3.88, 4.30)
    if travel > 0:
        # Additive accent only on the already-present line and passed segment.
        draw_path_range(
            frame, SECTION0_LOCKED_LINE_PATH, 0.0, travel,
            (255, 155, 48), 0.16, 0.95,
        )
        x, y = linear_path(SECTION0_LOCKED_LINE_PATH, travel)
        # Existing background color plane reacts locally; no star/particle is added.
        disc(frame, x, y, 42, (31, 53, 89), 0.020 * (1.0 - arrival))
        glow(
            frame, x, y, 1.0 * (1.0 - arrival),
            color=(255, 164, 57), radius=13,
        )
        # A compact warm core keeps the traveler legible after 540px iPhone
        # downscaling. It is the hero light itself, not an added particle.
        disc(frame, x, y, 2.4, (255, 238, 178), 0.82 * (1.0 - arrival))

    # Beat 5 — home reaction is warmer and broader than Earth's awakening.
    # It stabilizes at 4.30s and remains completely still through 5.40s.
    source_ellipse_layer(
        frame, base, cx=588, cy=1026, rx=118, ry=94,
        shift_x=-1, shift_y=0, strength=0.075 * arrival,
    )
    disc(frame, 575, 1036, 58, (255, 194, 108), 0.026 * arrival)
    glow(frame, 585, 1017, 0.52 * arrival, color=(255, 176, 67), radius=17)
    return bytes(frame)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    encode_scene(
        root / "assets/source/section-0-working-lock.jpg",
        root / "output/master/section-0-traveling-light-motion.mp4",
        5.4,
        render_section0_c,
        "null",
    )


if __name__ == "__main__":
    main()
