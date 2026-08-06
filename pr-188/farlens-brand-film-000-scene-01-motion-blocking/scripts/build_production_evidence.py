#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

EXPECTED_SHA256 = {
    "master": "f684be2ebcb176f043f419bdfed297bbeb1e4eb7ef68dae98cfbc462197d1b79",
    "iphone": "2c7dce60db133313a5853ff66b77243879900e188e09d7735aee1ba3b34ef5a5",
    "review": "d28e70f5d87e2eef394bc4910990e9b6dd37003edf6685924114fff3c59edbfa",
    "scene2": "3e51b0fbf461d7cfc49c91c05420777f2da1bc843b476a65127483fb50a76904",
    "baseline": "d9d5eec5fc14a80f45f3c22de57c3d3b3dc8579e8f33f8749aab0731349534dc",
}
VIDEO_SPECS = {
    "master": (1280, 720, 10.0, "300"),
    "iphone": (960, 540, 10.0, "300"),
    "review": (1280, 720, 23.0, "690"),
    "scene2": (1280, 720, 13.0, "390"),
    "baseline": (1280, 720, 23.0, "690"),
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
            "format=duration,size,bit_rate:stream=index,codec_name,codec_type,width,height,r_frame_rate,pix_fmt,nb_read_frames",
            "-of", "json", str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("master", "iphone", "review", "scene2", "baseline", "envelopes", "output"):
        parser.add_argument(f"--{name}", required=True, type=Path)
    args = parser.parse_args()

    videos = {}
    checks = {}
    for label in ("master", "iphone", "review", "scene2", "baseline"):
        path = getattr(args, label)
        metadata = probe(path)
        stream = next(item for item in metadata["streams"] if item.get("codec_type") == "video")
        expected_width, expected_height, expected_duration, expected_frames = VIDEO_SPECS[label]
        actual_sha = sha256(path)
        checks[f"{label}_sha256_locked"] = actual_sha == EXPECTED_SHA256[label]
        checks[f"{label}_video_spec_valid"] = (
            stream.get("codec_name") == "h264"
            and stream.get("pix_fmt") == "yuv420p"
            and stream.get("r_frame_rate") == "30/1"
            and stream.get("width") == expected_width
            and stream.get("height") == expected_height
            and stream.get("nb_read_frames") == expected_frames
            and abs(float(metadata["format"]["duration"]) - expected_duration) <= 0.01
        )
        videos[label] = {
            "path": path.name,
            "sha256": actual_sha,
            "expected_sha256": EXPECTED_SHA256[label],
            "probe": metadata,
        }

    envelopes = json.loads(args.envelopes.read_text(encoding="utf-8"))
    evidence = {
        "schema_version": 1,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "scope": "Review-only Scene 1 to Scene 2 layered connection",
        "formal_masters_modified": not (
            checks["master_sha256_locked"] and checks["scene2_sha256_locked"]
        ),
        "transition": envelopes["transition"],
        "layer_order": [item["id"] for item in sorted(envelopes["layers"], key=lambda item: item["order"])],
        "videos": videos,
        "checks": checks,
    }
    args.output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if evidence["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
