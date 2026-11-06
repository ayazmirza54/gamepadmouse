#!/usr/bin/env bash
# Append stock footage after the promo: ./add-footage.sh footage.mp4 [out.mp4]
# The footage is scaled/padded to 1920x1080 @30fps. The promo is silent, so it gets
# a silent track; the footage keeps its own audio if it has any.
set -euo pipefail
cd "$(dirname "$0")"
FOOTAGE="${1:?usage: ./add-footage.sh footage.mp4 [out.mp4]}"
OUT="${2:-gamepadmouse-promo-full.mp4}"
PROMO=gamepadmouse-promo.mp4

if ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$FOOTAGE" | grep -q .; then
  FA="[1:a]aformat=sample_rates=48000:channel_layouts=stereo[fa]"
else
  FA="anullsrc=r=48000:cl=stereo,atrim=duration=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$FOOTAGE")[fa]"
fi

ffmpeg -y -i "$PROMO" -i "$FOOTAGE" -filter_complex "
  [0:v]setsar=1,fps=30,format=yuv420p[pv];
  anullsrc=r=48000:cl=stereo,atrim=duration=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$PROMO")[pa];
  [1:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=30,format=yuv420p,fade=t=in:st=0:d=0.5[fv];
  $FA;
  [pv][pa][fv][fa]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k -movflags +faststart "$OUT"
echo "wrote $OUT"
