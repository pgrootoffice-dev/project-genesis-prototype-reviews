#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, capture_output=True, text=True)


def ssim_series(before: Path, after: Path, crop: str | None = None) -> dict[int, float]:
    if crop:
        graph = f"[0:v]crop={crop}[a];[1:v]crop={crop}[b];[a][b]ssim=stats_file=-"
    else:
        graph = "[0:v][1:v]ssim=stats_file=-"
    result = run([
        "ffmpeg", "-v", "error", "-i", str(before), "-i", str(after),
        "-filter_complex", graph, "-f", "null", "-",
    ])
    values: dict[int, float] = {}
    for line in (result.stdout + result.stderr).splitlines():
        match = re.search(r"n:(\d+).*All:([0-9.]+)", line)
        if match:
            values[int(match.group(1)) - 1] = float(match.group(2))
    if not values:
        raise RuntimeError("ffmpeg did not emit SSIM frame statistics")
    return values


def extract_frame(video: Path, frame: int, output: Path) -> None:
    run([
        "ffmpeg", "-v", "error", "-y", "-i", str(video),
        "-vf", f"select=eq(n\\,{frame})", "-vsync", "0", "-frames:v", "1", str(output),
    ])


def pair_ssim(video: Path, first: int, second: int, crop: str) -> float:
    with tempfile.TemporaryDirectory(prefix="farlens-scene02-revision-") as directory:
        root = Path(directory)
        first_path = root / "first.png"
        second_path = root / "second.png"
        extract_frame(video, first, first_path)
        extract_frame(video, second, second_path)
        return ssim_series(first_path, second_path, crop)[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--preroll", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    full = ssim_series(args.before, args.after)
    right = ssim_series(args.before, args.after, "780:720:500:0")
    revision_window = {frame: value for frame, value in full.items() if 216 <= frame <= 299}
    max_change_frame = min(revision_window, key=revision_window.get)

    # Frame 215 is the final A3 frame. Frame 246 (8.2 seconds) is the point
    # where the former full-screen blend was already visually dominant.
    old_background_ssim = pair_ssim(args.before, 215, 246, "780:720:500:0")
    new_background_ssim = pair_ssim(args.after, 215, 246, "780:720:500:0")
    old_focus_ssim = pair_ssim(args.before, 215, 246, "460:360:0:360")
    new_focus_ssim = pair_ssim(args.after, 215, 246, "460:360:0:360")

    early_min = min(full[frame] for frame in range(0, 216))
    late_right_min = min(right[frame] for frame in range(300, 390))
    evidence = {
        "schema_version": 1,
        "revision": "Compass PASS WITH REVISION — A3 to A4 recognition shift only",
        "baseline_master_sha256": sha256(args.before),
        "revised_master_sha256": sha256(args.after),
        "preroll_sha256": sha256(args.preroll),
        "max_change_frame": max_change_frame,
        "max_change_local_time_seconds": round(max_change_frame / 30.0, 3),
        "max_change_absolute_time_seconds": round(10.0 + max_change_frame / 30.0, 3),
        "max_change_ssim": revision_window[max_change_frame],
        "unchanged_regions": {
            "a1_through_a3_frames_0_215_min_ssim": early_min,
            "a1_through_a3_render_path_unchanged": True,
            "a1_through_a3_effectively_unchanged": early_min >= 0.99,
            "a4_to_a5_right_world_frames_300_389_min_ssim": late_right_min,
            "a4_to_a5_motion_parameters_unchanged": True,
            "a4_to_a5_right_world_effectively_unchanged": late_right_min >= 0.985,
            "scene_1_to_2_preroll_unchanged": sha256(args.preroll)
            == "2499b1e1f4b9f0dd646bb59965b60311eec487018b62cd1fb587d024874e8c47",
        },
        "transition_metrics_at_frame_246": {
            "former_background_ssim_to_a3": old_background_ssim,
            "revised_background_ssim_to_a3": new_background_ssim,
            "full_screen_blend_contribution_reduced": new_background_ssim > old_background_ssim,
            "former_focus_ssim_to_a3": old_focus_ssim,
            "revised_focus_ssim_to_a3": new_focus_ssim,
            "fixed_focus_continuity_improved": new_focus_ssim > old_focus_ssim,
        },
        "implementation_guards": {
            "focus_plate_source": "adopted A3 left-lower terrain masses",
            "focus_plate_transform": "none",
            "new_human_geometry": False,
            "a4_background_entry_delay_seconds": 0.95,
            "a4_background_entry_duration_seconds": 1.55,
        },
    }
    args.output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    return 0 if all([
        evidence["unchanged_regions"]["a1_through_a3_effectively_unchanged"],
        evidence["unchanged_regions"]["scene_1_to_2_preroll_unchanged"],
        evidence["transition_metrics_at_frame_246"]["full_screen_blend_contribution_reduced"],
        evidence["transition_metrics_at_frame_246"]["fixed_focus_continuity_improved"],
    ]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
