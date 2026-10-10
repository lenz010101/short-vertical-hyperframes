# -*- coding: utf-8 -*-
"""
Musica de fondo original sintetizada con numpy (torch/MusicGen no carga en
esta maquina: c10.dll falla). Bed instrumental moderno y discreto para un
short de negocios: bajo, pad, arpegio con delay, y percusion suave.
"""
import os

import numpy as np
import soundfile as sf

SR = 44100
BPM = 108.0
BEAT = 60.0 / BPM
TARGET = 62.0

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROJ = os.environ.get("HF_PROJ") or os.path.join(ROOT, "video-1")
OUT = os.path.join(PROJ, "assets", "bgm", "track.wav")

rng = np.random.default_rng(20261010)

NOTES = {
    "A2": 110.00, "C3": 130.81, "D3": 146.83, "E3": 164.81, "F3": 174.61,
    "G3": 196.00, "A3": 220.00, "B3": 246.94, "C4": 261.63, "D4": 293.66,
    "E4": 329.63, "F4": 349.23, "G4": 392.00, "A4": 440.00, "C5": 523.25,
    "E5": 659.25, "G5": 783.99,
}

# 4 compases: Am - F - C - G
CHORDS = [
    {"root": "A2", "tones": ["A3", "C4", "E4"], "arp": ["A4", "C5", "E5", "C5"]},
    {"root": "F3", "tones": ["F3", "A3", "C4"], "arp": ["F4", "A4", "C5", "A4"]},
    {"root": "C3", "tones": ["C4", "E4", "G4"], "arp": ["C5", "E5", "G5", "E5"]},
    {"root": "G3", "tones": ["G3", "B3", "D4"], "arp": ["G4", "B3", "D4", "G4"]},
]


def env_ad(n, attack, decay, sr=SR):
    a = max(1, int(attack * sr))
    e = np.ones(n, dtype=np.float32)
    e[:a] = np.linspace(0.0, 1.0, a, dtype=np.float32)
    tail = np.exp(-np.arange(n - a, dtype=np.float32) / (decay * sr))
    e[a:] = tail
    return e


def tone(freq, dur, amp, attack, decay, harmonics=(1.0,), detune=0.0):
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    sig = np.zeros(n, dtype=np.float32)
    for h, w in enumerate(harmonics, start=1):
        for d in ([0.0] if detune == 0 else [-detune, detune]):
            sig += w * np.sin(2 * np.pi * freq * h * (1.0 + d) * t,
                              dtype=np.float32)
    sig *= env_ad(n, attack, decay) * amp
    return sig


def place(buf, sig, at):
    i = int(at * SR)
    j = min(len(buf), i + len(sig))
    if i < 0 or i >= len(buf):
        return
    buf[i:j] += sig[: j - i]


def lowpass(x, cutoff):
    a = np.exp(-2.0 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1.0 - a) * x[i] + a * acc
        y[i] = acc
    return y


def highpass(x, cutoff):
    a = np.exp(-2.0 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    prev_x = 0.0
    prev_y = 0.0
    for i in range(len(x)):
        prev_y = a * (prev_y + x[i] - prev_x)
        prev_x = x[i]
        y[i] = prev_y
    return y


def build_loop():
    bars = len(CHORDS)
    loop_beats = bars * 4
    n = int(loop_beats * BEAT * SR)
    bass = np.zeros(n, dtype=np.float32)
    pad = np.zeros(n, dtype=np.float32)
    arp = np.zeros(n, dtype=np.float32)

    for b, ch in enumerate(CHORDS):
        bar_at = b * 4 * BEAT
        # bajo: una nota por compas, con quinta en el tercer tiempo
        place(bass, tone(NOTES[ch["root"]], 2.6 * BEAT, 0.60, 0.012, 1.1,
                         harmonics=(1.0, 0.30, 0.10)), bar_at)
        place(bass, tone(NOTES[ch["root"]] * 1.5, 1.6 * BEAT, 0.34, 0.012, 0.8,
                         harmonics=(1.0, 0.22)), bar_at + 2 * BEAT)
        # pad: acorde sostenido
        for tname in ch["tones"]:
            place(pad, tone(NOTES[tname], 4.0 * BEAT, 0.13, 0.55, 2.6,
                            harmonics=(1.0, 0.5, 0.22, 0.08), detune=0.004),
                  bar_at)
        # arpegio en corcheas
        for k in range(8):
            name = ch["arp"][k % len(ch["arp"])]
            amp = 0.20 if k % 2 == 0 else 0.13
            place(arp, tone(NOTES[name], 0.9 * BEAT, amp, 0.004, 0.26,
                            harmonics=(1.0, 0.35, 0.12)), bar_at + k * 0.5 * BEAT)
    return bass, pad, arp, n


def build_drums(total_n):
    kick = np.zeros(total_n, dtype=np.float32)
    hat = np.zeros(total_n, dtype=np.float32)
    beat_n = BEAT * SR
    nb = int(total_n / beat_n) + 2
    for b in range(nb):
        at = b * BEAT
        if b % 4 in (0, 2):
            n = int(0.30 * SR)
            t = np.arange(n, dtype=np.float32) / SR
            f = 118.0 * np.exp(-t * 26.0) + 46.0
            ph = 2 * np.pi * np.cumsum(f) / SR
            k = (np.sin(ph) * env_ad(n, 0.002, 0.10) * 0.85).astype(np.float32)
            place(kick, k, at)
        for half in (0.0, 0.5):
            n = int(0.06 * SR)
            noise = rng.normal(0.0, 1.0, n).astype(np.float32)
            h = (highpass(noise, 7000.0) * env_ad(n, 0.001, 0.012)
                 * (0.10 if half == 0.0 else 0.065))
            place(hat, h.astype(np.float32), at + half * BEAT)
    return kick, hat


def delay(x, time_s, feedback, mix, taps=6):
    out = x.copy()
    d = int(time_s * SR)
    for k in range(1, taps + 1):
        g = mix * (feedback ** k)
        if g < 0.01:
            break
        shifted = np.zeros_like(x)
        shifted[k * d:] = x[: len(x) - k * d]
        out += shifted * g
    return out


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    bass, pad, arp, loop_n = build_loop()
    loop_s = loop_n / SR

    total_n = int(TARGET * SR)
    bass_t = np.zeros(total_n, dtype=np.float32)
    pad_t = np.zeros(total_n, dtype=np.float32)
    arp_t = np.zeros(total_n, dtype=np.float32)

    reps = int(np.ceil(total_n / loop_n))
    for r in range(reps):
        at = int(r * loop_n)
        j = min(total_n, at + loop_n)
        bass_t[at:j] += bass[: j - at]
        pad_t[at:j] += pad[: j - at]
        arp_t[at:j] += arp[: j - at]

    kick, hat = build_drums(total_n)

    # El arpegio se abre en estereo con delays distintos.
    arp_d = delay(arp_t, 0.75 * BEAT, 0.42, 0.30)
    pad_t = lowpass(pad_t, 2600.0)
    arp_d = lowpass(arp_d, 5200.0)
    bass_t = lowpass(bass_t, 320.0)

    left = bass_t + pad_t * 0.9 + arp_t * 0.85 + arp_d * 0.35 + kick + hat * 0.9
    right = bass_t + pad_t * 0.9 + arp_t * 0.85 * 0.6 + arp_d * 0.55 + kick + hat

    # Limita picos y aplica fades globales.
    peak = max(float(np.max(np.abs(left))), float(np.max(np.abs(right)))) or 1.0
    left = np.tanh(left / peak * 1.25) * 0.62
    right = np.tanh(right / peak * 1.25) * 0.62

    fade_in = int(2.0 * SR)
    fade_out = int(3.5 * SR)
    ramp_in = np.linspace(0.0, 1.0, fade_in, dtype=np.float32)[:, None]
    ramp_out = np.linspace(1.0, 0.0, fade_out, dtype=np.float32)[:, None]
    stereo = np.stack([left, right], axis=1)
    stereo[:fade_in] *= ramp_in
    stereo[-fade_out:] *= ramp_out

    # Pausa musical en el arranque para no tapar la primera frase.
    stereo[: int(0.6 * SR)] *= np.linspace(0.0, 1.0, int(0.6 * SR),
                                           dtype=np.float32)[:, None]

    sf.write(OUT, stereo, SR)
    print("OK -> %s (%.1fs, loop %.2fs)" % (OUT, len(stereo) / SR, loop_s))


if __name__ == "__main__":
    main()
