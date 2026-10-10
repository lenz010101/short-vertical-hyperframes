#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Transcribe en la nube (GitHub Actions) el audio del clip base con
faster-whisper, en espanol, con timestamps por palabra.

Salidas:
  assets/transcript_full.json  [{id,text,start,end}]
  assets/transcript_full.txt   version legible
"""
import json
import os
import sys

from faster_whisper import WhisperModel

SRC = os.environ.get("ASR_SRC", "video-1/assets/source_audio.m4a")
MODEL = os.environ.get("ASR_MODEL", "small")
LANG = os.environ.get("ASR_LANG", "es")
OUT_JSON = os.environ.get("ASR_OUT", "video-1/assets/transcript_full.json")
THREADS = int(os.environ.get("ASR_THREADS") or (os.cpu_count() or 4))

print("modelo=%s lang=%s hilos=%d" % (MODEL, LANG, THREADS), flush=True)
model = WhisperModel(MODEL, device="cpu", compute_type="int8",
                     cpu_threads=THREADS)

segments, info = model.transcribe(
    SRC,
    language=LANG,
    beam_size=5,
    word_timestamps=True,
    vad_filter=True,
    vad_parameters={"min_silence_duration_ms": 400},
    condition_on_previous_text=False,
)
print("duracion=%.1fs idioma=%s" % (info.duration, info.language), flush=True)

words = []
lines = []
for seg in segments:
    txt = seg.text.strip()
    if txt:
        lines.append("%7.1f-%7.1f  %s" % (seg.start, seg.end, txt))
        print(lines[-1], flush=True)
    for w in (seg.words or []):
        t = w.word.strip()
        if t:
            words.append({"id": "w%d" % len(words), "text": t,
                          "start": round(float(w.start), 3),
                          "end": round(float(w.end), 3)})

os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
json.dump(words, open(OUT_JSON, "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
open(os.path.splitext(OUT_JSON)[0] + ".txt", "w",
     encoding="utf-8").write("\n".join(lines))
print("OK -> %s (%d palabras)" % (OUT_JSON, len(words)))
