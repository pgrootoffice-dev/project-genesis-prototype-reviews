#!/bin/zsh
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd)"
prototype_dir="$(cd "$script_dir/.." && pwd)"
repo_root="$(cd "$prototype_dir/../.." && pwd)"
source_image="$repo_root/docs/farlens/brand-film/assets/scene-01/BRAND_FILM_000_SCENE_01_STATIC_SEQUENCE_WORKING_LOCK.png"
scene2_reference="$prototype_dir/assets/reference/scene-02/scene-02-motion-blocking-reference.mp4"
terminal_reference="$prototype_dir/assets/reference/scene-02/scene-01-terminal-reference.png"
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
# 10.0s. From 10.0–10.7s, its terminal environmental light dissolves over the
# already-adopted Scene 2 timeline; Scene 2 itself is never edited or replaced.
transitioned_scene2="$render_dir/scene-02-with-read-only-entry-transition.mp4"
ffmpeg -loglevel error -y \
  -f lavfi -i "color=c=0xEFAE5C:s=1280x720:r=30:d=13,format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='clip(72-hypot(X-640,(Y-360)*2.2)/8.2,0,72)',fade=t=out:st=0:d=0.7:alpha=1" \
  -i "$scene2_reference" \
  -filter_complex "[1:v]fps=30,settb=AVTB,setpts=PTS-STARTPTS[s2];[s2][0:v]overlay=shortest=1:format=auto,format=yuv420p[v]" \
  -map "[v]" -t 13 -r 30 -an -c:v libx264 -preset medium -crf 18 \
  -pix_fmt yuv420p -movflags +faststart "$transitioned_scene2"

ffmpeg -loglevel error -y \
  -i "$prototype_dir/output/master/scene-01-motion-blocking.mp4" \
  -i "$transitioned_scene2" \
  -filter_complex "[0:v]fps=30,settb=AVTB,setpts=PTS-STARTPTS[s1];[1:v]fps=30,settb=AVTB,setpts=PTS-STARTPTS[s2];[s1][s2]concat=n=2:v=1:a=0,format=yuv420p[v]" \
  -map "[v]" -t 23 -r 30 -an -c:v libx264 -preset medium -crf 18 \
  -pix_fmt yuv420p -movflags +faststart \
  "$prototype_dir/output/review/scene-01-to-02-review-0-23.mp4"

ffmpeg -loglevel error -y \
  -i "$prototype_dir/output/review/scene-01-to-02-review-0-23.mp4" \
  -vf "select='eq(n,279)+eq(n,288)+eq(n,297)+eq(n,300)+eq(n,309)+eq(n,321)',setpts=N/FRAME_RATE/TB,scale=400:225,tile=3x2:padding=8:margin=8:color=0x061329" \
  -frames:v 1 "$prototype_dir/assets/review/scene-01-to-02-transition.png"

ffmpeg -loglevel error -y \
  -i "$prototype_dir/output/review/scene-01-to-02-review-0-23.mp4" \
  -vf "fps=1,scale=240:135,tile=6x4:padding=8:margin=8:color=0x061329" \
  -frames:v 1 "$prototype_dir/assets/review/scene-01-to-02-review-contact-sheet.png"

ffmpeg -loglevel error -y -ss 9.95 \
  -i "$prototype_dir/output/master/scene-01-motion-blocking.mp4" \
  -frames:v 1 "$prototype_dir/assets/review/scene-01-terminal-9.95.png"

python3 "$script_dir/build_connection_evidence.py" \
  --scene1 "$prototype_dir/output/master/scene-01-motion-blocking.mp4" \
  --scene2 "$scene2_reference" \
  --review "$prototype_dir/output/review/scene-01-to-02-review-0-23.mp4" \
  --terminal "$prototype_dir/assets/review/scene-01-terminal-9.95.png" \
  --terminal-reference "$terminal_reference" \
  --output "$prototype_dir/connection-evidence.json"

ffprobe -v error -show_entries \
  format=duration,size,bit_rate:stream=index,codec_name,codec_type,width,height,r_frame_rate,pix_fmt \
  -of json "$prototype_dir/output/master/scene-01-motion-blocking.mp4" \
  > "$prototype_dir/production-evidence.json"

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
    assets/source/static-sequence-working-lock.png \
    assets/source/SOURCE_PROVENANCE.md \
    assets/reference/scene-02/scene-02-motion-blocking-reference.mp4 \
    assets/reference/scene-02/scene-01-terminal-reference.png \
    assets/reference/scene-02/REFERENCE_PROVENANCE.md \
    beat-map.json \
    motion-budget.json \
    connection-evidence.json \
    technical-evidence.json \
    production-evidence.json \
    > checksums.sha256
)

echo "Built Scene 1 Motion Blocking"
