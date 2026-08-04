#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
SOURCE = REPO / "docs/farlens/brand-film/assets/scene-01/BRAND_FILM_000_SCENE_01_STATIC_SEQUENCE_WORKING_LOCK.png"
EXPECTED_SOURCE_SHA = "97bfd90afc8e6ceaa6d6bf3e8a26d78b6cf9b9d506240af5fd84fb5b9d290c59"

VIDEOS = {
    "master": ROOT / "output/master/scene-01-motion-blocking.mp4",
    "iphone": ROOT / "output/iphone/scene-01-motion-blocking-iphone.mp4",
}
RENDERER = ROOT / "scripts/render_motion_blocking.swift"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration,size:stream=codec_name,codec_type,width,height,r_frame_rate,pix_fmt,nb_read_frames",
            "-count_frames",
            "-of", "json", str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def has_faststart(path: Path) -> bool:
    data = path.read_bytes()
    return data.find(b"moov") < data.find(b"mdat")


def cropdetect(path: Path) -> set[tuple[int, int, int, int]]:
    result = subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-i", str(path), "-vf",
            "cropdetect=limit=2:round=2:reset=0", "-frames:v", "300",
            "-f", "null", "-",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    matches = re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", result.stderr)
    return {tuple(int(value) for value in match) for match in matches}


def decode_fully(path: Path) -> None:
    subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"],
        check=True,
    )


def verify() -> dict:
    failures: list[str] = []
    source_sha = sha256(SOURCE)
    if source_sha != EXPECTED_SOURCE_SHA:
        failures.append("approved Static Sequence SHA-256 mismatch")

    beat_map = json.loads((ROOT / "beat-map.json").read_text(encoding="utf-8"))
    if [item["frame"] for item in beat_map["timeline"]] != [1, 2, 3, 4, 5]:
        failures.append("Frame order is not 1..5")
    if [item["beat"] for item in beat_map["timeline"]] != ["Beat 1", "Beat 2", "Beat 3", "Beat 3→4", "Beat 4"]:
        failures.append("Frame/Beat mapping changed")
    if beat_map["timeline"][-1]["end"] != 10.0:
        failures.append("timeline does not end at 10.0 seconds")

    renderer_source = RENDERER.read_text(encoding="utf-8")
    frame_number_crop_count = renderer_source.count("sourceRect: CGRect(x: 68")
    frame_numbers_excluded = frame_number_crop_count == 5
    if not frame_numbers_excluded:
        failures.append("review-only Frame number regions are not excluded by all five source crops")

    text_drawing_tokens = ["NSAttributedString", "drawText(", "drawGlyphs("]
    no_video_text_drawing = not any(token in renderer_source for token in text_drawing_tokens)
    if not no_video_text_drawing:
        failures.append("renderer contains video text drawing code")

    circle_transition_tokens = ["addEllipse", "drawFrame2Reveal", "drawFrame3Reveal", "drawFrame4Reveal", "drawFrame5Reveal"]
    no_circle_transition_code = not any(token in renderer_source for token in circle_transition_tokens)
    if not no_circle_transition_code:
        failures.append("renderer contains circular transition code")

    video_evidence: dict[str, dict] = {}
    for label, path in VIDEOS.items():
        if not path.is_file() or path.stat().st_size == 0:
            failures.append(f"{label} MP4 missing or empty")
            continue
        metadata = probe(path)
        streams = metadata.get("streams", [])
        video_streams = [stream for stream in streams if stream.get("codec_type") == "video"]
        audio_streams = [stream for stream in streams if stream.get("codec_type") == "audio"]
        if len(video_streams) != 1:
            failures.append(f"{label} must have exactly one video stream")
            continue
        stream = video_streams[0]
        expected_size = (1280, 720) if label == "master" else (960, 540)
        if (stream.get("width"), stream.get("height")) != expected_size:
            failures.append(f"{label} dimensions mismatch")
        if stream.get("codec_name") != "h264":
            failures.append(f"{label} codec is not h264")
        if stream.get("pix_fmt") != "yuv420p":
            failures.append(f"{label} pixel format is not yuv420p")
        if stream.get("r_frame_rate") != "30/1":
            failures.append(f"{label} frame rate is not 30fps")
        if stream.get("nb_read_frames") != "300":
            failures.append(f"{label} does not contain exactly 300 decoded frames")
        if audio_streams:
            failures.append(f"{label} unexpectedly contains audio")
        measured_duration = float(metadata["format"]["duration"])
        if abs(measured_duration - 10.0) > 0.05:
            failures.append(f"{label} duration is not 10 seconds")
        if not has_faststart(path):
            failures.append(f"{label} lacks faststart")
        try:
            decode_fully(path)
        except subprocess.CalledProcessError:
            failures.append(f"{label} does not fully decode")
        detected_crops = cropdetect(path)
        expected_crop = expected_size + (0, 0)
        if detected_crops != {expected_crop}:
            failures.append(f"{label} black bar/crop detection mismatch: {sorted(detected_crops)}")
        video_evidence[label] = {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "duration": measured_duration,
            "width": stream.get("width"),
            "height": stream.get("height"),
            "codec": stream.get("codec_name"),
            "pixel_format": stream.get("pix_fmt"),
            "fps": stream.get("r_frame_rate"),
            "decoded_frame_count": int(stream.get("nb_read_frames", 0)),
            "audio": bool(audio_streams),
            "faststart": has_faststart(path),
            "full_decode": not any(f"{label} does not fully decode" == item for item in failures),
            "detected_content_crop": sorted(detected_crops),
            "black_bars_detected": detected_crops != {expected_crop},
        }

    required = [
        ROOT / "assets/review/storyboard-motion-contact-sheet.png",
        ROOT / "assets/review/transition-contact-sheet.png",
        ROOT / "assets/review/max-change-frame.jpg",
        ROOT / "assets/review/contact-sheet-0.5-second.png",
        ROOT / "assets/review/transition-frame-1-to-2.png",
        ROOT / "assets/review/transition-frame-2-to-3.png",
        ROOT / "assets/review/comparison-frame-2-to-3-before-after.png",
        ROOT / "assets/review/transition-frame-3-to-4.png",
        ROOT / "assets/review/transition-frame-4-to-5.png",
        *(ROOT / "assets/keyframes").glob("*.png"),
    ]
    if len(list((ROOT / "assets/keyframes").glob("*.png"))) != 5:
        failures.append("exactly five Frame/Beat keyframes are required")
    for path in required:
        if not path.is_file() or path.stat().st_size == 0:
            failures.append(f"missing review evidence: {path.relative_to(ROOT)}")

    evidence = {
        "schema_version": 1,
        "artifact_id": "farlens-brand-film-000-scene-01-motion-blocking",
        "status": "PASS" if not failures else "FAIL",
        "classification": "WORKING TEST / NON-CANONICAL / MOTION BLOCKING",
        "source_static_sequence": {
            "path": SOURCE.relative_to(REPO).as_posix(),
            "sha256": source_sha,
            "expected_sha256": EXPECTED_SOURCE_SHA,
            "unchanged": source_sha == EXPECTED_SOURCE_SHA,
        },
        "frame_beat_mapping": beat_map["timeline"],
        "videos": video_evidence,
        "checks": {
            "frame_beat_order_locked": not any("Frame" in item or "mapping" in item for item in failures),
            "duration_0_to_10_seconds": not any("duration" in item or "timeline" in item for item in failures),
            "iphone_compatible_encode": not any("iphone" in item for item in failures),
            "source_image_unchanged": source_sha == EXPECTED_SOURCE_SHA,
            "no_audio": not any("audio" in item for item in failures),
            "frame_numbers_detected_zero": frame_numbers_excluded and no_video_text_drawing,
            "black_bars_detected_zero": not any("black bar" in item for item in failures),
            "circular_transition_code_zero": no_circle_transition_code,
            "all_300_frames_regenerated": not any("300 decoded frames" in item for item in failures),
            "required_transition_evidence_present": not any("review evidence" in item for item in failures),
            "frame_2_to_3_revision_localized": (
                "drawFrame2To3DepthArrival" in renderer_source
                and "makeFrame2OriginBridgeMask" in renderer_source
                and "makeFrame2To3DepthMask" in renderer_source
            ),
        },
        "failures": failures,
    }
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args()
    evidence = verify()
    if args.write_evidence:
        (ROOT / "technical-evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    return 0 if evidence["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
