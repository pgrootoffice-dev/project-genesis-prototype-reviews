#!/usr/bin/env python3
"""Build source-registered Section 0 D layer PNGs without image generation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

from render_motion import HEIGHT, WIDTH, decode_rgb
from render_section0_c import SECTION0_LOCKED_LINE_PATH


PIXELS = WIDTH * HEIGHT
LAYER_NAMES = [
    "01-background.png",
    "02-earth.png",
    "03-clouds.png",
    "04-connection-line.png",
    "05-traveling-light.png",
    "06-hill.png",
    "07-house.png",
    "08-trees.png",
    "09-window-glow.png",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rgb_at(rgb: bytes | bytearray, x: int, y: int) -> tuple[int, int, int]:
    offset = (y * WIDTH + x) * 3
    return rgb[offset], rgb[offset + 1], rgb[offset + 2]


def set_rgb(rgb: bytearray, x: int, y: int, color: tuple[int, int, int]) -> None:
    offset = (y * WIDTH + x) * 3
    rgb[offset:offset + 3] = bytes(color)


def median(values: list[int]) -> int:
    values = sorted(values)
    return values[len(values) // 2]


def row_background(source: bytes, y: int) -> tuple[int, int, int]:
    sample_y = min(y, 1018)
    xs = [390, 430, 470, 680, 710]
    samples = [rgb_at(source, x, sample_y) for x in xs]
    return tuple(median([sample[channel] for sample in samples]) for channel in range(3))


def mask_earth(source: bytes) -> bytearray:
    mask = bytearray(PIXELS)
    # Circle fitted to three source-edge points: top (270,0), widest
    # (345,280), and the locked origin (167,516). This avoids mistaking the
    # orange connection line for the globe edge in the lower rows.
    center_x, center_y, radius = 17.073586, 217.792789, 333.774580
    for y in range(0, 553):
        inside = radius * radius - (y - center_y) ** 2
        if inside >= 0:
            edge = min(WIDTH - 1, round(center_x + math.sqrt(inside)))
            start = y * WIDTH
            mask[start:start + edge + 1] = b"\x01" * (edge + 1)
    return mask


def mask_clouds(source: bytes) -> bytearray:
    mask = bytearray(PIXELS)
    boxes = [(10, 48, 188, 125), (202, 298, 329, 359)]
    for left, top, right, bottom in boxes:
        for y in range(top, bottom):
            for x in range(left, right):
                r, g, b = rgb_at(source, x, y)
                if r > 62 and g > 98 and b > 118 and (g - r) < 80:
                    mask[y * WIDTH + x] = 1
    return mask


def mask_path(source: bytes) -> bytearray:
    mask = bytearray(PIXELS)
    for left, right in zip(SECTION0_LOCKED_LINE_PATH, SECTION0_LOCKED_LINE_PATH[1:]):
        distance = max(1, round(math.hypot(right[0] - left[0], right[1] - left[1])))
        for step in range(distance + 1):
            amount = step / distance
            cx = round(left[0] + (right[0] - left[0]) * amount)
            cy = round(left[1] + (right[1] - left[1]) * amount)
            for y in range(cy - 5, cy + 6):
                for x in range(cx - 5, cx + 6):
                    if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
                        continue
                    r, g, b = rgb_at(source, x, y)
                    warm = r > 72 and r - b > 28 and r - g > 10 and g > 34
                    if warm:
                        mask[y * WIDTH + x] = 1
    return mask


def mask_traveler(source: bytes) -> bytearray:
    mask = bytearray(PIXELS)
    cx, cy = SECTION0_LOCKED_LINE_PATH[0]
    for y in range(cy - 25, cy + 26):
        for x in range(cx - 25, cx + 26):
            if (x - cx) ** 2 + (y - cy) ** 2 > 25 ** 2:
                continue
            r, g, b = rgb_at(source, x, y)
            if r > 62 and r - b > 24 and r - g > 6:
                mask[y * WIDTH + x] = 1
    return mask


def mask_hill(source: bytes) -> bytearray:
    mask = bytearray(PIXELS)
    for x in range(WIDTH):
        top = HEIGHT
        for y in range(970, HEIGHT - 24):
            if 500 <= x <= 622 and y < 1038:
                continue
            if 620 <= x and y < 1038:
                continue
            bright = 0
            for probe_y in range(y, min(HEIGHT, y + 24)):
                r, g, b = rgb_at(source, x, probe_y)
                bright += int(r > 128 and g > 112 and b > 74)
            if bright >= 20:
                top = y
                break
        if top < HEIGHT:
            for y in range(top, HEIGHT):
                mask[y * WIDTH + x] = 1
    return mask


def mask_house(source: bytes) -> bytearray:
    mask = bytearray(PIXELS)
    for y in range(946, 1046):
        for x in range(500, 625):
            r, g, b = rgb_at(source, x, y)
            if r > 82 and g > 66 and b > 45 and r + g + b > 245:
                mask[y * WIDTH + x] = 1
    return mask


def mask_trees(source: bytes) -> bytearray:
    mask = bytearray(PIXELS)
    for y in range(950, 1065):
        for x in range(615, WIDTH):
            r, g, b = rgb_at(source, x, y)
            canopy = g > 45 and b > 48 and (g - r > 7 or b - r > 13)
            trunk = 638 <= x <= 666 and 986 <= y <= 1057 and b > 32 and b - r > 14
            if canopy or trunk:
                mask[y * WIDTH + x] = 1
    return mask


def mask_window() -> bytearray:
    mask = bytearray(PIXELS)
    for y in range(1005, 1029):
        for x in range(574, 596):
            mask[y * WIDTH + x] = 1
    return mask


def dilate(mask: bytearray, radius: int = 1) -> bytearray:
    output = bytearray(mask)
    selected = [index for index, value in enumerate(mask) if value]
    for index in selected:
        y, x = divmod(index, WIDTH)
        for offset_y in range(-radius, radius + 1):
            for offset_x in range(-radius, radius + 1):
                target_x, target_y = x + offset_x, y + offset_y
                if 0 <= target_x < WIDTH and 0 <= target_y < HEIGHT:
                    output[target_y * WIDTH + target_x] = 1
    return output


def nearest_fill(rgb: bytearray, parent: bytearray, hole: bytearray, max_distance: int = 48) -> None:
    source = bytes(rgb)
    for index, selected in enumerate(hole):
        if not selected or not parent[index]:
            continue
        y, x = divmod(index, WIDTH)
        replacement = None
        for distance in range(1, max_distance + 1):
            for probe_x, probe_y in ((x - distance, y), (x + distance, y), (x, y - distance), (x, y + distance)):
                if not (0 <= probe_x < WIDTH and 0 <= probe_y < HEIGHT):
                    continue
                probe = probe_y * WIDTH + probe_x
                if parent[probe] and not hole[probe]:
                    replacement = rgb_at(source, probe_x, probe_y)
                    break
            if replacement is not None:
                break
        if replacement is not None:
            set_rgb(rgb, x, y, replacement)


def horizontal_fill(rgb: bytearray, parent: bytearray, hole: bytearray) -> None:
    """Replace child holes with smooth row-wise parent interpolation."""
    source = bytes(rgb)
    for y in range(HEIGHT):
        x = 0
        while x < WIDTH:
            index = y * WIDTH + x
            if not (parent[index] and hole[index]):
                x += 1
                continue
            start = x
            while x < WIDTH and parent[y * WIDTH + x] and hole[y * WIDTH + x]:
                x += 1
            end = x - 1
            left = start - 1
            while left >= 0 and not (parent[y * WIDTH + left] and not hole[y * WIDTH + left]):
                left -= 1
            right = end + 1
            while right < WIDTH and not (parent[y * WIDTH + right] and not hole[y * WIDTH + right]):
                right += 1
            if left < 0 and right >= WIDTH:
                continue
            left_color = rgb_at(source, left if left >= 0 else right, y)
            right_color = rgb_at(source, right if right < WIDTH else left, y)
            length = max(1, end - start + 1)
            for fill_x in range(start, end + 1):
                amount = (fill_x - start + 1) / (length + 1)
                color = tuple(round(left_color[channel] * (1 - amount) + right_color[channel] * amount) for channel in range(3))
                set_rgb(rgb, fill_x, y, color)


def fill_cloud_underlay(rgb: bytearray, parent: bytearray, hole: bytearray) -> None:
    """Use a local source-derived solid plate under each small cloud drift."""
    boxes = [(10, 48, 188, 125), (202, 298, 329, 359)]
    source = bytes(rgb)
    for left, top, right, bottom in boxes:
        samples = [[], [], []]
        for y in range(max(0, top - 12), min(HEIGHT, bottom + 12)):
            for x in range(max(0, left - 12), min(WIDTH, right + 12)):
                index = y * WIDTH + x
                border = x < left or x >= right or y < top or y >= bottom
                if not border or not parent[index] or hole[index]:
                    continue
                color = rgb_at(source, x, y)
                for channel in range(3):
                    samples[channel].append(color[channel])
        fill = tuple(median(channel) for channel in samples)
        for y in range(top, bottom):
            for x in range(left, right):
                index = y * WIDTH + x
                if parent[index] and hole[index]:
                    set_rgb(rgb, x, y, fill)


def fill_origin_underlay(rgb: bytearray, parent: bytearray, hole: bytearray) -> None:
    source = bytes(rgb)
    cx, cy = SECTION0_LOCKED_LINE_PATH[0]
    samples = [[], [], []]
    for y in range(cy - 34, cy + 35):
        for x in range(cx - 34, cx + 35):
            index = y * WIDTH + x
            distance = math.hypot(x - cx, y - cy)
            if not (20 <= distance <= 34) or not parent[index] or hole[index]:
                continue
            color = rgb_at(source, x, y)
            if color[0] - color[2] > 20:
                continue
            for channel in range(3):
                samples[channel].append(color[channel])
    fill = tuple(median(channel) for channel in samples)
    for index, selected in enumerate(hole):
        if selected and parent[index]:
            y, x = divmod(index, WIDTH)
            set_rgb(rgb, x, y, fill)


def rgba_for(rgb: bytes | bytearray, mask: bytearray | None) -> bytes:
    output = bytearray(PIXELS * 4)
    for index in range(PIXELS):
        rgb_offset = index * 3
        rgba_offset = index * 4
        output[rgba_offset:rgba_offset + 3] = rgb[rgb_offset:rgb_offset + 3]
        output[rgba_offset + 3] = 255 if mask is None or mask[index] else 0
    return bytes(output)


def write_png(path: Path, rgba: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    process = subprocess.Popen(
        [
            "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba",
            "-s", f"{WIDTH}x{HEIGHT}", "-i", "-", "-frames:v", "1", str(path),
        ],
        stdin=subprocess.PIPE,
    )
    assert process.stdin is not None
    process.stdin.write(rgba)
    process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError(f"failed to encode {path}")


def composite(base: bytearray, layer_rgb: bytes | bytearray, mask: bytearray) -> None:
    for index, selected in enumerate(mask):
        if selected:
            source_offset = index * 3
            base[source_offset:source_offset + 3] = layer_rgb[source_offset:source_offset + 3]


def write_rgb_png(path: Path, rgb: bytes | bytearray) -> None:
    rgba = bytearray(PIXELS * 4)
    for index in range(PIXELS):
        rgba[index * 4:index * 4 + 3] = rgb[index * 3:index * 3 + 3]
        rgba[index * 4 + 3] = 255
    write_png(path, bytes(rgba))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    source_path = root / "assets/source/section-0-working-lock.jpg"
    layer_dir = root / "assets/layers/section-0-d"
    review_dir = root / "assets/review"
    source = decode_rgb(source_path)

    earth = mask_earth(source)
    clouds = dilate(mask_clouds(source))
    connection = mask_path(source)
    traveler = mask_traveler(source)
    hill = mask_hill(source)
    house = dilate(mask_house(source))
    trees = dilate(mask_trees(source))
    # House color selection touches a few green pixels at the right roof edge;
    # tree ownership must win so house tinting cannot erase the canopy.
    for index, selected in enumerate(trees):
        if selected:
            house[index] = 0
    window = mask_window()
    masks = {
        "earth": earth,
        "clouds": clouds,
        "connection-line": connection,
        "traveling-light": traveler,
        "hill": hill,
        "house": house,
        "trees": trees,
        "window-glow": window,
    }

    background = bytearray(source)
    union = bytearray(PIXELS)
    for name, mask in masks.items():
        # The source has a permanent departure anchor at the globe edge.
        # Traveling Light reuses its pixels as a movable hero, while the
        # anchor remains part of Earth/Connection beneath it.
        if name == "traveling-light":
            continue
        for index, selected in enumerate(mask):
            union[index] |= selected
    for index, selected in enumerate(union):
        if selected:
            y, x = divmod(index, WIDTH)
            set_rgb(background, x, y, row_background(source, y))

    earth_rgb = bytearray(source)
    fill_cloud_underlay(earth_rgb, earth, clouds)
    house_rgb = bytearray(source)
    horizontal_fill(house_rgb, house, window)

    layer_rgbs = {
        "background": background,
        "earth": earth_rgb,
        "clouds": source,
        "connection-line": source,
        "traveling-light": source,
        "hill": source,
        "house": house_rgb,
        "trees": source,
        "window-glow": source,
    }
    layer_masks = {
        "background": None,
        "earth": earth,
        "clouds": clouds,
        "connection-line": connection,
        "traveling-light": traveler,
        "hill": hill,
        "house": house,
        "trees": trees,
        "window-glow": window,
    }

    ordered = [
        "background", "earth", "clouds", "connection-line", "traveling-light",
        "hill", "house", "trees", "window-glow",
    ]
    for filename, name in zip(LAYER_NAMES, ordered):
        write_png(layer_dir / filename, rgba_for(layer_rgbs[name], layer_masks[name]))

    recomposed = bytearray(background)
    # Design Z-order: Background → Earth → Clouds → Hill → Trees → House →
    # Window → Connection Line → Traveling Light.
    for name in ["earth", "clouds", "hill", "trees", "house", "window-glow", "connection-line", "traveling-light"]:
        composite(recomposed, layer_rgbs[name], layer_masks[name])
    difference = bytearray(PIXELS * 3)
    absolute_total = 0
    maximum = 0
    changed = 0
    for index, (actual, expected) in enumerate(zip(recomposed, source)):
        delta = abs(actual - expected)
        absolute_total += delta
        maximum = max(maximum, delta)
        if delta:
            changed += 1
        difference[index] = min(255, delta * 8)

    recomposed_path = review_dir / "section-0-d-recomposed.png"
    difference_path = review_dir / "section-0-d-difference.png"
    write_rgb_png(recomposed_path, recomposed)
    write_rgb_png(difference_path, difference)

    manifest = {
        "status": "PASS" if maximum == 0 else "REVIEW",
        "scope": "Section 0 D Layer-first assets — Working / NON-CANONICAL",
        "source": str(source_path.relative_to(root)),
        "canvas": {"width": WIDTH, "height": HEIGHT},
        "layer_count": 9,
        "manual_mask_count": 8,
        "layers": [
            {
                "name": name,
                "file": str((layer_dir / filename).relative_to(root)),
                "sha256": sha256(layer_dir / filename),
                "opaque_pixels": PIXELS if layer_masks[name] is None else int(sum(layer_masks[name])),
            }
            for filename, name in zip(LAYER_NAMES, ordered)
        ],
        "recomposition": {
            "file": str(recomposed_path.relative_to(root)),
            "difference_file": str(difference_path.relative_to(root)),
            "mean_absolute_error": round(absolute_total / (PIXELS * 3), 8),
            "maximum_channel_error": maximum,
            "changed_channel_values": changed,
            "pixel_exact": maximum == 0,
        },
        "new_objects": [],
        "generative_services": [],
        "external_uploads": [],
    }
    manifest_path = root / "section-0-d-layer-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
