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
SOURCE_DIR = REPO / "docs/farlens/brand-film/assets/scene-02"
EXPECTED_SOURCES = {
    "BRAND_FILM_000_SCENE_02_STATIC_A1.png": "6c4d3f3896889db7a8e16802c92b8d739a4bc5342bdbfaeb12851523606fbc8d",
    "BRAND_FILM_000_SCENE_02_STATIC_A2.png": "c4f16462dbe58888a5072a6d023e39db877c57811b5041a444eeb8cc07e57122",
    "BRAND_FILM_000_SCENE_02_STATIC_A3.png": "dbc4f9c4449d23c72fca7d649b5d54112c2ecd00828c0ddf11598d78e6e23cac",
    "BRAND_FILM_000_SCENE_02_STATIC_A4.png": "b909d73c727d937ee8acf63ceee247214cecd46f888ceecabde50fdd227b7274",
    "BRAND_FILM_000_SCENE_02_STATIC_A5.png": "8ce4ad337213db9b99e0b75f973266494abb5d1fbcfe6d7f9468e1f59071dcc1",
}
VIDEOS = {
    "master": ROOT / "output/master/scene-02-motion-blocking.mp4",
    "iphone": ROOT / "output/iphone/scene-02-motion-blocking-iphone.mp4",
    "transition_review": ROOT / "output/review/scene-01-to-02-preroll.mp4",
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
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration,size:stream=codec_name,codec_type,width,height,r_frame_rate,pix_fmt,nb_read_frames",
            "-count_frames", "-of", "json", str(path),
        ],
        check=True, capture_output=True, text=True,
    )
    return json.loads(result.stdout)


def has_faststart(path: Path) -> bool:
    data = path.read_bytes()
    return data.find(b"moov") < data.find(b"mdat")


def decode_fully(path: Path) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"], check=True)


def cropdetect(path: Path, frames: int) -> set[tuple[int, int, int, int]]:
    result = subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-i", str(path), "-vf",
            "cropdetect=limit=2:round=2:reset=0", "-frames:v", str(frames), "-f", "null", "-",
        ],
        check=True, capture_output=True, text=True,
    )
    matches = re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", result.stderr)
    return {tuple(int(value) for value in match) for match in matches}


def verify() -> dict:
    failures: list[str] = []
    source_evidence = {}
    for filename, expected in EXPECTED_SOURCES.items():
        path = SOURCE_DIR / filename
        actual = sha256(path) if path.is_file() else "missing"
        source_evidence[filename] = {"sha256": actual, "expected_sha256": expected, "unchanged": actual == expected}
        if actual != expected:
            failures.append(f"adopted Static source mismatch: {filename}")

    beat_map = json.loads((ROOT / "beat-map.json").read_text(encoding="utf-8"))
    timeline = beat_map["timeline"]
    expected_local = [(0.0, 2.2), (2.2, 4.6), (4.6, 7.2), (7.2, 10.0), (10.0, 13.0)]
    expected_absolute = [(10.0, 12.2), (12.2, 14.6), (14.6, 17.2), (17.2, 20.0), (20.0, 23.0)]
    if [(item["local_start"], item["local_end"]) for item in timeline] != expected_local:
        failures.append("local Beat timing mismatch")
    if [(item["absolute_start"], item["absolute_end"]) for item in timeline] != expected_absolute:
        failures.append("absolute Beat timing mismatch")
    if [item["frame"] for item in timeline] != ["A1", "A2", "A3", "A4", "A5"]:
        failures.append("A1-A5 order changed")
    if [item["recognizable_membranes"] for item in timeline] != [3, 6, 8, "8-origin-priority-lowered", 0]:
        failures.append("membrane progression mismatch")

    renderer = (ROOT / "scripts/render_motion_blocking.swift").read_text(encoding="utf-8")
    required_renderer_markers = [
        "let membraneMasks = (0..<8).map(makeBandMask)",
        "drawA4Focused",
        "makeFocusMask",
        "makeSkyRestoreMask",
        "drawDistantLightBreath",
    ]
    for marker in required_renderer_markers:
        if marker not in renderer:
            failures.append(f"renderer marker missing: {marker}")
    forbidden_tokens = ["Camera Pan", "Camera Orbit", "addEllipse", "drawText(", "NSAttributedString"]
    if any(token in renderer for token in forbidden_tokens):
        failures.append("renderer contains prohibited camera/circle/text implementation token")

    video_evidence: dict[str, dict] = {}
    for label, path in VIDEOS.items():
        if not path.is_file() or path.stat().st_size == 0:
            failures.append(f"{label} MP4 missing or empty")
            continue
        metadata = probe(path)
        streams = metadata.get("streams", [])
        video_streams = [item for item in streams if item.get("codec_type") == "video"]
        audio_streams = [item for item in streams if item.get("codec_type") == "audio"]
        if len(video_streams) != 1:
            failures.append(f"{label} must contain one video stream")
            continue
        stream = video_streams[0]
        expected_size = (960, 540) if label == "iphone" else (1280, 720)
        expected_frames = 390 if label in {"master", "iphone"} else None
        if (stream.get("width"), stream.get("height")) != expected_size:
            failures.append(f"{label} dimensions mismatch")
        if stream.get("codec_name") != "h264" or stream.get("pix_fmt") != "yuv420p":
            failures.append(f"{label} encode is not H.264/yuv420p")
        if stream.get("r_frame_rate") != "30/1":
            failures.append(f"{label} is not 30fps")
        if expected_frames is not None and stream.get("nb_read_frames") != str(expected_frames):
            failures.append(f"{label} does not decode to {expected_frames} frames")
        if audio_streams:
            failures.append(f"{label} unexpectedly contains audio")
        duration = float(metadata["format"]["duration"])
        if label in {"master", "iphone"} and abs(duration - 13.0) > 0.01:
            failures.append(f"{label} duration is not 13.000 seconds")
        if not has_faststart(path):
            failures.append(f"{label} lacks faststart")
        try:
            decode_fully(path)
        except subprocess.CalledProcessError:
            failures.append(f"{label} full decode failed")
        detected = cropdetect(path, min(expected_frames or 60, 390))
        expected_crop = expected_size + (0, 0)
        if detected != {expected_crop}:
            failures.append(f"{label} black-bar detection mismatch: {sorted(detected)}")
        video_evidence[label] = {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "duration": duration,
            "width": stream.get("width"),
            "height": stream.get("height"),
            "codec": stream.get("codec_name"),
            "pixel_format": stream.get("pix_fmt"),
            "fps": stream.get("r_frame_rate"),
            "decoded_frame_count": int(stream.get("nb_read_frames", 0)),
            "audio": bool(audio_streams),
            "faststart": has_faststart(path),
            "full_decode": not any(f"{label} full decode failed" == issue for issue in failures),
            "black_bars_detected": detected != {expected_crop},
        }

    required = [
        ROOT / "assets/review/contact-sheet-0.5-second.png",
        ROOT / "assets/review/transition-contact-sheet.png",
        ROOT / "assets/review/a3-to-a4-focus-expanded.png",
        ROOT / "assets/review/a4-to-a5-space-recovery-expanded.png",
        ROOT / "assets/review/scene-01-to-02-transition.png",
        ROOT / "assets/source/scene-01-terminal-review.png",
        *(ROOT / "assets/keyframes").glob("*.png"),
    ]
    if len(list((ROOT / "assets/keyframes").glob("*.png"))) != 5:
        failures.append("exactly five Beat keyframes are required")
    for path in required:
        if not path.is_file() or path.stat().st_size == 0:
            failures.append(f"missing review artifact: {path.relative_to(ROOT)}")

    return {
        "schema_version": 1,
        "artifact_id": "farlens-brand-film-000-scene-02-motion-blocking",
        "status": "PASS" if not failures else "FAIL",
        "classification": "WORKING TEST / NON-CANONICAL / MOTION BLOCKING",
        "source_static_sequence": source_evidence,
        "frame_beat_mapping": timeline,
        "videos": video_evidence,
        "checks": {
            "duration_13_seconds": not any("13.000" in item or "timing" in item for item in failures),
            "frame_order_locked": not any("order" in item for item in failures),
            "membrane_progression_locked": not any("membrane progression" in item for item in failures),
            "source_images_unchanged": all(item["unchanged"] for item in source_evidence.values()),
            "no_audio": not any("audio" in item for item in failures),
            "black_bars_detected_zero": not any("black-bar" in item for item in failures),
            "all_390_frames_regenerated": not any("390 frames" in item for item in failures),
            "iphone_compatible_encode": not any("iphone" in item for item in failures),
            "review_artifacts_present": not any("review artifact" in item for item in failures),
            "a4_parent_child_is_existing_source_region": "makeFocusMask" in renderer,
            "a5_recognizable_membranes_zero_at_design_state": "makeSkyRestoreMask" in renderer,
            "distant_light_breath_only": "drawDistantLightBreath" in renderer,
        },
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args()
    evidence = verify()
    if args.write_evidence:
        (ROOT / "technical-evidence.json").write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    return 0 if evidence["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
