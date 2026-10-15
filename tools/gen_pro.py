#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Genera video-1/index.html desde cero: anuncio carrito gastronomico.
Lee assets/transcript_full.json y escribe la composicion completa."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.environ.get("HF_PROJ") or os.path.join(HERE, "..", "video-1")
ASSETS = os.path.join(PROJ, "assets")

DUR = 51.8
words = json.load(open(os.path.join(ASSETS, "transcript_full.json"), encoding="utf-8-sig"))

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def cap_groups(words, max_chars=24):
    groups, cur, n = [], [], 0
    for w in words:
        cur.append(w); n += len(w["text"]) + 1
        if n >= max_chars:
            groups.append(cur); cur, n = [], 0
    if cur:
        groups.append(cur)
    out = []
    for g in groups:
        out.append({
            "s": round(g[0]["start"], 3),
            "e": round(g[-1]["end"], 3),
            "words": [{"t": w["text"], "s": round(w["start"], 3)} for w in g],
        })
    return out

caps = cap_groups(words)

# tarjetas de spec: (t, titulo, detalle)
specs = [
    (9.9,  "1.30 × 0.70 × 0.95 m", "medidas ideales"),
    (17.8, "35 × 60 CM",           "plancha profesional"),
    (21.3, "12 LITROS",            "freidora reforzada"),
    (24.3, "BAÑO MARÍA",           "+3 insertos con tapa"),
    (31.1, "TECHO DE LONA",        "super resistente"),
]
PRICE_T = 37.6
CTA_T   = 46.4

L = []
a = L.append
a('<!doctype html>')
a('<html lang="es"><head><meta charset="UTF-8"/>')
a('<title>Carrito PRO — anuncio</title>')
a('<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>')
a('<style>')
a('''*{margin:0;padding:0;box-sizing:border-box}
html,body{width:100%;height:100%;background:#0B0B0E;color:#fff;overflow:hidden;
 font-family:Inter,system-ui,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}
#root{position:relative;width:100%;height:100%;overflow:hidden;
 background:radial-gradient(900px 700px at 50% 12%,#16161d 0%,#0B0B0E 65%)}
.clip{position:absolute;inset:0;overflow:hidden}
/* banda de video */
#band{position:absolute;top:560px;left:0;width:1080px;height:810px;overflow:hidden;
 background:#000;box-shadow:0 30px 80px rgba(0,0,0,.6)}
#band .seg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}
#scrim{position:absolute;left:0;right:0;bottom:0;height:300px;pointer-events:none;
 background:linear-gradient(to top,rgba(8,8,11,.95),rgba(8,8,11,.55) 45%,transparent 100%)}
#vignette{position:absolute;inset:0;pointer-events:none;
 box-shadow:inset 0 0 220px 40px rgba(0,0,0,.55)}
/* titulo */
#head{position:absolute;top:130px;left:0;right:0;padding:0 64px;text-align:center}
#kicker{font-size:30px;font-weight:700;letter-spacing:.3em;color:rgba(255,255,255,.55);
 text-transform:uppercase}
#t1{margin-top:18px;font-size:100px;font-weight:800;line-height:1.03;letter-spacing:-.03em}
#t1 .w{display:inline-block;white-space:pre}
#t1 .acc{color:#FFD84D}
#rule{width:200px;height:8px;margin:24px auto 0;border-radius:99px;
 background:rgba(255,255,255,.12);overflow:hidden}
#rule i{display:block;width:100%;height:100%;background:#FFD84D;transform-origin:left center}
/* tarjetas de spec */
#specs{position:absolute;left:0;top:600px;width:1080px;height:700px;pointer-events:none}
.specbox{position:absolute;left:44px;display:flex;align-items:stretch;
 background:rgba(10,10,14,.82);border:1px solid rgba(255,255,255,.14);
 border-radius:22px;overflow:hidden;box-shadow:0 14px 40px rgba(0,0,0,.5)}
.specbox .bar{width:10px;background:#FFD84D}
.specbox .in{padding:16px 26px}
.specbox .big{font-size:44px;font-weight:800;letter-spacing:-.01em;white-space:nowrap}
.specbox .small{font-size:26px;font-weight:500;color:#FFD84D;white-space:nowrap}
/* precio hero */
#price{position:absolute;left:0;right:0;top:235px;text-align:center}
#priceCard{display:inline-block;padding:30px 70px;border-radius:34px;
 background:#FFD84D;color:#0B0B0E;box-shadow:0 26px 90px rgba(255,216,77,.35);
 transform-origin:center}
#priceNum{font-size:150px;font-weight:900;letter-spacing:-.03em;line-height:1}
#priceSub{font-size:38px;font-weight:800;letter-spacing:.08em;margin-top:6px}
/* captions */
#caps{position:absolute;left:0;right:0;top:1120px;height:220px;pointer-events:none}
.cap{position:absolute;inset:0;display:flex;flex-wrap:wrap;align-content:center;
 justify-content:center;column-gap:16px;row-gap:4px;padding:0 58px;text-align:center}
.w{display:inline-block;font-size:50px;font-weight:800;line-height:1.16;
 letter-spacing:-.015em;color:rgba(255,255,255,.72);
 text-shadow:0 4px 26px rgba(0,0,0,.9)}
.w.act{color:#FFD84D}
/* CTA */
#ctaBox{position:absolute;left:0;right:0;top:250px;text-align:center}
#ctaCard{display:inline-block;padding:26px 64px;border-radius:999px;background:#25D366;
 color:#062b16;box-shadow:0 22px 70px rgba(37,211,102,.4);transform-origin:center}
#ctaTxt{font-size:56px;font-weight:900;letter-spacing:.01em;white-space:nowrap}
#ctaSub{margin-top:26px;font-size:36px;font-weight:700;color:rgba(255,255,255,.85);
 letter-spacing:.06em}
/* hud */
#hud{position:absolute;left:0;right:0;bottom:0;height:120px;padding:0 60px;
 display:flex;flex-direction:column;justify-content:center;gap:18px}
#pbar{height:8px;border-radius:99px;background:rgba(255,255,255,.14);overflow:hidden}
#pfill{display:block;width:100%;height:100%;background:#FFD84D;transform-origin:left center}
#foot{display:flex;justify-content:space-between;align-items:center}
#handle{font-size:29px;font-weight:700;color:rgba(255,255,255,.55)}
#cta2{font-size:26px;font-weight:800;color:#0B0B0E;background:#FFD84D;
 padding:10px 24px;border-radius:99px}
#flash{position:absolute;inset:0;background:#fff;opacity:0;pointer-events:none}''')
a('</style></head><body>')
a('<div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="%.3f">' % DUR)

# video
a('  <div id="band">')
a('    <div id="band-clip">')
a('      <video id="v0" class="clip seg" src="assets/seg_00.mp4" playsinline preload="auto" data-has-audio="true" data-start="0" data-duration="%.3f" data-track-index="0" data-volume="1"></video>' % DUR)
a('    </div><div id="scrim"></div><div id="vignette"></div>')
a('  </div>')

# titulo: palabras separadas para stagger
a('  <div id="head">')
a('    <div id="kicker"><span id="kicker-in">Carrito gastronómico profesional</span></div>')
a('    <h1 id="t1"><span class="w">TU</span> <span class="w">NEGOCIO</span> <span class="w acc">SOBRE</span> <span class="w acc">RUEDAS</span></h1>')
a('    <div id="rule"><i></i></div>')
a('  </div>')

# specs
a('  <div id="specs">')
for i, (t, big, small) in enumerate(specs):
    top = 30 + i * 118
    a('    <div class="specbox clip" id="spec%d" data-start="%.3f" data-duration="%.3f" data-track-index="3" style="top:%dpx">'
      % (i, t, DUR - t, top))
    a('      <div class="bar"></div><div class="in"><div class="big">%s</div><div class="small">%s</div></div>' % (esc(big), esc(small)))
    a('    </div>')
a('  </div>')

# precio
a('  <div id="price" class="clip" data-start="%.3f" data-duration="4.4" data-track-index="5">' % PRICE_T)
a('    <div id="priceCard"><div id="priceNum">$0</div><div id="priceSub">MXN · LISTO PARA FACTURAR</div></div>')
a('  </div>')

# captions
a('  <div id="caps">')
for g in caps:
    dur = max(0.45, g["e"] - g["s"] + 0.32)
    a('    <div class="cap clip" data-start="%.3f" data-duration="%.3f" data-track-index="4">' % (g["s"], dur))
    for w in g["words"]:
        a('      <span class="w" data-s="%.3f">%s</span>' % (w["s"], esc(w["t"])))
    a('    </div>')
a('  </div>')

# CTA
a('  <div id="ctaBox" class="clip" data-start="%.3f" data-duration="%.3f" data-track-index="6">' % (CTA_T, DUR - CTA_T))
a('    <div id="ctaCard"><div id="ctaTxt">COTIZÁ EL TUYO HOY</div></div>')
a('    <div id="ctaSub">👉 Mandanos un WhatsApp</div>')
a('  </div>')

# hud
a('  <div id="hud"><div id="pbar"><i id="pfill"></i></div>')
a('    <div id="foot"><span id="handle">HOT DOGS &amp; BURGERS</span><span id="cta2">GUARDÁ ESTO</span></div></div>')
a('  <div id="flash"></div>')

# audio
a('  <audio id="music" src="assets/bgm/track.wav" data-start="0" data-duration="%.3f" data-track-index="8" data-volume="0.14" data-fade-in="0.8" data-fade-out="2.2"></audio>' % DUR)
for i, (t, big, small) in enumerate(specs):
    a('  <audio id="sfxs%d" src="assets/sfx/whoosh-short.mp3" data-start="%.3f" data-duration="1.0" data-track-index="9" data-volume="0.5"></audio>' % (i, max(0, t - 0.05)))
a('  <audio id="sfxp" src="assets/sfx/pop.mp3" data-start="%.3f" data-duration="0.6" data-track-index="10" data-volume="0.7"></audio>' % (PRICE_T + 0.05))
a('  <audio id="sfxc" src="assets/sfx/whoosh-cinematic.mp3" data-start="%.3f" data-duration="2.0" data-track-index="10" data-volume="0.5"></audio>' % CTA_T)
a('</div>')

# timeline
a('<script>')
a('const tl = gsap.timeline({ paused: true });')
a('const $$ = (s) => Array.from(document.querySelectorAll(s));')
# intro
a('tl.fromTo("#kicker-in",{y:24,opacity:0},{y:0,opacity:1,duration:0.45,ease:"power3.out"},0.15);')
a('tl.fromTo("#t1 .w",{y:70,opacity:0},{y:0,opacity:1,duration:0.55,stagger:0.09,ease:"back.out(1.6)"},0.28);')
a('tl.fromTo("#rule i",{scaleX:0},{scaleX:1,duration:0.7,ease:"power3.inOut"},0.75);')
a('tl.fromTo("#band-clip",{scale:1.07,opacity:0},{scale:1,opacity:1,duration:0.8,ease:"power3.out"},0.1);')
a('tl.fromTo("#foot",{opacity:0},{opacity:1,duration:0.5},0.9);')
# barra progreso
a('tl.fromTo("#pfill",{scaleX:0},{scaleX:1,duration:%.3f,ease:"none"},0);' % DUR)
# push-in continuo del video
a('tl.fromTo("#v0",{scale:1.0},{scale:1.08,duration:%.3f,ease:"none"},0);' % DUR)
# specs: entrada con rebote + micro flash
for i, (t, big, small) in enumerate(specs):
    a('tl.fromTo("#spec%d",{x:-120,opacity:0},{x:0,opacity:1,duration:0.45,ease:"back.out(1.8)"},%.3f);' % (i, t + 0.05))
    a('tl.fromTo("#flash",{opacity:0.35},{opacity:0,duration:0.25,immediateRender:false},%.3f);' % (max(0, t - 0.02),))
# precio: entra, count-up, sale
a('tl.fromTo("#priceCard",{scale:0.3,opacity:0},{scale:1,opacity:1,duration:0.5,ease:"back.out(2.0)"},%.3f);' % (PRICE_T + 0.08))
a('const pc=document.getElementById("priceNum");const cnt={v:0};')
a('tl.to(cnt,{v:13500,duration:1.6,ease:"power2.out",onUpdate:()=>{pc.textContent="$"+Math.round(cnt.v).toLocaleString("es-MX");}},%.3f);' % (PRICE_T + 0.35))
a('tl.to("#priceCard",{scale:1.07,duration:0.35,yoyo:true,repeat:3,ease:"sine.inOut"},%.3f);' % (PRICE_T + 2.0))
a('tl.to("#priceCard",{opacity:0,scale:0.85,duration:0.35,ease:"power2.in"},%.3f);' % (PRICE_T + 3.9))
# cta: entra y pulsa
a('tl.fromTo("#ctaCard",{scale:0.3,opacity:0},{scale:1,opacity:1,duration:0.5,ease:"back.out(2.0)"},%.3f);' % (CTA_T + 0.05))
a('tl.to("#ctaCard",{scale:1.08,duration:0.4,yoyo:true,repeat:7,ease:"sine.inOut"},%.3f);' % (CTA_T + 0.7))
a('tl.fromTo("#ctaSub",{opacity:0,y:20},{opacity:1,y:0,duration:0.5},%.3f);' % (CTA_T + 0.5))
# karaoke
a('$$(".cap").forEach((cap)=>{const ws=Array.from(cap.querySelectorAll(".w"));')
a(' ws.forEach((w)=>{const at=parseFloat(w.dataset.s);')
a('  tl.fromTo(w,{y:16,opacity:0},{y:0,opacity:1,duration:0.16,ease:"power2.out"},at);')
a('  tl.set(ws,{className:"w"},at);')
a('  tl.set(w,{className:"w act"},at);});});')
a('window.__timelines["main"] = tl;')
a('</script></body></html>')

out = os.path.join(PROJ, "index.html")
open(out, "w", encoding="utf-8").write("\n".join(L))
print("index.html OK (%d caps, %.1fs)" % (len(caps), DUR))
