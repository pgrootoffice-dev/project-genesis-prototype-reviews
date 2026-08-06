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
            "-filter_complex", "[0:v]select='eq(n,0)'[a];[1:v]select='eq(n,0)'[b];[a][b]ssim",
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene1", required=True, type=Path)
    parser.add_argument("--scene2", required=True, type=Path)
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--terminal", required=True, type=Path)
    parser.add_argument("--terminal-reference", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    review_hashes = frame_hashes(args.review)
    scene2_sha = sha256(args.scene2)
    terminal_sha = sha256(args.terminal)
    terminal_reference_sha = sha256(args.terminal_reference)
    review_probe = probe(args.review)
    review_stream = next(item for item in review_probe["streams"] if item.get("codec_type") == "video")

    scene1_ssim = sequence_ssim(args.scene1, args.review, 0.0, 0.0, 10.0)
    scene2_tail_ssim = sequence_ssim(args.scene2, args.review, 0.7, 10.7, 12.3)

    checks = {
        "scene_1_segment_faithful": scene1_ssim is not None and scene1_ssim >= 0.99,
        "scene_2_after_transition_faithful": scene2_tail_ssim is not None and scene2_tail_ssim >= 0.99,
        "scene_2_reference_sha_unchanged": scene2_sha == EXPECTED_SCENE2_SHA,
        "scene_1_terminal_matches_pr191_reference": terminal_sha == terminal_reference_sha == EXPECTED_TERMINAL_SHA,
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
            "entry_transition_seconds": 0.7,
            "raw_boundary_ssim_observation": boundary_ssim(args.scene1, args.scene2),
            "scene_1_segment_ssim": scene1_ssim,
            "scene_2_after_transition_ssim": scene2_tail_ssim
        },
        "checks": checks,
    }
    args.output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    return 0 if evidence["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
