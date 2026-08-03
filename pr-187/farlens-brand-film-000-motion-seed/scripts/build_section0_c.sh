#!/bin/zsh
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd)"
prototype_dir="$(cd "$script_dir/.." && pwd)"
master_dir="$prototype_dir/output/master"
iphone_dir="$prototype_dir/output/iphone"
review_dir="$prototype_dir/assets/review"

mkdir -p "$master_dir" "$iphone_dir" "$review_dir"

# A, B, Section 4, Final, and all existing comparison bytes are input-only.
python3 "$script_dir/verify_section0_c.py" --root "$prototype_dir" --lock-only
python3 "$script_dir/render_section0_c.py" --root "$prototype_dir"

ffmpeg -v error -y -i "$master_dir/section-0-traveling-light-motion.mp4" -an \
  -vf "scale=540:960:flags=lanczos" -c:v libx264 -preset medium -crf 25 \
  -pix_fmt yuv420p -movflags +faststart \
  "$iphone_dir/section-0-traveling-light-motion-iphone.mp4"

ffmpeg -v error -y \
  -i "$master_dir/section-0-motion-test.mp4" \
  -i "$master_dir/section-0-layered-semantic-motion.mp4" \
  -i "$master_dir/section-0-traveling-light-motion.mp4" \
  -filter_complex "[0:v]setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[2:v]setpts=PTS-STARTPTS[c];[a][b][c]hstack=inputs=3[v]" \
  -map "[v]" -an -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p \
  -movflags +faststart -shortest "$master_dir/section-0-abc-comparison.mp4"

ffmpeg -v error -y -i "$master_dir/section-0-abc-comparison.mp4" -an \
  -vf "scale=810:480:flags=lanczos" -c:v libx264 -preset medium -crf 24 \
  -pix_fmt yuv420p -movflags +faststart \
  "$iphone_dir/section-0-abc-comparison-iphone.mp4"

ffmpeg -v error -y \
  -i "$master_dir/section-0-motion-test.mp4" \
  -i "$master_dir/section-0-layered-semantic-motion.mp4" \
  -i "$master_dir/section-0-traveling-light-motion.mp4" \
  -filter_complex "[0:v]setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[2:v]setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0[v]" \
  -map "[v]" -an -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p \
  -movflags +faststart "$master_dir/section-0-abc-sequence.mp4"

ffmpeg -v error -y -i "$master_dir/section-0-abc-sequence.mp4" -an \
  -vf "scale=540:960:flags=lanczos" -c:v libx264 -preset medium -crf 25 \
  -pix_fmt yuv420p -movflags +faststart \
  "$iphone_dir/section-0-abc-sequence-iphone.mp4"

python3 "$script_dir/verify_section0_c.py" --root "$prototype_dir"

echo "Built Section 0 Motion C and A/B/C comparisons; all existing bytes remain locked"
