#!/bin/zsh
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd)"
prototype_dir="$(cd "$script_dir/.." && pwd)"
master_dir="$prototype_dir/output/master"
iphone_dir="$prototype_dir/output/iphone"
review_dir="$prototype_dir/assets/review"

mkdir -p "$master_dir" "$iphone_dir" "$review_dir"

# Fail before rendering if any Base Motion or Final byte changed.
python3 "$script_dir/verify_layered_ab.py" --root "$prototype_dir" --a-lock-only
python3 "$script_dir/render_layered_semantic.py" --root "$prototype_dir"

for section in 0 4; do
  source="$master_dir/section-$section-layered-semantic-motion.mp4"
  ffmpeg -v error -y -i "$source" -an \
    -vf "scale=540:960:flags=lanczos" -c:v libx264 -preset medium -crf 25 \
    -pix_fmt yuv420p -movflags +faststart \
    "$iphone_dir/section-$section-layered-semantic-motion-iphone.mp4"

  ffmpeg -v error -y \
    -i "$master_dir/section-$section-motion-test.mp4" \
    -i "$source" \
    -filter_complex "[0:v]setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[a][b]hstack=inputs=2[v]" \
    -map "[v]" -an -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p \
    -movflags +faststart -shortest "$master_dir/section-$section-ab-comparison.mp4"

  ffmpeg -v error -y -i "$master_dir/section-$section-ab-comparison.mp4" -an \
    -vf "scale=720:640:flags=lanczos" -c:v libx264 -preset medium -crf 25 \
    -pix_fmt yuv420p -movflags +faststart \
    "$iphone_dir/section-$section-ab-comparison-iphone.mp4"
done

ffmpeg -v error -y \
  -i "$master_dir/section-0-ab-comparison.mp4" \
  -i "$master_dir/section-4-ab-comparison.mp4" \
  -filter_complex "[0:v]setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0[v]" \
  -map "[v]" -an -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p \
  -movflags +faststart "$master_dir/layered-semantic-ab-sequence.mp4"

ffmpeg -v error -y -i "$master_dir/layered-semantic-ab-sequence.mp4" -an \
  -vf "scale=720:640:flags=lanczos" -c:v libx264 -preset medium -crf 25 \
  -pix_fmt yuv420p -movflags +faststart \
  "$iphone_dir/layered-semantic-ab-sequence-iphone.mp4"

python3 "$script_dir/verify_layered_ab.py" --root "$prototype_dir"

echo "Built FARLENS Layered Semantic Motion A/B working test; A and Final bytes remain locked"
