#!/bin/zsh
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd)"
prototype_dir="$(cd "$script_dir/.." && pwd)"
repo_root="$(cd "$prototype_dir/../.." && pwd)"
source_dir="$repo_root/docs/farlens/brand-film/assets/scene-02"
render_dir="$(mktemp -d /tmp/farlens-scene02-blocking.XXXXXX)"
frame_dir="$render_dir/frames"
mkdir -p "$frame_dir" "$prototype_dir/output/master" "$prototype_dir/output/iphone" \
  "$prototype_dir/output/review" "$prototype_dir/assets/keyframes" "$prototype_dir/assets/review"

cleanup() {
  rm -rf "$render_dir"
}
trap cleanup EXIT

sources=(
  BRAND_FILM_000_SCENE_02_STATIC_A1.png
  BRAND_FILM_000_SCENE_02_STATIC_A2.png
  BRAND_FILM_000_SCENE_02_STATIC_A3.png
  BRAND_FILM_000_SCENE_02_STATIC_A4.png
  BRAND_FILM_000_SCENE_02_STATIC_A5.png
)
expected=(
  6c4d3f3896889db7a8e16802c92b8d739a4bc5342bdbfaeb12851523606fbc8d
  c4f16462dbe58888a5072a6d023e39db877c57811b5041a444eeb8cc07e57122
  dbc4f9c4449d23c72fca7d649b5d54112c2ecd00828c0ddf11598d78e6e23cac
  b909d73c727d937ee8acf63ceee247214cecd46f888ceecabde50fdd227b7274
  8ce4ad337213db9b99e0b75f973266494abb5d1fbcfe6d7f9468e1f59071dcc1
)

for index in {1..5}; do
  actual="$(shasum -a 256 "$source_dir/${sources[$index]}" | awk '{print $1}')"
  [[ "$actual" == "${expected[$index]}" ]]
done

swift -module-cache-path "$render_dir/swift-cache" \
  "$script_dir/render_motion_blocking.swift" \
  "$source_dir/${sources[1]}" "$source_dir/${sources[2]}" "$source_dir/${sources[3]}" \
  "$source_dir/${sources[4]}" "$source_dir/${sources[5]}" "$frame_dir"

ffmpeg -loglevel error -y \
  -framerate 30 -i "$frame_dir/frame-%04d.png" \
  -t 13 -r 30 -an -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -movflags +faststart "$prototype_dir/output/master/scene-02-motion-blocking.mp4"

ffmpeg -loglevel error -y \
  -i "$prototype_dir/output/master/scene-02-motion-blocking.mp4" \
  -vf "scale=960:540:flags=lanczos" -r 30 -an -c:v libx264 -preset medium -crf 22 \
  -pix_fmt yuv420p -movflags +faststart \
  "$prototype_dir/output/iphone/scene-02-motion-blocking-iphone.mp4"

timestamps=(1.1 3.4 5.9 8.6 11.8)
names=(a1-beat-1 a2-beat-2 a3-beat-3 a4-beat-4 a5-beat-5)
for index in {1..5}; do
  ffmpeg -loglevel error -y -ss "${timestamps[$index]}" \
    -i "$prototype_dir/output/master/scene-02-motion-blocking.mp4" -frames:v 1 \
    "$prototype_dir/assets/keyframes/${names[$index]}.png"
done

ffmpeg -loglevel error -y \
  -i "$prototype_dir/output/master/scene-02-motion-blocking.mp4" \
  -vf "fps=2,scale=240:135,tile=7x4:padding=8:margin=8:color=0x061329" \
  -frames:v 1 "$prototype_dir/assets/review/contact-sheet-0.5-second.png"

ffmpeg -loglevel error -y \
  -i "$prototype_dir/output/master/scene-02-motion-blocking.mp4" \
  -vf "select='eq(n,60)+eq(n,66)+eq(n,126)+eq(n,138)+eq(n,204)+eq(n,216)+eq(n,294)+eq(n,300)+eq(n,336)+eq(n,360)+eq(n,378)+eq(n,389)',setpts=N/FRAME_RATE/TB,scale=320:180,tile=4x3:padding=8:margin=8:color=0x061329" \
  -frames:v 1 "$prototype_dir/assets/review/transition-contact-sheet.png"

ffmpeg -loglevel error -y \
  -i "$prototype_dir/output/master/scene-02-motion-blocking.mp4" \
  -vf "select='eq(n,204)+eq(n,216)+eq(n,228)+eq(n,246)+eq(n,264)+eq(n,288)',setpts=N/FRAME_RATE/TB,crop=700:430:0:290,scale=490:301,tile=3x2:padding=8:margin=8:color=0x061329" \
  -frames:v 1 "$prototype_dir/assets/review/a3-to-a4-focus-expanded.png"

ffmpeg -loglevel error -y \
  -i "$prototype_dir/output/master/scene-02-motion-blocking.mp4" \
  -vf "select='eq(n,288)+eq(n,300)+eq(n,318)+eq(n,336)+eq(n,360)+eq(n,384)',setpts=N/FRAME_RATE/TB,scale=480:270,tile=3x2:padding=8:margin=8:color=0x061329" \
  -frames:v 1 "$prototype_dir/assets/review/a4-to-a5-space-recovery-expanded.png"

scene1_terminal="$prototype_dir/assets/source/scene-01-terminal-review.png"
test "$(shasum -a 256 "$scene1_terminal" | awk '{print $1}')" = "32b9a74ea1ee1a01386671726abb47201bdcbc7c3ff4dd2f59a51cd157258c1c"

ffmpeg -loglevel error -y -loop 1 -framerate 30 -t 1.0 -i "$scene1_terminal" \
  -i "$prototype_dir/output/master/scene-02-motion-blocking.mp4" \
  -filter_complex "[0:v]scale=1280:720,zoompan=z='min(zoom+0.00015,1.006)':d=1:s=1280x720:fps=30,trim=duration=1.0,settb=AVTB,setpts=PTS-STARTPTS[s1];[1:v]trim=start=0:end=1.4,fps=30,settb=AVTB,setpts=PTS-STARTPTS[s2];[s1][s2]xfade=transition=fade:duration=0.7:offset=0.3,format=yuv420p[v]" \
  -map "[v]" -t 1.7 -r 30 -an -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -movflags +faststart "$prototype_dir/output/review/scene-01-to-02-preroll.mp4"

ffmpeg -loglevel error -y \
  -i "$prototype_dir/output/review/scene-01-to-02-preroll.mp4" \
  -vf "select='eq(n,0)+eq(n,9)+eq(n,18)+eq(n,27)+eq(n,39)+eq(n,50)',setpts=N/FRAME_RATE/TB,scale=400:225,tile=3x2:padding=8:margin=8:color=0x061329" \
  -frames:v 1 "$prototype_dir/assets/review/scene-01-to-02-transition.png"

ffprobe -v error -show_entries \
  format=duration,size,bit_rate:stream=index,codec_name,codec_type,width,height,r_frame_rate,pix_fmt,nb_frames \
  -of json "$prototype_dir/output/master/scene-02-motion-blocking.mp4" \
  > "$prototype_dir/production-evidence.json"

python3 "$script_dir/verify_scene02.py" --write-evidence

(
  cd "$prototype_dir"
  shasum -a 256 \
    output/master/scene-02-motion-blocking.mp4 \
    output/iphone/scene-02-motion-blocking-iphone.mp4 \
    output/review/scene-01-to-02-preroll.mp4 \
    assets/keyframes/*.png assets/review/*.png \
    assets/source/scene-01-terminal-review.png assets/source/SOURCE_PROVENANCE.md \
    beat-map.json technical-evidence.json production-evidence.json \
    > checksums.sha256
)

echo "Built Scene 2 Motion Blocking"
