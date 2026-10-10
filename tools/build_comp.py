#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Genera la composicion HyperFrames (HTML -> video) para el short vertical.

Entrada:
  segments.json   -> lista de recortes de la fuente (in/out) y sus puntos
  assets/full_transcript.json -> palabras con timestamps de la fuente

Salida:
  assets/seg_XX.mp4      recortes 4:3 (1080x810, 30fps, con voz)
  index.html             composicion

Diseno: lienzo 1080x1920, banda de video 4:3 al centro, titulo arriba,
chips numerados que se acumulan, captions karaoke, barra de progreso,
transiciones CSS entre bloques y SFX.
"""

import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROJ = os.environ.get("HF_PROJ") or os.path.join(ROOT, "video-1")
ASSETS = os.path.join(PROJ, "assets")
SRC = os.environ.get("HF_SRC") or r"C:\Users\Admin\Downloads\clip base (2).mp4"
SFX_DIR = os.environ.get("HF_SFX") or os.path.join(
    ROOT, ".agents", "skills", "media-use", "audio", "assets", "sfx")

W, H = 1080, 1920
BAND_W, BAND_H = 1080, 810
BAND_Y = 552
FPS = 30

ACCENT = "#FFD84D"
BG = "#07080B"

# Recorte 4:3 de la fuente 1280x720, con el sujeto a la izquierda para dejar
# libre el lado del texto.
CROP = "crop=960:720:320:0"


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", **kw)


def load_json(path):
    with open(path, encoding="utf-8-sig") as fh:
        return json.load(fh)


def extract_segments(segs):
    made = []
    for i, s in enumerate(segs):
        out = os.path.join(ASSETS, "seg_%02d.mp4" % i)
        if os.path.exists(out):
            print("  seg_%02d.mp4 (ya existe)" % i)
            made.append(out)
            continue
        dur = s["out"] - s["in"]
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", "%.3f" % s["in"], "-t", "%.3f" % dur, "-i", SRC,
            "-vf", "%s,scale=%d:%d:flags=lanczos,setsar=1" % (CROP, BAND_W, BAND_H),
            "-r", str(FPS),
            "-c:v", "libx264", "-preset", "slow", "-crf", "17",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-movflags", "+faststart", out,
        ]
        r = sh(cmd)
        if r.returncode != 0:
            sys.exit("ffmpeg fallo en segmento %d: %s" % (i, r.stderr[-500:]))
        made.append(out)
        print("  seg_%02d.mp4  %.1fs -> %.1fs" % (i, s["in"], s["out"]))
    return made


def copy_audio():
    """Copia musica y SFX al proyecto si existen (best-effort)."""
    os.makedirs(os.path.join(ASSETS, "sfx"), exist_ok=True)
    if not os.path.isdir(SFX_DIR):
        return
    for name in ("whoosh-cinematic.mp3", "whoosh-short.mp3", "pop.mp3",
                 "riser.mp3", "impact-bass-1.mp3", "sparkle.mp3",
                 "click-soft.mp3"):
        src = os.path.join(SFX_DIR, name)
        dst = os.path.join(ASSETS, "sfx", name)
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)


def group_captions(words, t0, src_in, src_out):
    """Palabras de la fuente -> grupos de caption rebasados al tiempo de comp."""
    sel = [w for w in words if w["start"] >= src_in - 0.05 and w["end"] <= src_out + 0.05]
    groups, cur, n = [], [], 0
    for w in sel:
        cur.append(w)
        n += len(w["text"]) + 1
        gap_next = None
        groups_break = n >= 26
        if groups_break:
            groups.append(cur)
            cur, n = [], 0
    if cur:
        groups.append(cur)

    out = []
    for g in groups:
        if not g:
            continue
        st = t0 + (g[0]["start"] - src_in)
        en = t0 + (g[-1]["end"] - src_in)
        out.append({
            "start": max(0.0, st),
            "end": max(0.0, en),
            "words": [{"t": w["text"], "s": round(t0 + (w["start"] - src_in), 3)}
                      for w in g],
        })
    return out


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def build_html(segs, caps, has_music, music_rel, sfx_cues, title, kicker,
               chips, handle, duration):
    L = []
    a = L.append

    a('<!doctype html>')
    a('<html lang="es">')
    a('<head>')
    a('<meta charset="UTF-8" />')
    a('<meta name="viewport" content="width=%d, height=%d" />' % (W, H))
    a('<title>%s</title>' % esc(title))
    a('<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>')
    a('<style>')
    a(open(os.path.join(PROJ, "style.css"), encoding="utf-8").read())
    a('</style>')
    a('</head>')
    a('<body>')
    a('<div id="root" data-composition-id="main" data-start="0" '
      'data-width="%d" data-height="%d" data-duration="%.3f">' % (W, H, duration))

    # ---------- banda de video ----------
    a('  <div id="band">')
    a('    <div id="band-clip">')
    for i, s in enumerate(segs):
        a('      <video id="v%d" class="clip seg" src="assets/seg_%02d.mp4" '
          'playsinline preload="auto" data-has-audio="true" '
          'data-start="%.3f" data-duration="%.3f" data-track-index="0" '
          'data-volume="1"></video>'
          % (i, i, s["t"], s["out"] - s["in"]))
    a('    </div>')
    a('    <div id="scrim"></div>')
    a('    <div id="chips">')
    for i, c in enumerate(chips):
        a('      <div class="chip-box clip" data-start="%.3f" data-duration="%.3f" '
          'data-track-index="3">' % (c["start"], duration - c["start"]))
        a('        <div class="chip" id="chip%d" style="top:%dpx">' % (i, 48 + i * 74))
        a('          <span class="chip-n">%d</span><span class="chip-t">%s</span>'
          % (i + 1, esc(c["text"])))
        a('        </div>')
        a('      </div>')
    a('    </div>')
    a('  </div>')

    # ---------- titulo ----------
    a('  <div id="head">')
    a('    <div id="kicker"><span id="kicker-in">%s</span></div>' % esc(kicker))
    a('    <h1 id="t1">%s</h1>' % esc(title))
    a('    <div id="rule"><i></i></div>')
    a('  </div>')

    # ---------- captions ----------
    a('  <div id="caps">')
    for i, g in enumerate(caps):
        dur = max(0.45, g["end"] - g["start"] + 0.30)
        a('    <div class="cap clip" data-start="%.3f" data-duration="%.3f" '
          'data-track-index="4">' % (g["start"], dur))
        for w in g["words"]:
            a('      <span class="w" data-s="%.3f">%s</span>' % (w["s"], esc(w["t"])))
        a('    </div>')
    a('  </div>')

    # ---------- HUD ----------
    a('  <div id="hud">')
    a('    <div id="bar"><i id="bar-fill"></i></div>')
    a('    <div id="foot"><span id="handle">%s</span>'
      '<span id="cta">GUARDÁ ESTO</span></div>' % esc(handle))
    a('  </div>')

    # ---------- audio ----------
    if has_music:
        a('  <audio id="music" src="%s" data-start="0" data-duration="%.3f" '
          'data-track-index="8" data-volume="0.16" data-fade-in="0.8" '
          'data-fade-out="2.0"></audio>' % (music_rel, duration))
    for i, (t, f) in enumerate(sfx_cues):
        a('  <audio id="sfx%d" src="assets/sfx/%s" data-start="%.3f" '
          'data-duration="%.3f" data-track-index="9" data-volume="%.2f"></audio>'
          % (i, f, t, 2.0, 0.45))

    a('</div>')

    # ---------- timeline ----------
    a('<script>')
    a('const tl = gsap.timeline({ paused: true });')
    a('const $ = (s) => document.querySelector(s);')
    a('const $$ = (s) => Array.from(document.querySelectorAll(s));')
    a('const DUR = %.3f;' % duration)
    a('')

    # intro
    a('/* ---- intro del titulo ---- */')
    a('tl.fromTo("#kicker-in", { y: 26, opacity: 0 }, '
      '{ y: 0, opacity: 1, duration: 0.45, ease: "power3.out" }, 0.18);')
    a('tl.fromTo("#t1", { y: 60, opacity: 0 }, '
      '{ y: 0, opacity: 1, duration: 0.62, ease: "power3.out" }, 0.30);')
    a('tl.fromTo("#rule i", { scaleX: 0 }, '
      '{ scaleX: 1, duration: 0.70, ease: "power3.inOut" }, 0.62);')
    a('tl.fromTo("#band-clip", { scale: 1.06, opacity: 0 }, '
      '{ scale: 1, opacity: 1, duration: 0.75, ease: "power3.out" }, 0.10);')
    a('tl.fromTo("#caps", { y: 24, opacity: 0 }, '
      '{ y: 0, opacity: 1, duration: 0.5, ease: "power3.out" }, 0.55);')
    a('tl.fromTo("#foot", { opacity: 0 }, { opacity: 1, duration: 0.5 }, 0.8);')

    # barra de progreso
    a('/* ---- barra de progreso ---- */')
    a('tl.fromTo("#bar-fill", { scaleX: 0 }, '
      '{ scaleX: 1, duration: DUR, ease: "none" }, 0);')

    # push-in sutil en cada segmento
    a('')
    a('/* ---- push-in sutil por segmento ---- */')
    for i, s in enumerate(segs):
        dur = s["out"] - s["in"]
        a('tl.fromTo("#v%d", { scale: 1.0 }, { scale: 1.055, duration: %.3f, '
          'ease: "none" }, %.3f);' % (i, dur, s["t"]))

    # chips
    a('')
    a('/* ---- chips numerados ---- */')
    for i, c in enumerate(chips):
        a('tl.fromTo("#chip%d", { x: 46, opacity: 0 }, '
          '{ x: 0, opacity: 1, duration: 0.42, ease: "back.out(1.7)" }, %.3f);'
          % (i, c["start"] + 0.10))

    # captions
    a('')
    a('/* ---- captions karaoke ---- */')
    a('$$(".cap").forEach((cap) => {')
    a('  const ws = Array.from(cap.querySelectorAll(".w"));')
    a('  ws.forEach((w, i) => {')
    a('    const at = parseFloat(w.dataset.s);')
    a('    tl.fromTo(w, { y: 16, opacity: 0 }, '
      '{ y: 0, opacity: 1, duration: 0.16, ease: "power2.out" }, at);')
    a('    tl.set(ws, { className: "w" }, at);')
    a('    tl.set(w, { className: "w act" }, at);')
    a('  });')
    a('});')

    # transiciones de corte: flash breve en cada frontera de segmento
    a('')
    a('/* ---- transiciones entre bloques ---- */')
    a('const flash = document.createElement("div");')
    a('flash.id = "flash";')
    a('document.getElementById("band").appendChild(flash);')
    for i, s in enumerate(segs):
        if i == 0:
            continue
        a('tl.fromTo("#flash", { opacity: 0.85 }, '
          '{ opacity: 0, duration: 0.22, ease: "power2.out" }, %.3f);' % (s["t"] - 0.01))

    a('')
    a('window.__timelines["main"] = tl;')
    a('</script>')
    a('</body>')
    a('</html>')

    html = "\n".join(L)
    with open(os.path.join(PROJ, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
    return html


def main():
    cfg = load_json(os.path.join(PROJ, "segments.json"))
    words = []
    tp = os.path.join(ASSETS, "transcript_full.json")
    if os.path.exists(tp):
        words = load_json(tp)
    print("palabras en el transcript: %d" % len(words))

    # timeline de la composicion: encadenar segmentos con un pequeno solape 0
    segs, t = [], 0.0
    for s in cfg["segments"]:
        seg = dict(s)
        seg["t"] = round(t, 3)
        segs.append(seg)
        t += (s["out"] - s["in"])
    total = round(t, 3)
    duration = float(cfg.get("duration") or total)
    print("duracion total: %.2fs (root %.2fs) en %d segmentos"
          % (total, duration, len(segs)))
    if abs(total - 60.0) > 1.2:
        print("  AVISO: la duracion se aleja de 60s")

    print("extrayendo segmentos...")
    extract_segments(segs)
    copy_audio()

    caps = []
    for s in segs:
        caps.extend(group_captions(words, s["t"], s["in"], s["out"]))
    caps.sort(key=lambda c: c["start"])
    print("grupos de caption: %d" % len(caps))

    # chips: aparecen cuando arranca cada bloque con punto
    chips = []
    for i, s in enumerate(segs):
        if s.get("chip"):
            chips.append({"text": s["chip"], "start": round(s["t"] + 0.35, 3)})

    # sfx: whoosh en cada frontera + pop en cada chip
    sfx = []
    for i, s in enumerate(segs):
        if i == 0:
            continue
        sfx.append((round(s["t"] - 0.05, 3), "whoosh-short.mp3"))
    for c in chips:
        sfx.append((round(c["start"] + 0.05, 3), "pop.mp3"))

    music = os.path.join(ASSETS, "bgm", "track.wav")
    has_music = os.path.exists(music)
    music_rel = "assets/bgm/track.wav" if has_music else ""
    print("musica: %s" % ("si" if has_music else "NO (falta assets/bgm/track.wav)"))

    build_html(segs, caps, has_music, music_rel, sfx,
               cfg["title"], cfg["kicker"], chips, cfg["handle"], duration)
    print("escrito index.html")


if __name__ == "__main__":
    main()
