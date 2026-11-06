#!/usr/bin/env bash
# Append stock footage after the promo: ./add-footage.sh footage.mp4 [out.mp4] [promo.mp4]
# 9:16: ./add-footage.sh footage.mp4 gamepadmouse-promo-9x16-full.mp4 gamepadmouse-promo-9x16.mp4
# The footage is scaled/padded to the promo's size @30fps. The promo keeps its soundtrack;
# the footage keeps its own audio (or gets silence if it has none).
set -euo pipefail
cd "$(dirname "$0")"
FOOTAGE="${1:?usage: ./add-footage.sh footage.mp4 [out.mp4]}"
OUT="${2:-gamepadmouse-promo-full.mp4}"
PROMO="${3:-gamepadmouse-promo.mp4}"
W=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$PROMO")
H=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$PROMO")

if ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$PROMO" | grep -q .; then
  PA="[0:a]aformat=sample_rates=48000:channel_layouts=stereo[pa]"
else
  PA="anullsrc=r=48000:cl=stereo,atrim=duration=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$PROMO")[pa]"
fi

if ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$FOOTAGE" | grep -q .; then
  FA="[1:a]aformat=sample_rates=48000:channel_layouts=stereo[fa]"
else
  FA="anullsrc=r=48000:cl=stereo,atrim=duration=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$FOOTAGE")[fa]"
fi

ffmpeg -y -i "$PROMO" -i "$FOOTAGE" -filter_complex "
  [0:v]setsar=1,fps=30,format=yuv420p[pv];
  $PA;
  [1:v]scale=$W:$H:force_original_aspect_ratio=decrease,pad=$W:$H:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=30,format=yuv420p,fade=t=in:st=0:d=0.5[fv];
  $FA;
  [pv][pa][fv][fa]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k -movflags +faststart "$OUT"
echo "wrote $OUT"
