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
EXPECTED_SCENE2_SHA = "3e51b0fbf461d7cfc49c91c05420777f2da1bc843b476a65127483fb50a76904"
EXPECTED_TERMINAL_SHA = "32b9a74ea1ee1a01386671726abb47201bdcbc7c3ff4dd2f59a51cd157258c1c"
EXPECTED_MASTER_SHA = "f684be2ebcb176f043f419bdfed297bbeb1e4eb7ef68dae98cfbc462197d1b79"
EXPECTED_IPHONE_SHA = "2c7dce60db133313a5853ff66b77243879900e188e09d7735aee1ba3b34ef5a5"
EXPECTED_BASELINE_SHA = "d9d5eec5fc14a80f45f3c22de57c3d3b3dc8579e8f33f8749aab0731349534dc"

VIDEO_SPECS = {
    "master": {
        "path": ROOT / "output/master/scene-01-motion-blocking.mp4",
        "size": (1280, 720), "frames": 300, "duration": 10.0,
    },
    "iphone": {
        "path": ROOT / "output/iphone/scene-01-motion-blocking-iphone.mp4",
        "size": (960, 540), "frames": 300, "duration": 10.0,
    },
    "scene_1_to_2_review": {
        "path": ROOT / "output/review/scene-01-to-02-review-0-23.mp4",
        "size": (1280, 720), "frames": 690, "duration": 23.0,
    },
}
SCENE2_REFERENCE = ROOT / "assets/reference/scene-02/scene-02-motion-blocking-reference.mp4"
TERMINAL_REFERENCE = ROOT / "assets/reference/scene-02/scene-01-terminal-reference.png"
CONNECTION_BASELINE = ROOT / "assets/source/revision-02/scene-01-to-02-review-before-layered-transition.mp4"
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


def cropdetect(path: Path, frame_count: int) -> set[tuple[int, int, int, int]]:
    result = subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-i", str(path), "-vf",
            "cropdetect=limit=2:round=2:reset=0", "-frames:v", str(frame_count),
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
    if [item["frame"] for item in beat_map["timeline"]] != [1, 2, 3, 4, 5, 5]:
        failures.append("Frame order does not preserve five adopted Frames with the Frame 5 stability sub-beat")
    if [item["beat"] for item in beat_map["timeline"]] != ["Beat 1", "Beat 2", "Beat 3", "Beat 4", "Beat 4", "Beat 5"]:
        failures.append("Frame/Beat mapping changed")
    if any(current["end"] != following["start"] for current, following in zip(beat_map["timeline"], beat_map["timeline"][1:])):
        failures.append("machine-readable Beat timeline overlaps or contains a gap")
    if beat_map["timeline"][-1]["end"] != 10.0:
        failures.append("timeline does not end at 10.0 seconds")
    if beat_map["timeline"][-1]["start"] != 9.3:
        failures.append("Beat 5 connection stability does not begin at 9.3 seconds")

    motion_budget = json.loads((ROOT / "motion-budget.json").read_text(encoding="utf-8"))
    if [item["beat"] for item in motion_budget["beats"]] != [f"Beat {index}" for index in range(1, 6)]:
        failures.append("motion budget does not contain Beat 1 through Beat 5")
    if motion_budget["beats"][-1].get("start") != 9.3 or not motion_budget["beats"][-1].get("fully_stable"):
        failures.append("motion budget does not lock the 9.3 to 10.0 stability interval")

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

    scene2_semantic_tokens = ["InformationMembrane", "drawRefraction", "ParentLayer", "ChildLayer", "DistantPossibilityLight"]
    no_scene2_motion_semantics = not any(token in renderer_source for token in scene2_semantic_tokens)
    if not no_scene2_motion_semantics:
        failures.append("renderer imports Scene 2-specific Motion semantics")

    layer_budget_managed = all(token in renderer_source for token in ["enum SceneLayer", "struct MotionBudget", "connectionStableStart"])
    if not layer_budget_managed:
        failures.append("renderer does not expose Layer and Motion Budget controls")

    scene2_sha = sha256(SCENE2_REFERENCE) if SCENE2_REFERENCE.is_file() else "missing"
    terminal_reference_sha = sha256(TERMINAL_REFERENCE) if TERMINAL_REFERENCE.is_file() else "missing"
    baseline_sha = sha256(CONNECTION_BASELINE) if CONNECTION_BASELINE.is_file() else "missing"
    if scene2_sha != EXPECTED_SCENE2_SHA:
        failures.append("Scene 2 read-only reference SHA-256 mismatch")
    if terminal_reference_sha != EXPECTED_TERMINAL_SHA:
        failures.append("Scene 1 terminal reference SHA-256 mismatch")
    if baseline_sha != EXPECTED_BASELINE_SHA:
        failures.append("reviewed Scene 1 to 2 baseline SHA-256 mismatch")

    video_evidence: dict[str, dict] = {}
    for label, spec in VIDEO_SPECS.items():
        path = spec["path"]
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
        expected_size = spec["size"]
        if (stream.get("width"), stream.get("height")) != expected_size:
            failures.append(f"{label} dimensions mismatch")
        if stream.get("codec_name") != "h264":
            failures.append(f"{label} codec is not h264")
        if stream.get("pix_fmt") != "yuv420p":
            failures.append(f"{label} pixel format is not yuv420p")
        if stream.get("r_frame_rate") != "30/1":
            failures.append(f"{label} frame rate is not 30fps")
        if stream.get("nb_read_frames") != str(spec["frames"]):
            failures.append(f"{label} does not contain exactly {spec['frames']} decoded frames")
        if audio_streams:
            failures.append(f"{label} unexpectedly contains audio")
        measured_duration = float(metadata["format"]["duration"])
        if abs(measured_duration - spec["duration"]) > 0.01:
            failures.append(f"{label} duration is not {spec['duration']:.3f} seconds")
        if not has_faststart(path):
            failures.append(f"{label} lacks faststart")
        try:
            decode_fully(path)
        except subprocess.CalledProcessError:
            failures.append(f"{label} does not fully decode")
        detected_crops = cropdetect(path, spec["frames"])
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

    master_sha = video_evidence.get("master", {}).get("sha256", "missing")
    iphone_sha = video_evidence.get("iphone", {}).get("sha256", "missing")
    if master_sha != EXPECTED_MASTER_SHA:
        failures.append("Scene 1 Master SHA-256 changed")
    if iphone_sha != EXPECTED_IPHONE_SHA:
        failures.append("Scene 1 iPhone SHA-256 changed")

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
        ROOT / "assets/review/scene-01-to-02-transition.png",
        ROOT / "assets/review/scene-01-to-02-connection-expanded.png",
        ROOT / "assets/review/scene-01-to-02-before-after.png",
        ROOT / "assets/review/connection-layer-envelope.svg",
        ROOT / "assets/review/scene-01-to-02-review-contact-sheet.png",
        ROOT / "assets/review/scene-01-terminal-9.95.png",
        ROOT / "connection-evidence.json",
        ROOT / "motion-budget.json",
        ROOT / "connection-layer-envelopes.json",
        CONNECTION_BASELINE,
        SCENE2_REFERENCE,
        TERMINAL_REFERENCE,
        *(ROOT / "assets/keyframes").glob("*.png"),
    ]
    if len(list((ROOT / "assets/keyframes").glob("*.png"))) != 5:
        failures.append("exactly five Frame/Beat keyframes are required")
    for path in required:
        if not path.is_file() or path.stat().st_size == 0:
            failures.append(f"missing review evidence: {path.relative_to(ROOT)}")

    connection_path = ROOT / "connection-evidence.json"
    connection_evidence = json.loads(connection_path.read_text(encoding="utf-8")) if connection_path.is_file() else {}
    if connection_evidence.get("status") != "PASS":
        failures.append("Scene 1 to Scene 2 connection evidence is not PASS")
    required_connection_checks = {
        "scene_1_master_sha_unchanged",
        "scene_1_iphone_sha_unchanged",
        "scene_1_segment_faithful",
        "scene_2_after_transition_faithful",
        "scene_2_reference_sha_unchanged",
        "reviewed_baseline_sha_locked",
        "scene_1_terminal_hold_present",
        "transition_duration_1_1_seconds",
        "layer_order_locked",
        "warmth_melts_before_scene_2_layers",
        "air_horizon_before_terrain",
        "lower_left_mass_arrives_after_terrain",
        "information_membranes_arrive_last",
        "scene_2_semantics_begin_after_scene_1",
        "uniform_full_screen_blend_reduced",
        "rendered_transition_sample_fingerprints_locked",
        "implementation_envelopes_match_design",
        "implementation_composite_order_matches_design",
        "implementation_uses_spatial_masks_not_xfade",
        "implementation_renders_full_1_1_second_connection",
        "scene_2_entry_seam_matches_reference",
    }
    connection_checks = connection_evidence.get("checks", {})
    failed_connection_checks = sorted(
        check for check in required_connection_checks if connection_checks.get(check) is not True
    )
    if failed_connection_checks:
        failures.append("connection verification failed: " + ", ".join(failed_connection_checks))

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
        "scene_2_read_only_reference": {
            "pr": 191,
            "commit": "23cc8f2446f77895f926e7e19264f49dfc9012dd",
            "path": SCENE2_REFERENCE.relative_to(ROOT).as_posix(),
            "sha256": scene2_sha,
            "expected_sha256": EXPECTED_SCENE2_SHA,
            "unchanged": scene2_sha == EXPECTED_SCENE2_SHA,
        },
        "immutable_scene_1_outputs": {
            "master_sha256": master_sha,
            "expected_master_sha256": EXPECTED_MASTER_SHA,
            "master_unchanged": master_sha == EXPECTED_MASTER_SHA,
            "iphone_sha256": iphone_sha,
            "expected_iphone_sha256": EXPECTED_IPHONE_SHA,
            "iphone_unchanged": iphone_sha == EXPECTED_IPHONE_SHA,
        },
        "reviewed_connection_baseline": {
            "workflow_run_id": 31077899888,
            "artifact_id": 8958248421,
            "sha256": baseline_sha,
            "expected_sha256": EXPECTED_BASELINE_SHA,
            "unchanged": baseline_sha == EXPECTED_BASELINE_SHA,
        },
        "frame_beat_mapping": beat_map["timeline"],
        "motion_budget": motion_budget,
        "connection_evidence": connection_evidence,
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
            "five_beat_motion_budget_locked": not any("motion budget" in item or "Beat 5" in item for item in failures),
            "layer_management_explicit": layer_budget_managed,
            "scene_2_motion_semantics_absent": no_scene2_motion_semantics,
            "scene_2_reference_unchanged": scene2_sha == EXPECTED_SCENE2_SHA,
            "scene_1_to_2_connection_pass": connection_evidence.get("status") == "PASS",
            "scene_1_master_sha_unchanged": master_sha == EXPECTED_MASTER_SHA,
            "scene_1_iphone_sha_unchanged": iphone_sha == EXPECTED_IPHONE_SHA,
            "reviewed_connection_baseline_locked": baseline_sha == EXPECTED_BASELINE_SHA,
            "layered_connection_checks_pass": not failed_connection_checks,
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
