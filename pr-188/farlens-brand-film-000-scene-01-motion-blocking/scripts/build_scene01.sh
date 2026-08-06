#!/bin/zsh
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd)"
prototype_dir="$(cd "$script_dir/.." && pwd)"
repo_root="$(cd "$prototype_dir/../.." && pwd)"
source_image="$repo_root/docs/farlens/brand-film/assets/scene-01/BRAND_FILM_000_SCENE_01_STATIC_SEQUENCE_WORKING_LOCK.png"
scene2_reference="$prototype_dir/assets/reference/scene-02/scene-02-motion-blocking-reference.mp4"
terminal_reference="$prototype_dir/assets/reference/scene-02/scene-01-terminal-reference.png"
connection_baseline="$prototype_dir/assets/source/revision-02/scene-01-to-02-review-before-layered-transition.mp4"
render_dir="$(mktemp -d /tmp/farlens-scene01-blocking.XXXXXX)"
frame_dir="$render_dir/frames"
mkdir -p "$frame_dir" "$prototype_dir/output/master" "$prototype_dir/output/iphone" \
  "$prototype_dir/output/review" "$prototype_dir/assets/keyframes" \
  "$prototype_dir/assets/review" "$prototype_dir/assets/source"

cleanup() {
  rm -rf "$render_dir"
}
trap cleanup EXIT

expected_source_sha="97bfd90afc8e6ceaa6d6bf3e8a26d78b6cf9b9d506240af5fd84fb5b9d290c59"
actual_source_sha="$(shasum -a 256 "$source_image" | awk '{print $1}')"
[[ "$actual_source_sha" == "$expected_source_sha" ]]
[[ "$(shasum -a 256 "$scene2_reference" | awk '{print $1}')" == "3e51b0fbf461d7cfc49c91c05420777f2da1bc843b476a65127483fb50a76904" ]]
[[ "$(shasum -a 256 "$terminal_reference" | awk '{print $1}')" == "32b9a74ea1ee1a01386671726abb47201bdcbc7c3ff4dd2f59a51cd157258c1c" ]]
[[ "$(shasum -a 256 "$connection_baseline" | awk '{print $1}')" == "d9d5eec5fc14a80f45f3c22de57c3d3b3dc8579e8f33f8749aab0731349534dc" ]]
cp "$source_image" "$prototype_dir/assets/source/static-sequence-working-lock.png"

swift -module-cache-path "$render_dir/swift-cache" \
  "$script_dir/render_motion_blocking.swift" "$source_image" "$frame_dir"

ffmpeg -loglevel error -y \
  -framerate 30 -i "$frame_dir/frame-%04d.png" \
  -t 10 -r 30 -an -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -movflags +faststart \
  "$prototype_dir/output/master/scene-01-motion-blocking.mp4"

ffmpeg -loglevel error -y \
  -i "$prototype_dir/output/master/scene-01-motion-blocking.mp4" \
  -vf "scale=960:540:flags=lanczos" -r 30 -an -c:v libx264 -preset medium -crf 22 \
  -pix_fmt yuv420p -movflags +faststart \
  "$prototype_dir/output/iphone/scene-01-motion-blocking-iphone.mp4"

timestamps=(0.8 2.7 4.7 7.1 9.65)
names=(frame-01-beat-1 frame-02-beat-2 frame-03-beat-3 frame-04-beat-4 frame-05-beat-5)
for index in {1..5}; do
  ffmpeg -loglevel error -y \
    -ss "${timestamps[$index]}" \
    -i "$prototype_dir/output/master/scene-01-motion-blocking.mp4" \
    -frames:v 1 "$prototype_dir/assets/keyframes/${names[$index]}.png"
done

ffmpeg -loglevel error -y \
  -ss 6.8 -i "$prototype_dir/output/master/scene-01-motion-blocking.mp4" \
  -frames:v 1 "$prototype_dir/assets/review/max-change-frame.jpg"

ffmpeg -loglevel error -y \
  -i "$prototype_dir/output/iphone/scene-01-motion-blocking-iphone.mp4" \
  -vf "fps=1.25,scale=320:180,tile=4x3:padding=8:margin=8:color=0x061329" \
  -frames:v 1 "$prototype_dir/assets/review/storyboard-motion-contact-sheet.png"

ffmpeg -loglevel error -y \
  -i "$prototype_dir/output/master/scene-01-motion-blocking.mp4" \
  -vf "select='eq(n,30)+eq(n,48)+eq(n,81)+eq(n,96)+eq(n,153)+eq(n,171)+eq(n,222)+eq(n,240)',setpts=N/FRAME_RATE/TB,scale=320:180,tile=4x2:padding=8:margin=8:color=0x061329" \
  -frames:v 1 "$prototype_dir/assets/review/transition-contact-sheet.png"

ffmpeg -loglevel error -y \
  -i "$prototype_dir/output/master/scene-01-motion-blocking.mp4" \
  -vf "fps=2,scale=240:135,tile=5x4:padding=8:margin=8:color=0x061329" \
  -frames:v 1 "$prototype_dir/assets/review/contact-sheet-0.5-second.png"

ffmpeg -loglevel error -y \
  -i "$prototype_dir/output/master/scene-01-motion-blocking.mp4" \
  -vf "select='eq(n,30)+eq(n,39)+eq(n,48)+eq(n,57)+eq(n,69)+eq(n,84)',setpts=N/FRAME_RATE/TB,scale=400:225,tile=3x2:padding=8:margin=8:color=0x061329" \
  -frames:v 1 "$prototype_dir/assets/review/transition-frame-1-to-2.png"

ffmpeg -loglevel error -y \
  -i "$prototype_dir/output/master/scene-01-motion-blocking.mp4" \
  -vf "select='eq(n,78)+eq(n,84)+eq(n,90)+eq(n,99)+eq(n,111)+eq(n,120)',setpts=N/FRAME_RATE/TB,scale=400:225,tile=3x2:padding=8:margin=8:color=0x061329" \
  -frames:v 1 "$prototype_dir/assets/review/transition-frame-2-to-3.png"

# The before/after sheet is historical review evidence. Supply the approved
# pre-revision MP4 when creating or refreshing it; subsequent deterministic
# rebuilds preserve the committed comparison asset.
comparison_path="$prototype_dir/assets/review/comparison-frame-2-to-3-before-after.png"
if [[ -n "${FRAME23_BASELINE_MP4:-}" ]]; then
  test -s "$FRAME23_BASELINE_MP4"
  baseline_sheet="$render_dir/frame-2-to-3-before.png"
  ffmpeg -loglevel error -y \
    -i "$FRAME23_BASELINE_MP4" \
    -vf "select='eq(n,78)+eq(n,84)+eq(n,90)+eq(n,99)+eq(n,111)+eq(n,120)',setpts=N/FRAME_RATE/TB,scale=400:225,tile=3x2:padding=8:margin=8:color=0x061329" \
    -frames:v 1 "$baseline_sheet"
  ffmpeg -loglevel error -y \
    -i "$baseline_sheet" \
    -i "$prototype_dir/assets/review/transition-frame-2-to-3.png" \
    -filter_complex "[0:v][1:v]hstack=inputs=2" \
    -frames:v 1 "$comparison_path"
else
  test -s "$comparison_path"
fi

ffmpeg -loglevel error -y \
  -i "$prototype_dir/output/master/scene-01-motion-blocking.mp4" \
  -vf "select='eq(n,153)+eq(n,159)+eq(n,171)+eq(n,183)+eq(n,201)+eq(n,219)',setpts=N/FRAME_RATE/TB,scale=400:225,tile=3x2:padding=8:margin=8:color=0x061329" \
  -frames:v 1 "$prototype_dir/assets/review/transition-frame-3-to-4.png"

ffmpeg -loglevel error -y \
  -i "$prototype_dir/output/master/scene-01-motion-blocking.mp4" \
  -vf "select='eq(n,222)+eq(n,228)+eq(n,240)+eq(n,255)+eq(n,270)+eq(n,285)',setpts=N/FRAME_RATE/TB,scale=400:225,tile=3x2:padding=8:margin=8:color=0x061329" \
  -frames:v 1 "$prototype_dir/assets/review/transition-frame-4-to-5.png"

# Review-only 0–23 second assembly. Scene 1 stays completely stable through
# 10.0s. The first 1.1s of the read-only Scene 2 timeline is reconstructed with
# separate spatial envelopes: warmth, air/horizon, terrain, lower-left masses,
# then membranes. Scene 2 source time continues underneath without retiming.
layered_core="$render_dir/scene-01-to-02-layered-core.mkv"
layered_transition="$render_dir/scene-01-to-02-layered-transition.mkv"
ffmpeg -loglevel error -y \
  -loop 1 -framerate 30 -t 0.9 -i "$terminal_reference" \
  -i "$scene2_reference" \
  -f lavfi -i "color=c=0x081C3D:s=1280x720:r=30:d=1.1,format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='clip(105-hypot(X-640,(Y-360)*2.1)/6.8,0,105)',fade=t=in:st=0.05:d=0.25:alpha=1" \
  -filter_complex "[0:v]scale=1280:720,fps=30,settb=AVTB,setpts=PTS-STARTPTS,format=rgba[terminal];[1:v]trim=duration=0.9,fps=30,settb=AVTB,setpts=PTS-STARTPTS,split=4[s2a][s2t][s2l][s2m];[terminal][2:v]overlay=shortest=1:format=auto[cooled];[s2a]gblur=sigma=18,format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='clip((420-Y)*4.25,0,255)',fade=t=in:st=0.22:d=0.28:alpha=1[atmo];[s2t]format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='clip((Y-340)*6.375,0,255)*clip((X-360)*4.25,0,255)/255',fade=t=in:st=0.42:d=0.23:alpha=1[terrain];[s2l]format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='clip((Y-340)*6.375,0,255)*clip((480-X)*4.25,0,255)/255',fade=t=in:st=0.60:d=0.12:alpha=1[leftmass];[s2m]format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='clip((420-Y)*6.375,0,255)',fade=t=in:st=0.76:d=0.10:alpha=1[membranes];[cooled][atmo]overlay=shortest=1:format=auto[s1];[s1][terrain]overlay=shortest=1:format=auto[s2];[s2][leftmass]overlay=shortest=1:format=auto[s3];[s3][membranes]overlay=shortest=1:format=auto,format=yuv420p[v]" \
  -map "[v]" -t 0.9 -r 30 -an -c:v ffv1 -level 3 \
  -pix_fmt yuv420p "$layered_core"

# Keep the complete Review-only connection at 1.1s. After all spatial
# partitions have converged, preserve 0.2s of the exact Scene 2 source inside
# the transition segment so the following read-only tail has no image seam.
ffmpeg -loglevel error -y \
  -i "$layered_core" -i "$scene2_reference" \
  -filter_complex "[0:v]trim=start=0:end=0.9,fps=30,settb=AVTB,setpts=PTS-STARTPTS[core];[1:v]trim=start=0.9:end=1.1,fps=30,settb=AVTB,setpts=PTS-STARTPTS[settle];[core][settle]concat=n=2:v=1:a=0,format=yuv420p[v]" \
  -map "[v]" -t 1.1 -r 30 -an -c:v ffv1 -level 3 \
  -pix_fmt yuv420p "$layered_transition"

ffmpeg -loglevel error -y \
  -i "$prototype_dir/output/master/scene-01-motion-blocking.mp4" \
  -i "$layered_transition" \
  -i "$scene2_reference" \
  -filter_complex "[0:v]trim=start=0:end=10,fps=30,settb=AVTB,setpts=PTS-STARTPTS[s1];[1:v]trim=start=0:end=1.1,fps=30,settb=AVTB,setpts=PTS-STARTPTS[transition];[2:v]trim=start=1.1:end=13,fps=30,settb=AVTB,setpts=PTS-STARTPTS[s2tail];[s1][transition][s2tail]concat=n=3:v=1:a=0,format=yuv420p[v]" \
  -map "[v]" -t 23 -r 30 -an -c:v libx264 -preset medium -crf 18 \
  -pix_fmt yuv420p -movflags +faststart \
  "$prototype_dir/output/review/scene-01-to-02-review-0-23.mp4"

ffmpeg -loglevel error -y \
  -i "$prototype_dir/output/review/scene-01-to-02-review-0-23.mp4" \
  -vf "select='eq(n,279)+eq(n,291)+eq(n,299)+eq(n,300)+eq(n,306)+eq(n,312)+eq(n,318)+eq(n,324)+eq(n,330)+eq(n,333)',setpts=N/FRAME_RATE/TB,scale=320:180,tile=5x2:padding=8:margin=8:color=0x061329" \
  -frames:v 1 "$prototype_dir/assets/review/scene-01-to-02-transition.png"

ffmpeg -loglevel error -y \
  -i "$prototype_dir/output/review/scene-01-to-02-review-0-23.mp4" \
  -vf "select='eq(n,300)+eq(n,306)+eq(n,312)+eq(n,318)+eq(n,326)+eq(n,333)',setpts=N/FRAME_RATE/TB,scale=480:270,tile=3x2:padding=8:margin=8:color=0x061329" \
  -frames:v 1 "$prototype_dir/assets/review/scene-01-to-02-connection-expanded.png"

baseline_strip="$render_dir/scene-01-to-02-before.png"
revised_strip="$render_dir/scene-01-to-02-after.png"
ffmpeg -loglevel error -y -i "$connection_baseline" \
  -vf "select='eq(n,300)+eq(n,306)+eq(n,312)+eq(n,318)+eq(n,326)+eq(n,333)',setpts=N/FRAME_RATE/TB,scale=240:135,tile=6x1:padding=8:margin=8:color=0x061329" \
  -frames:v 1 "$baseline_strip"
ffmpeg -loglevel error -y -i "$prototype_dir/output/review/scene-01-to-02-review-0-23.mp4" \
  -vf "select='eq(n,300)+eq(n,306)+eq(n,312)+eq(n,318)+eq(n,326)+eq(n,333)',setpts=N/FRAME_RATE/TB,scale=240:135,tile=6x1:padding=8:margin=8:color=0x061329" \
  -frames:v 1 "$revised_strip"
ffmpeg -loglevel error -y -i "$baseline_strip" -i "$revised_strip" \
  -filter_complex "[0:v][1:v]vstack=inputs=2" -frames:v 1 \
  "$prototype_dir/assets/review/scene-01-to-02-before-after.png"

ffmpeg -loglevel error -y \
  -i "$prototype_dir/output/review/scene-01-to-02-review-0-23.mp4" \
  -vf "fps=1,scale=240:135,tile=6x4:padding=8:margin=8:color=0x061329" \
  -frames:v 1 "$prototype_dir/assets/review/scene-01-to-02-review-contact-sheet.png"

ffmpeg -loglevel error -y -ss 9.95 \
  -i "$prototype_dir/output/master/scene-01-motion-blocking.mp4" \
  -frames:v 1 "$prototype_dir/assets/review/scene-01-terminal-9.95.png"

python3 "$script_dir/build_connection_evidence.py" \
  --scene1 "$prototype_dir/output/master/scene-01-motion-blocking.mp4" \
  --iphone "$prototype_dir/output/iphone/scene-01-motion-blocking-iphone.mp4" \
  --scene2 "$scene2_reference" \
  --baseline "$connection_baseline" \
  --review "$prototype_dir/output/review/scene-01-to-02-review-0-23.mp4" \
  --terminal "$prototype_dir/assets/review/scene-01-terminal-9.95.png" \
  --terminal-reference "$terminal_reference" \
  --envelopes "$prototype_dir/connection-layer-envelopes.json" \
  --implementation "$script_dir/build_scene01.sh" \
  --output "$prototype_dir/connection-evidence.json"

python3 "$script_dir/build_production_evidence.py" \
  --master "$prototype_dir/output/master/scene-01-motion-blocking.mp4" \
  --iphone "$prototype_dir/output/iphone/scene-01-motion-blocking-iphone.mp4" \
  --review "$prototype_dir/output/review/scene-01-to-02-review-0-23.mp4" \
  --scene2 "$scene2_reference" \
  --baseline "$connection_baseline" \
  --envelopes "$prototype_dir/connection-layer-envelopes.json" \
  --output "$prototype_dir/production-evidence.json"

python3 "$script_dir/verify_scene01.py" --write-evidence

(
  cd "$prototype_dir"
  shasum -a 256 \
    output/master/scene-01-motion-blocking.mp4 \
    output/iphone/scene-01-motion-blocking-iphone.mp4 \
    output/review/scene-01-to-02-review-0-23.mp4 \
    assets/keyframes/*.png \
    assets/review/*.jpg \
    assets/review/*.png \
    assets/review/*.svg \
    assets/source/static-sequence-working-lock.png \
    assets/source/SOURCE_PROVENANCE.md \
    assets/source/revision-02/scene-01-to-02-review-before-layered-transition.mp4 \
    assets/reference/scene-02/scene-02-motion-blocking-reference.mp4 \
    assets/reference/scene-02/scene-01-terminal-reference.png \
    assets/reference/scene-02/REFERENCE_PROVENANCE.md \
    beat-map.json \
    motion-budget.json \
    connection-layer-envelopes.json \
    connection-evidence.json \
    technical-evidence.json \
    production-evidence.json \
    > checksums.sha256
)

echo "Built Scene 1 Motion Blocking"
