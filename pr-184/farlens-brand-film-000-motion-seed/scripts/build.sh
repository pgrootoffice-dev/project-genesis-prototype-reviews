#!/bin/zsh
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd)"
prototype_dir="$(cd "$script_dir/.." && pwd)"
master_dir="$prototype_dir/output/master"
iphone_dir="$prototype_dir/output/iphone"
poster_dir="$prototype_dir/assets/posters"

mkdir -p "$master_dir" "$iphone_dir" "$poster_dir"
python3 "$script_dir/render_motion.py" --root "$prototype_dir"

for name in section-0-motion-test section-4-motion-test final-motion-test; do
  ffmpeg -v error -y -i "$master_dir/$name.mp4" -an \
    -vf "scale=540:960:flags=lanczos" -c:v libx264 -preset medium -crf 27 \
    -pix_fmt yuv420p -movflags +faststart "$iphone_dir/$name-iphone.mp4"
  ffmpeg -v error -y -ss 4.8 -i "$master_dir/$name.mp4" -frames:v 1 -q:v 3 "$poster_dir/$name.jpg"
done

ffmpeg -v error -y \
  -i "$master_dir/section-0-motion-test.mp4" \
  -i "$master_dir/section-4-motion-test.mp4" \
  -i "$master_dir/final-motion-test.mp4" \
  -filter_complex "[0:v][1:v][2:v]concat=n=3:v=1:a=0[v]" \
  -map "[v]" -an -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p \
  -movflags +faststart "$master_dir/motion-seed-sequence.mp4"

ffmpeg -v error -y -i "$master_dir/motion-seed-sequence.mp4" -an \
  -vf "scale=540:960:flags=lanczos" -c:v libx264 -preset medium -crf 27 \
  -pix_fmt yuv420p -movflags +faststart "$iphone_dir/motion-seed-sequence-iphone.mp4"

python3 "$script_dir/verify.py" --root "$prototype_dir"
(
  cd "$prototype_dir"
  shasum -a 256 assets/source/*.jpg output/master/*.mp4 output/iphone/*.mp4 > checksums.sha256
)

echo "Built FARLENS Brand Film #000 Motion Seed Test"
