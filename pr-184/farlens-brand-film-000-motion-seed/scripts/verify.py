#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

EXPECTED = [
    ("output/master/section-0-motion-test.mp4", 5.4, 720, 1280),
    ("output/master/section-4-motion-test.mp4", 5.6, 720, 1280),
    ("output/master/final-motion-test.mp4", 5.4, 720, 1280),
    ("output/master/motion-seed-sequence.mp4", 16.4, 720, 1280),
    ("output/iphone/section-0-motion-test-iphone.mp4", 5.4, 540, 960),
    ("output/iphone/section-4-motion-test-iphone.mp4", 5.6, 540, 960),
    ("output/iphone/final-motion-test-iphone.mp4", 5.4, 540, 960),
    ("output/iphone/motion-seed-sequence-iphone.mp4", 16.4, 540, 960),
]


def probe(path: Path) -> dict:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return json.loads(result.stdout)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    reports = []
    failures = []

    for relative_path, expected_duration, expected_width, expected_height in EXPECTED:
        path = root / relative_path
        name = path.name
        data = probe(path)
        video = [stream for stream in data["streams"] if stream["codec_type"] == "video"]
        audio = [stream for stream in data["streams"] if stream["codec_type"] == "audio"]
        duration = float(data["format"]["duration"])
        entry = {
            "path": str(path.relative_to(root)),
            "sha256": sha256(path),
            "duration": duration,
            "video_streams": len(video),
            "audio_streams": len(audio),
            "codec": video[0].get("codec_name") if video else None,
            "width": video[0].get("width") if video else None,
            "height": video[0].get("height") if video else None,
            "fps": video[0].get("r_frame_rate") if video else None,
            "pixel_format": video[0].get("pix_fmt") if video else None,
        }
        reports.append(entry)
        if abs(duration - expected_duration) > 0.08:
            failures.append(f"{name}: duration {duration} != {expected_duration}")
        if len(video) != 1 or audio:
            failures.append(f"{name}: expected one video stream and no audio")
        if not video or (video[0].get("width"), video[0].get("height")) != (expected_width, expected_height):
            failures.append(f"{name}: dimensions are not {expected_width}x{expected_height}")
        if video and (video[0].get("codec_name"), video[0].get("pix_fmt"), video[0].get("r_frame_rate")) != ("h264", "yuv420p", "30/1"):
            failures.append(f"{name}: expected H.264/yuv420p/30fps")

    source_hashes = {
        path.name: sha256(path) for path in sorted((root / "assets" / "source").glob("*.jpg"))
    }
    evidence = {
        "status": "PASS" if not failures else "FAIL",
        "source_lock": {
            "method": (
                "locked JPEG decoded as the full-frame base; deterministic additive highlights are used in all scenes; "
                "Final also applies a temporary source-luminance-selected attenuation only to the existing wordmark "
                "and point, with the locked source appearance fully restored before the final 2-second hold"
            ),
            "source_hashes": source_hashes,
            "generative_services": [],
            "external_uploads": [],
            "source_resolution": "720x1280 (9:16)",
        },
        "technical_checks": reports,
        "failures": failures,
    }
    (root / "technical-evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
