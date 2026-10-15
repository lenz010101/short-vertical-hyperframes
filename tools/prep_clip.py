#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Solo prepara el video: recorte a banda 1080x810 (crop auto via ffprobe)."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, "..", "video-1")
ASSETS = os.path.join(PROJ, "assets")
SRC = os.environ.get("HF_SRC", os.path.join(ASSETS, "output_base.mp4"))
DUR = float(os.environ.get("CLIP_DUR", "52.0"))
BW, BH = 1080, 810

def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")

r = sh(["ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height", "-of", "csv=p=0", SRC])
try:
    w, h = [int(x) for x in r.stdout.strip().split(",")[:2]]
except Exception:
    w, h = 1280, 720

cw = int(h * BW / BH)
if cw > w:
    crop = "crop=%d:%d:(in_w-%d)/2:(in_h-%d)/2" % (w, int(w * BH / BW), w, int(w * BH / BW))
else:
    crop = "crop=%d:%d:(in_w-%d)/2:0" % (cw, h, cw)
print("fuente %dx%d -> %s" % (w, h, crop))

out = os.path.join(ASSETS, "seg_00.mp4")
cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
       "-t", "%.3f" % DUR, "-i", SRC,
       "-vf", "%s,scale=%d:%d:flags=lanczos,setsar=1" % (crop, BW, BH),
       "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
       "-movflags", "+faststart", out]
r = sh(cmd)
if r.returncode != 0:
    sys.exit("ffmpeg: " + r.stderr[-500:])
print("seg_00.mp4 OK (%.1fs)" % DUR)
