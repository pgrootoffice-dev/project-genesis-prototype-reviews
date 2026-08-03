#!/usr/bin/env python3
"""Fail-closed evidence for Section 0 Motion C."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from render_section0_c import SECTION0_LOCKED_LINE_PATH


EXPECTED = [
    ("output/master/section-0-traveling-light-motion.mp4", 5.4, 720, 1280),
    ("output/master/section-0-abc-comparison.mp4", 5.4, 2160, 1280),
    ("output/master/section-0-abc-sequence.mp4", 16.2, 720, 1280),
    ("output/iphone/section-0-traveling-light-motion-iphone.mp4", 5.4, 540, 960),
    ("output/iphone/section-0-abc-comparison-iphone.mp4", 5.4, 810, 480),
    ("output/iphone/section-0-abc-sequence-iphone.mp4", 16.2, 540, 960),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def locked_hashes(root: Path) -> dict[str, str]:
    result = {}
    # The base lock includes all three Working Lock JPEGs. The layered lock
    # adds A/B, Section 4, Final, and their evidence. C must refuse to render
    # if either the source bytes or any existing motion bytes have changed.
    for checksum_file in ("checksums.sha256", "layered-semantic-checksums.sha256"):
        for line in (root / checksum_file).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            expected, relative = line.split("  ", 1)
            previous = result.get(relative)
            if previous is not None and previous != expected:
                raise ValueError(f"conflicting byte locks for {relative}")
            result[relative] = expected
    return result


def verify_lock(root: Path) -> list[str]:
    failures = []
    for relative, expected in locked_hashes(root).items():
        path = root / relative
        actual = sha256(path) if path.is_file() else None
        if actual != expected:
            failures.append(f"existing byte lock mismatch: {relative}: {actual} != {expected}")
    return failures


def probe(path: Path) -> dict:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        check=True, stdout=subprocess.PIPE, text=True,
    )
    return json.loads(result.stdout)


SAMPLE_WIDTH = 180
SAMPLE_HEIGHT = 320


def sample_frame(video: Path, timestamp: float) -> bytes:
    return subprocess.run(
        [
            "ffmpeg", "-v", "error", "-i", str(video), "-ss", f"{timestamp:.3f}",
            "-frames:v", "1", "-vf", f"scale={SAMPLE_WIDTH}:{SAMPLE_HEIGHT}",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
        ],
        check=True, stdout=subprocess.PIPE,
    ).stdout


def difference(left: bytes, right: bytes) -> float:
    return sum(abs(a - b) for a, b in zip(left, right)) / len(left)


def max_change(video: Path, source: Path) -> tuple[float, float]:
    source_frame = sample_frame(source, 0.0)
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(video),
         "-vf", f"scale={SAMPLE_WIDTH}:{SAMPLE_HEIGHT},fps=30",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        check=True, stdout=subprocess.PIPE,
    ).stdout
    size = SAMPLE_WIDTH * SAMPLE_HEIGHT * 3
    best_index, best_score = 0, -1.0
    for index in range(len(raw) // size):
        score = difference(raw[index * size:(index + 1) * size], source_frame)
        if score > best_score:
            best_index, best_score = index, score
    return best_index / 30, round(best_score, 4)


def extract_frame(video: Path, timestamp: float, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-ss", f"{timestamp:.3f}", "-i", str(video), "-frames:v", "1", "-q:v", "2", str(destination)],
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--lock-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    failures = verify_lock(root)
    if args.lock_only:
        if failures:
            raise SystemExit("\n".join(failures))
        print("EXISTING_A_B_SECTION4_FINAL_LOCK_PASS")
        return

    reports = []
    for relative, expected_duration, expected_width, expected_height in EXPECTED:
        path = root / relative
        if not path.is_file() or path.stat().st_size == 0:
            failures.append(f"missing or empty: {relative}")
            continue
        data = probe(path)
        video = [stream for stream in data["streams"] if stream["codec_type"] == "video"]
        audio = [stream for stream in data["streams"] if stream["codec_type"] == "audio"]
        duration = float(data["format"]["duration"])
        stream = video[0] if video else {}
        reports.append({
            "path": relative, "sha256": sha256(path), "bytes": path.stat().st_size,
            "duration": duration, "width": stream.get("width"), "height": stream.get("height"),
            "codec": stream.get("codec_name"), "pixel_format": stream.get("pix_fmt"),
            "fps": stream.get("r_frame_rate"), "audio_streams": len(audio),
        })
        if abs(duration - expected_duration) > 0.08:
            failures.append(f"{relative}: duration {duration} != {expected_duration}")
        if len(video) != 1 or audio:
            failures.append(f"{relative}: expected one silent video stream")
        if (stream.get("width"), stream.get("height")) != (expected_width, expected_height):
            failures.append(f"{relative}: unexpected dimensions")
        if (stream.get("codec_name"), stream.get("pix_fmt"), stream.get("r_frame_rate")) != ("h264", "yuv420p", "30/1"):
            failures.append(f"{relative}: expected H.264/yuv420p/30fps")

    master_c = root / "output/master/section-0-traveling-light-motion.mp4"
    hold_difference = round(difference(sample_frame(master_c, 4.333), sample_frame(master_c, 5.333)), 6)
    if hold_difference > 0.08:
        failures.append(f"C hold is not still: mean difference {hold_difference}")

    max_time, max_score = max_change(master_c, root / "assets/source/section-0-working-lock.jpg")
    max_frame = root / "assets/review/section-0-c-max-change.jpg"
    extract_frame(master_c, max_time, max_frame)

    evidence = {
        "status": "PASS" if not failures else "FAIL",
        "scope": "Section 0 Motion C — Working Test / NON-CANONICAL",
        "design_source": {
            "pr": 186,
            "commit": "6cfde74041e7a64e791bac31b15d61db772521cc",
            "file": "docs/farlens/brand-film/SECTION_00_MOTION_C_DESIGN_REVIEW.md",
        },
        "existing_a_b_section4_final_lock": {
            "status": "PASS" if not verify_lock(root) else "FAIL",
            "sha256": locked_hashes(root),
        },
        "motion_contract": {
            "meaning_verb": "届く",
            "hero": "Traveling Light on the locked orange line",
            "semantic_order": ["覚醒", "移動", "到達・定着"],
            "hold": {"start": 4.30, "end": 5.40, "duration": 1.10, "mean_frame_difference": hold_difference},
            "path_coordinate_count": len(SECTION0_LOCKED_LINE_PATH),
            "path_coordinates": SECTION0_LOCKED_LINE_PATH,
            "camera": "fixed",
        },
        "deterministic_2d_method": {
            "source_base": "complete locked JPEG on every frame",
            "allowed_operations": ["source-region duplicate", "source-traced path follow", "additive trail", "local RGB light change"],
            "new_stars_or_particles": False,
            "background_reconstruction": False,
            "generative_services": [],
            "external_uploads": [],
        },
        "technical_checks": reports,
        "maximum_change_frame": {
            "timestamp": round(max_time, 3), "mean_absolute_difference": max_score,
            "file": str(max_frame.relative_to(root)),
        },
        "failures": failures,
    }
    evidence_path = root / "section-0-c-technical-evidence.json"
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checksum_paths = [root / relative for relative, *_rest in EXPECTED] + [max_frame, evidence_path]
    (root / "section-0-c-checksums.sha256").write_text(
        "\n".join(f"{sha256(path)}  {path.relative_to(root)}" for path in checksum_paths) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
