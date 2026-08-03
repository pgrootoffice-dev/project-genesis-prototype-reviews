#!/usr/bin/env python3
"""Fail-closed checks for the Layered Semantic Motion A/B test."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


A_LOCK = {
    "output/master/final-motion-test.mp4": "3179f19d8ba4b97080bce988232e34d96eae355771720ab32f7500662eb2b528",
    "output/master/motion-seed-sequence.mp4": "bdc4769b5b7e36c133544ccd79ebcead78888a7a6f0dee7b2b705b336e3bc144",
    "output/master/section-0-motion-test.mp4": "b71bee84e39db5f843c9dfee75915687d63acbdb55eccee4f4dd4deae600a9e0",
    "output/master/section-4-motion-test.mp4": "5706e61d0d3be50b35f722c9ef1d9f27bdfb81991853d1b3d407e112f81ac474",
    "output/iphone/final-motion-test-iphone.mp4": "352f83a5a1249839e927e02a9bc8b9ae10c577193df69c14915f9a5a9db36d15",
    "output/iphone/motion-seed-sequence-iphone.mp4": "6b3710a7d7288084a42542cbaed8b6bb3e38d8b1e2df61ca3408345e55b54c48",
    "output/iphone/section-0-motion-test-iphone.mp4": "92033f5182daa93888955c3ec4af493c30e05f2bec4a21df2855804c5e3cbbe3",
    "output/iphone/section-4-motion-test-iphone.mp4": "be2309f13efea423cd3fe2eec7d82a195654c9b5640c66c6ee4bab74f4f0b1aa",
}

EXPECTED = [
    ("output/master/section-0-layered-semantic-motion.mp4", 5.4, 720, 1280),
    ("output/master/section-4-layered-semantic-motion.mp4", 5.6, 720, 1280),
    ("output/master/section-0-ab-comparison.mp4", 5.4, 1440, 1280),
    ("output/master/section-4-ab-comparison.mp4", 5.6, 1440, 1280),
    ("output/master/layered-semantic-ab-sequence.mp4", 11.0, 1440, 1280),
    ("output/iphone/section-0-layered-semantic-motion-iphone.mp4", 5.4, 540, 960),
    ("output/iphone/section-4-layered-semantic-motion-iphone.mp4", 5.6, 540, 960),
    ("output/iphone/section-0-ab-comparison-iphone.mp4", 5.4, 720, 640),
    ("output/iphone/section-4-ab-comparison-iphone.mp4", 5.6, 720, 640),
    ("output/iphone/layered-semantic-ab-sequence-iphone.mp4", 11.0, 720, 640),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def probe(path: Path) -> dict:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return json.loads(result.stdout)


def extract_frame(video: Path, timestamp: float, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-v", "error", "-y", "-ss", f"{timestamp:.3f}", "-i", str(video),
            "-frames:v", "1", "-q:v", "2", str(destination),
        ],
        check=True,
    )


def max_change(video: Path, source: Path) -> tuple[float, float]:
    source_result = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(source), "-frames:v", "1", "-vf", "scale=90:160", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        check=True,
        stdout=subprocess.PIPE,
    )
    result = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(video), "-vf", "scale=90:160,fps=30", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        check=True,
        stdout=subprocess.PIPE,
    )
    frame_size = 90 * 160
    source_bytes = source_result.stdout
    best_index, best_score = 0, -1.0
    for index in range(len(result.stdout) // frame_size):
        frame = result.stdout[index * frame_size:(index + 1) * frame_size]
        score = sum(abs(left - right) for left, right in zip(frame, source_bytes)) / frame_size
        if score > best_score:
            best_index, best_score = index, score
    return best_index / 30, round(best_score, 4)


def verify_a_lock(root: Path) -> list[str]:
    failures = []
    for relative, expected in A_LOCK.items():
        path = root / relative
        actual = sha256(path) if path.is_file() else None
        if actual != expected:
            failures.append(f"A/Final lock mismatch: {relative}: {actual} != {expected}")
    return failures


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--a-lock-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    failures = verify_a_lock(root)
    if args.a_lock_only:
        if failures:
            raise SystemExit("\n".join(failures))
        print("A_LOCK_PASS")
        return

    reports = []
    for relative, expected_duration, expected_width, expected_height in EXPECTED:
        path = root / relative
        if not path.is_file() or path.stat().st_size == 0:
            failures.append(f"missing or empty: {relative}")
            continue
        data = probe(path)
        videos = [stream for stream in data["streams"] if stream["codec_type"] == "video"]
        audios = [stream for stream in data["streams"] if stream["codec_type"] == "audio"]
        duration = float(data["format"]["duration"])
        stream = videos[0] if videos else {}
        report = {
            "path": relative,
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "duration": duration,
            "width": stream.get("width"),
            "height": stream.get("height"),
            "codec": stream.get("codec_name"),
            "pixel_format": stream.get("pix_fmt"),
            "fps": stream.get("r_frame_rate"),
            "audio_streams": len(audios),
        }
        reports.append(report)
        if abs(duration - expected_duration) > 0.08:
            failures.append(f"{relative}: duration {duration} != {expected_duration}")
        if len(videos) != 1 or audios:
            failures.append(f"{relative}: expected one silent video stream")
        if (stream.get("width"), stream.get("height")) != (expected_width, expected_height):
            failures.append(f"{relative}: unexpected dimensions")
        if (stream.get("codec_name"), stream.get("pix_fmt"), stream.get("r_frame_rate")) != ("h264", "yuv420p", "30/1"):
            failures.append(f"{relative}: expected H.264/yuv420p/30fps")

    max_frames = []
    for section in (0, 4):
        video = root / f"output/master/section-{section}-layered-semantic-motion.mp4"
        source = root / f"assets/source/section-{section}-working-lock.jpg"
        timestamp, score = max_change(video, source)
        destination = root / f"assets/review/section-{section}-b-max-change.jpg"
        extract_frame(video, timestamp, destination)
        max_frames.append({
            "section": section,
            "timestamp": round(timestamp, 3),
            "mean_absolute_difference": score,
            "file": str(destination.relative_to(root)),
        })

    evidence = {
        "status": "PASS" if not failures else "FAIL",
        "scope": "Section 0 and Section 4 Layered Semantic Motion A/B working test",
        "a_and_final_lock": {"status": "PASS" if not verify_a_lock(root) else "FAIL", "sha256": A_LOCK},
        "deterministic_2d_method": {
            "source_base": "complete locked JPEG on every frame",
            "allowed_operations": ["soft source-region duplicate", "existing-path response", "local RGB light change"],
            "background_reconstruction": False,
            "generative_services": [],
            "external_uploads": [],
        },
        "technical_checks": reports,
        "maximum_change_frames": max_frames,
        "failures": failures,
    }
    (root / "layered-semantic-technical-evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    checksum_paths = [root / relative for relative in A_LOCK]
    checksum_paths.extend(root / relative for relative, *_rest in EXPECTED)
    checksum_paths.extend(root / item["file"] for item in max_frames)
    checksum_lines = [f"{sha256(path)}  {path.relative_to(root)}" for path in checksum_paths]
    (root / "layered-semantic-checksums.sha256").write_text(
        "\n".join(checksum_lines) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
