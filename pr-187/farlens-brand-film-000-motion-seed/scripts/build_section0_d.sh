#!/usr/bin/env zsh
set -euo pipefail

ROOT="${0:A:h:h}"
cd "$ROOT"

python3 scripts/verify_section0_d.py --root . --lock-only
python3 scripts/build_section0_d_layers.py --root .
python3 scripts/render_section0_d.py --root .

ffmpeg -v error -y \
  -i output/master/section-0-layer-first-motion.mp4 \
  -an -vf 'scale=540:960:flags=lanczos' \
  -c:v libx264 -preset medium -crf 24 -pix_fmt yuv420p -r 30 -movflags +faststart \
  output/iphone/section-0-layer-first-motion-iphone.mp4

ffmpeg -v error -y \
  -i output/master/section-0-layer-breakdown.mp4 \
  -an -vf 'scale=540:960:flags=lanczos' \
  -c:v libx264 -preset medium -crf 24 -pix_fmt yuv420p -r 30 -movflags +faststart \
  output/iphone/section-0-layer-breakdown-iphone.mp4

ffmpeg -v error -y \
  -i output/master/section-0-motion-test.mp4 \
  -i output/master/section-0-layered-semantic-motion.mp4 \
  -i output/master/section-0-traveling-light-motion.mp4 \
  -i output/master/section-0-layer-first-motion.mp4 \
  -filter_complex '[0:v][1:v][2:v][3:v]hstack=inputs=4,format=yuv420p[v]' \
  -map '[v]' -an -r 30 -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -movflags +faststart \
  output/master/section-0-abcd-comparison.mp4

ffmpeg -v error -y \
  -i output/master/section-0-abcd-comparison.mp4 \
  -an -vf 'scale=960:426:flags=lanczos' \
  -c:v libx264 -preset medium -crf 24 -pix_fmt yuv420p -r 30 -movflags +faststart \
  output/iphone/section-0-abcd-comparison-iphone.mp4

ffmpeg -v error -y \
  -i output/master/section-0-motion-test.mp4 \
  -i output/master/section-0-layered-semantic-motion.mp4 \
  -i output/master/section-0-traveling-light-motion.mp4 \
  -i output/master/section-0-layer-first-motion.mp4 \
  -filter_complex '[0:v][1:v][2:v][3:v]concat=n=4:v=1:a=0,format=yuv420p[v]' \
  -map '[v]' -an -r 30 -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -movflags +faststart \
  output/master/section-0-abcd-sequence.mp4

ffmpeg -v error -y \
  -i output/master/section-0-abcd-sequence.mp4 \
  -an -vf 'scale=540:960:flags=lanczos' \
  -c:v libx264 -preset medium -crf 24 -pix_fmt yuv420p -r 30 -movflags +faststart \
  output/iphone/section-0-abcd-sequence-iphone.mp4

python3 scripts/verify_section0_d.py --root .
echo 'Built Section 0 layer-first Motion D; A/B/C remain byte-locked'
