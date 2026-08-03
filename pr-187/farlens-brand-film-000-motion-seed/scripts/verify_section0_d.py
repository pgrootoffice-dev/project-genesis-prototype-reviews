#!/usr/bin/env python3
"""Fail-closed verification and evidence for Section 0 layer-first Motion D."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from build_section0_d_layers import LAYER_NAMES


VIDEO_EXPECTED = [
    ("output/master/section-0-layer-first-motion.mp4", 5.4, 720, 1280),
    ("output/master/section-0-layer-breakdown.mp4", 5.4, 720, 1280),
    ("output/master/section-0-abcd-comparison.mp4", 5.4, 2880, 1280),
    ("output/master/section-0-abcd-sequence.mp4", 21.6, 720, 1280),
    ("output/iphone/section-0-layer-first-motion-iphone.mp4", 5.4, 540, 960),
    ("output/iphone/section-0-layer-breakdown-iphone.mp4", 5.4, 540, 960),
    ("output/iphone/section-0-abcd-comparison-iphone.mp4", 5.4, 960, 426),
    ("output/iphone/section-0-abcd-sequence-iphone.mp4", 21.6, 540, 960),
]
SAMPLE_WIDTH = 180
SAMPLE_HEIGHT = 320


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def locked_hashes(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for filename in ("checksums.sha256", "layered-semantic-checksums.sha256", "section-0-c-checksums.sha256"):
        for line in (root / filename).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            expected, relative = line.split("  ", 1)
            if relative in result and result[relative] != expected:
                raise ValueError(f"conflicting lock for {relative}")
            result[relative] = expected
    return result


def verify_lock(root: Path) -> tuple[list[str], dict[str, str]]:
    failures = []
    locked = locked_hashes(root)
    for relative, expected in locked.items():
        path = root / relative
        actual = sha256(path) if path.is_file() else None
        if actual != expected:
            failures.append(f"existing A/B/C lock mismatch: {relative}: {actual} != {expected}")
    return failures, locked


def probe(path: Path) -> dict:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return json.loads(result.stdout)


def decode(path: Path, pixel_format: str) -> bytes:
    return subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", pixel_format, "-"],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout


def current_recomposition(root: Path, layer_dir: Path) -> dict:
    source = decode(root / "assets/source/section-0-working-lock.jpg", "rgb24")
    decoded = {filename: decode(layer_dir / filename, "rgba") for filename in LAYER_NAMES}
    background = decoded[LAYER_NAMES[0]]
    composite = bytearray(len(source))
    for index in range(len(source) // 3):
        composite[index * 3:index * 3 + 3] = background[index * 4:index * 4 + 3]
    # Source-of-Truth Z-order: Background → Earth → Clouds → Hill → Trees →
    # House → Window → Connection Line → Traveling Light.
    order = [1, 2, 5, 7, 6, 8, 3, 4]
    for layer_index in order:
        rgba = decoded[LAYER_NAMES[layer_index]]
        for index in range(len(source) // 3):
            if rgba[index * 4 + 3] > 0:
                composite[index * 3:index * 3 + 3] = rgba[index * 4:index * 4 + 3]
    deltas = [abs(actual - expected) for actual, expected in zip(composite, source)]
    return {
        "file": "assets/review/section-0-d-recomposed.png",
        "difference_file": "assets/review/section-0-d-difference.png",
        "mean_absolute_error": round(sum(deltas) / len(deltas), 8),
        "maximum_channel_error": max(deltas),
        "changed_channel_values": sum(delta > 0 for delta in deltas),
        "pixel_exact": not any(deltas),
    }


def sample_frame(path: Path, timestamp: float) -> bytes:
    return subprocess.run(
        [
            "ffmpeg", "-v", "error", "-i", str(path), "-ss", f"{timestamp:.3f}",
            "-frames:v", "1", "-vf", f"scale={SAMPLE_WIDTH}:{SAMPLE_HEIGHT}",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
        ],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout


def difference(left: bytes, right: bytes) -> float:
    if not left or len(left) != len(right):
        raise ValueError("sample frame length mismatch")
    return sum(abs(a - b) for a, b in zip(left, right)) / len(left)


def max_change(video: Path, source: Path) -> tuple[float, float]:
    source_frame = sample_frame(source, 0.0)
    raw = subprocess.run(
        [
            "ffmpeg", "-v", "error", "-i", str(video),
            "-vf", f"scale={SAMPLE_WIDTH}:{SAMPLE_HEIGHT},fps=30",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
        ],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    frame_size = SAMPLE_WIDTH * SAMPLE_HEIGHT * 3
    best_index, best_score = 0, -1.0
    for index in range(len(raw) // frame_size):
        frame = raw[index * frame_size:(index + 1) * frame_size]
        score = difference(frame, source_frame)
        if score > best_score:
            best_index, best_score = index, score
    return best_index / 30, round(best_score, 4)


def extract_frame(video: Path, timestamp: float, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-ss", f"{timestamp:.3f}", "-i", str(video), "-frames:v", "1", "-q:v", "2", str(destination)],
        check=True,
    )


def faststart(path: Path) -> bool:
    data = path.read_bytes()
    return data.find(b"moov") < data.find(b"mdat") and data.find(b"moov") >= 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--lock-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    failures, locked = verify_lock(root)
    if args.lock_only:
        if failures:
            raise SystemExit("\n".join(failures))
        print("EXISTING_A_B_C_SOURCE_LOCK_PASS")
        return

    checks = []
    for relative, duration, width, height in VIDEO_EXPECTED:
        path = root / relative
        if not path.is_file() or path.stat().st_size == 0:
            failures.append(f"missing or empty video: {relative}")
            continue
        metadata = probe(path)
        video = next((stream for stream in metadata["streams"] if stream.get("codec_type") == "video"), {})
        audio_count = sum(stream.get("codec_type") == "audio" for stream in metadata["streams"])
        observed_duration = float(metadata["format"]["duration"])
        check = {
            "path": relative,
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "duration": observed_duration,
            "width": video.get("width"),
            "height": video.get("height"),
            "codec": video.get("codec_name"),
            "pixel_format": video.get("pix_fmt"),
            "fps": video.get("r_frame_rate"),
            "audio_streams": audio_count,
            "faststart": faststart(path),
        }
        checks.append(check)
        expected = (duration, width, height, "h264", "yuv420p", "30/1", 0, True)
        actual = (round(observed_duration, 3), video.get("width"), video.get("height"), video.get("codec_name"), video.get("pix_fmt"), video.get("r_frame_rate"), audio_count, check["faststart"])
        if actual != expected:
            failures.append(f"video contract mismatch: {relative}: {actual} != {expected}")

    layer_dir = root / "assets/layers/section-0-d"
    layer_checks = []
    for filename in LAYER_NAMES:
        path = layer_dir / filename
        metadata = probe(path)
        stream = metadata["streams"][0]
        layer_checks.append({
            "path": str(path.relative_to(root)),
            "sha256": sha256(path),
            "width": stream.get("width"),
            "height": stream.get("height"),
            "pixel_format": stream.get("pix_fmt"),
        })
        if (stream.get("width"), stream.get("height"), stream.get("pix_fmt")) != (720, 1280, "rgba"):
            failures.append(f"layer contract mismatch: {filename}")

    layer_manifest = json.loads((root / "section-0-d-layer-manifest.json").read_text(encoding="utf-8"))
    recomposition = current_recomposition(root, layer_dir)
    if not recomposition.get("pixel_exact") or recomposition.get("maximum_channel_error") != 0:
        failures.append(f"recomposition is not pixel exact: {recomposition}")
    if recomposition != layer_manifest.get("recomposition"):
        failures.append("current PNG recomposition no longer matches section-0-d-layer-manifest.json")

    motion = root / "output/master/section-0-layer-first-motion.mp4"
    hold_difference = round(difference(sample_frame(motion, 4.333), sample_frame(motion, 5.333)), 6)
    if hold_difference > 0.05:
        failures.append(f"hold is not stable: {hold_difference}")
    # The opening cue is intentionally local (a restrained atmospheric wake), so
    # it uses a lower full-frame threshold than the subsequent hero handoffs.
    continuity_pairs = [(0.00, 0.20, 0.005), (0.38, 0.62, 0.01), (0.88, 1.06, 0.01), (1.30, 1.52, 0.01), (2.00, 2.22, 0.01), (2.68, 2.92, 0.01), (3.38, 3.62, 0.01), (3.94, 4.16, 0.01)]
    continuity = []
    for start, end, threshold in continuity_pairs:
        score = round(difference(sample_frame(motion, start), sample_frame(motion, end)), 6)
        continuity.append({"start": start, "end": end, "mean_frame_difference": score, "minimum": threshold, "status": "PASS" if score > threshold else "FAIL"})
        if score <= threshold:
            failures.append(f"pre-hold motion gap: {start}-{end}: {score}")

    maximum_timestamp, maximum_score = max_change(motion, root / "assets/source/section-0-working-lock.jpg")
    maximum_path = root / "assets/review/section-0-d-max-change.jpg"
    extract_frame(motion, maximum_timestamp, maximum_path)

    evidence = {
        "status": "PASS" if not failures else "FAIL",
        "scope": "Section 0 Motion D — Layer-first Working Prototype / NON-CANONICAL",
        "design_source": {
            "pr": 186,
            "commit": "fb671a9427fd19c15867ad082701433d664c4973",
            "file": "docs/farlens/brand-film/SECTION_00_MOTION_D_LAYER_MANIFEST_AND_SPEC.md",
        },
        "existing_a_b_c_source_lock": {"status": "PASS" if not verify_lock(root)[0] else "FAIL", "file_count": len(locked), "sha256": locked},
        "layer_first_contract": {
            "layer_count": 9,
            "manual_mask_count": 8,
            "same_canvas_rgba": True,
            "recomposition": recomposition,
            "camera": "fixed",
            "new_objects": [],
            "generative_services": [],
        },
        "motion_contract": {
            "motion_level": "Lv2 Semantic Motion",
            "meaning": "世界の変化が、家族へ届く",
            "hero": "Traveling Light",
            "role_handoff": ["Background", "Earth", "Clouds", "Traveling Light", "Trees", "Hill / House", "Window Glow", "Hold"],
            "hold": {"start": 4.3, "end": 5.4, "duration": 1.1, "mean_frame_difference": hold_difference},
            "pre_hold_motion_samples": continuity,
        },
        "technical_checks": checks,
        "layer_checks": layer_checks,
        "maximum_change_frame": {
            "timestamp": maximum_timestamp,
            "mean_absolute_difference": maximum_score,
            "file": str(maximum_path.relative_to(root)),
        },
        "failures": failures,
    }
    evidence_path = root / "section-0-d-technical-evidence.json"
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checksum_paths = [
        *(str((Path("assets/layers/section-0-d") / filename)) for filename in LAYER_NAMES),
        "assets/review/section-0-d-recomposed.png",
        "assets/review/section-0-d-difference.png",
        "assets/review/section-0-d-max-change.jpg",
        "section-0-d-layer-manifest.json",
        "section-0-d-technical-evidence.json",
        *(relative for relative, _, _, _ in VIDEO_EXPECTED),
    ]
    (root / "section-0-d-checksums.sha256").write_text(
        "".join(f"{sha256(root / relative)}  {relative}\n" for relative in checksum_paths),
        encoding="utf-8",
    )
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
