#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


EXPECTED_SCENE2_SHA = "3e51b0fbf461d7cfc49c91c05420777f2da1bc843b476a65127483fb50a76904"
EXPECTED_TERMINAL_SHA = "32b9a74ea1ee1a01386671726abb47201bdcbc7c3ff4dd2f59a51cd157258c1c"
EXPECTED_SCENE1_SHA = "f684be2ebcb176f043f419bdfed297bbeb1e4eb7ef68dae98cfbc462197d1b79"
EXPECTED_IPHONE_SHA = "2c7dce60db133313a5853ff66b77243879900e188e09d7735aee1ba3b34ef5a5"
EXPECTED_BASELINE_SHA = "d9d5eec5fc14a80f45f3c22de57c3d3b3dc8579e8f33f8749aab0731349534dc"
EXPECTED_TRANSITION_FRAME_HASHES = {
    300: "7a454c6ffda50b125d299cdd37bfbf0b",
    306: "f6b0664490d7ca929019cc974a1f0e7b",
    312: "c380b7b8fa221d84b8a559fdb233c724",
    318: "b9f6f18b3852f84caea4478d9ba5aec5",
    326: "2dc30c2f4c819914e07c199a83f8f5ef",
    333: "5da7ded449880e0bdb2345462211eb9d",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-count_frames", "-show_entries",
            "format=duration,size:stream=codec_name,codec_type,width,height,r_frame_rate,pix_fmt,nb_read_frames",
            "-of", "json", str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def frame_hashes(path: Path) -> list[str]:
    result = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "framemd5", "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    hashes: list[str] = []
    for line in result.stdout.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        fields = [field.strip() for field in line.split(",")]
        if len(fields) >= 6:
            hashes.append(fields[-1])
    return hashes


def boundary_ssim(scene1: Path, scene2: Path) -> float | None:
    result = subprocess.run(
        [
            "ffmpeg", "-v", "info", "-sseof", "-0.04", "-i", str(scene1),
            "-ss", "0", "-i", str(scene2),
            "-filter_complex", "[0:v]select='eq(n,0)',setpts=PTS-STARTPTS[a];[1:v]select='eq(n,0)',setpts=PTS-STARTPTS[b];[a][b]ssim",
            "-frames:v", "1", "-f", "null", "-",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    match = re.search(r"All:([0-9.]+)", result.stderr)
    return float(match.group(1)) if match else None


def sequence_ssim(reference: Path, review: Path, reference_start: float, review_start: float, duration: float) -> float | None:
    result = subprocess.run(
        [
            "ffmpeg", "-v", "info", "-ss", str(reference_start), "-i", str(reference),
            "-ss", str(review_start), "-i", str(review), "-t", str(duration),
            "-lavfi", "[0:v][1:v]ssim", "-f", "null", "-",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    matches = re.findall(r"All:([0-9.]+)", result.stderr)
    return float(matches[-1]) if matches else None


def frame_pair_ssim(path: Path, first_time: float, second_time: float) -> float | None:
    result = subprocess.run(
        [
            "ffmpeg", "-v", "info", "-ss", str(first_time), "-i", str(path),
            "-ss", str(second_time), "-i", str(path),
            "-filter_complex", "[0:v]select='eq(n,0)',setpts=PTS-STARTPTS[a];[1:v]select='eq(n,0)',setpts=PTS-STARTPTS[b];[a][b]ssim",
            "-frames:v", "1", "-f", "null", "-",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    matches = re.findall(r"All:([0-9.]+)", result.stderr)
    return float(matches[-1]) if matches else None


def corresponding_frame_ssim(first: Path, first_time: float, second: Path, second_time: float) -> float | None:
    result = subprocess.run(
        [
            "ffmpeg", "-v", "info", "-ss", str(first_time), "-i", str(first),
            "-ss", str(second_time), "-i", str(second),
            "-filter_complex", "[0:v]select='eq(n,0)',setpts=PTS-STARTPTS[a];[1:v]select='eq(n,0)',setpts=PTS-STARTPTS[b];[a][b]ssim",
            "-frames:v", "1", "-f", "null", "-",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    matches = re.findall(r"All:([0-9.]+)", result.stderr)
    return float(matches[-1]) if matches else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene1", required=True, type=Path)
    parser.add_argument("--iphone", required=True, type=Path)
    parser.add_argument("--scene2", required=True, type=Path)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--terminal", required=True, type=Path)
    parser.add_argument("--terminal-reference", required=True, type=Path)
    parser.add_argument("--envelopes", required=True, type=Path)
    parser.add_argument("--implementation", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    review_hashes = frame_hashes(args.review)
    scene1_sha = sha256(args.scene1)
    iphone_sha = sha256(args.iphone)
    scene2_sha = sha256(args.scene2)
    baseline_sha = sha256(args.baseline)
    terminal_sha = sha256(args.terminal)
    terminal_reference_sha = sha256(args.terminal_reference)
    review_probe = probe(args.review)
    review_stream = next(item for item in review_probe["streams"] if item.get("codec_type") == "video")
    envelopes = json.loads(args.envelopes.read_text(encoding="utf-8"))
    layers = envelopes["layers"]
    implementation_source = args.implementation.read_text(encoding="utf-8")

    scene1_ssim = sequence_ssim(args.scene1, args.review, 0.0, 0.0, 10.0)
    scene2_tail_ssim = sequence_ssim(args.scene2, args.review, 1.1, 11.1, 11.9)
    hold_ssim = frame_pair_ssim(args.scene1, 9.3, 9.95)
    layer_ids = [item["id"] for item in sorted(layers, key=lambda item: item["order"])]
    layer_starts = [item["review_start"] for item in sorted(layers, key=lambda item: item["order"])]
    expected_layer_ids = ["warm_center_melt", "dark_air_horizon", "terrain", "lower_left_mass", "information_membranes"]
    transition = envelopes["transition"]
    rendered_transition_frame_hashes = {
        frame: review_hashes[frame] for frame in EXPECTED_TRANSITION_FRAME_HASHES
    }
    expected_implementation_envelopes = {
        item["id"]: {
            "start": round(item["review_start"] - transition["review_start"], 6),
            "duration": round(item["review_end"] - item["review_start"], 6),
        }
        for item in layers
    }
    implementation_envelopes = {}
    warm_match = re.search(r"fade=t=in:st=([0-9.]+):d=([0-9.]+):alpha=1\"", implementation_source)
    if warm_match:
        implementation_envelopes["warm_center_melt"] = {
            "start": float(warm_match.group(1)),
            "duration": float(warm_match.group(2)),
        }
    implementation_labels = {
        "dark_air_horizon": "atmo",
        "terrain": "terrain",
        "lower_left_mass": "leftmass",
        "information_membranes": "membranes",
    }
    for layer_id, output_label in implementation_labels.items():
        match = re.search(
            rf"fade=t=in:st=([0-9.]+):d=([0-9.]+):alpha=1\[{output_label}\]",
            implementation_source,
        )
        if match:
            implementation_envelopes[layer_id] = {
                "start": float(match.group(1)),
                "duration": float(match.group(2)),
            }
    composite_order = ["[cooled][atmo]", "[s1][terrain]", "[s2][leftmass]", "[s3][membranes]"]
    review_frame_332_to_scene2_32_ssim = corresponding_frame_ssim(args.review, 332 / 30, args.scene2, 32 / 30)
    review_frame_333_to_scene2_33_ssim = corresponding_frame_ssim(args.review, 333 / 30, args.scene2, 33 / 30)

    checks = {
        "scene_1_master_sha_unchanged": scene1_sha == EXPECTED_SCENE1_SHA,
        "scene_1_iphone_sha_unchanged": iphone_sha == EXPECTED_IPHONE_SHA,
        "scene_1_segment_faithful": scene1_ssim is not None and scene1_ssim >= 0.99,
        "scene_2_after_transition_faithful": scene2_tail_ssim is not None and scene2_tail_ssim >= 0.99,
        "scene_2_reference_sha_unchanged": scene2_sha == EXPECTED_SCENE2_SHA,
        "reviewed_baseline_sha_locked": baseline_sha == EXPECTED_BASELINE_SHA,
        "scene_1_terminal_matches_pr191_reference": terminal_sha == terminal_reference_sha == EXPECTED_TERMINAL_SHA,
        "scene_1_terminal_hold_present": hold_ssim is not None and hold_ssim >= 0.99,
        "transition_duration_1_1_seconds": abs(transition["duration"] - 1.1) <= 0.001,
        "layer_order_locked": layer_ids == expected_layer_ids and layer_starts == sorted(layer_starts),
        "warmth_melts_before_scene_2_layers": layer_ids[0] == "warm_center_melt" and layer_starts[0] < layer_starts[1],
        "air_horizon_before_terrain": layer_starts[1] < layer_starts[2],
        "lower_left_mass_arrives_after_terrain": layer_starts[3] > layer_starts[2],
        "information_membranes_arrive_last": layer_ids[-1] == "information_membranes" and layer_starts[-1] == max(layer_starts),
        "scene_2_semantics_begin_after_scene_1": min(layer_starts[1:]) >= 10.0,
        "uniform_full_screen_blend_reduced": (
            transition["revised_simultaneous_full_frame_switch_contribution"]
            < transition["baseline_simultaneous_full_frame_switch_contribution"]
            and not transition["uniform_full_screen_crossfade"]
        ),
        "rendered_transition_sample_fingerprints_locked": (
            rendered_transition_frame_hashes == EXPECTED_TRANSITION_FRAME_HASHES
        ),
        "implementation_envelopes_match_design": implementation_envelopes == expected_implementation_envelopes,
        "implementation_composite_order_matches_design": (
            [implementation_source.index(token) for token in composite_order]
            == sorted(implementation_source.index(token) for token in composite_order)
        ),
        "implementation_uses_spatial_masks_not_xfade": (
            "geq=r='r(X,Y)'" in implementation_source
            and "xfade=" not in implementation_source
            and "[finalconverge]" not in implementation_source
        ),
        "implementation_renders_full_1_1_second_connection": all(
            token in implementation_source
            for token in (
                "trim=start=0:end=0.9",
                "trim=start=0.9:end=1.1",
                "trim=start=0:end=1.1",
            )
        ),
        "scene_2_entry_seam_matches_reference": (
            review_frame_332_to_scene2_32_ssim is not None
            and review_frame_333_to_scene2_33_ssim is not None
            and review_frame_332_to_scene2_32_ssim >= 0.99
            and review_frame_333_to_scene2_33_ssim >= 0.99
        ),
        "review_duration_23_seconds": abs(float(review_probe["format"]["duration"]) - 23.0) <= 0.01,
        "review_frame_count_690": review_stream.get("nb_read_frames") == "690",
        "review_30fps": review_stream.get("r_frame_rate") == "30/1",
        "review_h264_yuv420p": review_stream.get("codec_name") == "h264" and review_stream.get("pix_fmt") == "yuv420p",
    }
    evidence = {
        "schema_version": 1,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "reference_implementation": {
            "pr": 191,
            "commit": "23cc8f2446f77895f926e7e19264f49dfc9012dd",
            "scene_2_master_sha256": scene2_sha,
            "expected_scene_2_master_sha256": EXPECTED_SCENE2_SHA,
            "read_only": True
        },
        "immutable_scene_1": {
            "master_sha256": scene1_sha,
            "expected_master_sha256": EXPECTED_SCENE1_SHA,
            "iphone_sha256": iphone_sha,
            "expected_iphone_sha256": EXPECTED_IPHONE_SHA
        },
        "revision_baseline": {
            "sha256": baseline_sha,
            "expected_sha256": EXPECTED_BASELINE_SHA,
            "workflow_run_id": 31077899888,
            "artifact_id": 8958248421
        },
        "scene_1_terminal": {
            "captured_at_seconds": 9.95,
            "sha256": terminal_sha,
            "pr191_reference_sha256": terminal_reference_sha,
            "expected_sha256": EXPECTED_TERMINAL_SHA
        },
        "review_clip": {
            "path": args.review.resolve().relative_to(args.output.parent.resolve()).as_posix(),
            "sha256": sha256(args.review),
            "duration": float(review_probe["format"]["duration"]),
            "decoded_frame_count": int(review_stream.get("nb_read_frames", 0)),
            "scene_1_frames": 300,
            "scene_2_frames": 390,
            "boundary_frame": 300,
            "entry_transition_seconds": 1.1,
            "raw_boundary_ssim_observation": boundary_ssim(args.scene1, args.scene2),
            "scene_1_segment_ssim": scene1_ssim,
            "scene_1_terminal_hold_ssim": hold_ssim,
            "scene_2_after_transition_ssim": scene2_tail_ssim
        },
        "layer_envelopes": envelopes,
        "rendered_transition_verification": {
            "method": "decoded framemd5 fingerprints at six ordered transition samples",
            "frame_indices": list(EXPECTED_TRANSITION_FRAME_HASHES),
            "actual_framemd5": rendered_transition_frame_hashes,
            "expected_framemd5": EXPECTED_TRANSITION_FRAME_HASHES,
            "implementation_sha256": sha256(args.implementation),
            "implementation_envelopes_actual": implementation_envelopes,
            "implementation_envelopes_expected_from_design": expected_implementation_envelopes,
            "implementation_composite_order": composite_order,
            "review_frame_332_to_scene_2_frame_32_ssim": review_frame_332_to_scene2_32_ssim,
            "review_frame_333_to_scene_2_frame_33_ssim": review_frame_333_to_scene2_33_ssim,
        },
        "checks": checks,
    }
    args.output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    return 0 if evidence["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
