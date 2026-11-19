"""Erzeugt die Tonspur (Musikbett + Sound-Effekte) synchron zu den Events aus out/sfx.json.
Alles synthetisch erzeugt -> keine Lizenzfragen.  Aufruf: python3 audio.py
"""
import json, wave, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100
rng = np.random.default_rng(7)
ev = json.load(open(os.path.join(HERE, "out", "sfx.json")))
T = ev["DURATION"]
N = int(T * SR)
music = np.zeros(N)
fx = np.zeros(N)


def add(buf, t, sig):
    i = int(t * SR)
    if i >= len(buf):
        return
    sig = sig[: len(buf) - i]
    buf[i : i + len(sig)] += sig


def tt(d):
    return np.arange(int(d * SR)) / SR


def bell(f0=1046.5):
    t = tt(2.2)
    s = sum(a * np.sin(2 * np.pi * f0 * r * t) * np.exp(-t * dcy)
            for r, a, dcy in [(1, 1, 2.2), (2.0, .5, 3), (2.76, .35, 4), (5.4, .2, 6), (8.9, .1, 9)])
    return 0.32 * s * np.minimum(1, t / 0.003)


def pop():
    t = tt(0.09)
    f = 700 * np.exp(-t * 25) + 220
    return 0.28 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40)


def whoosh():
    t = tt(0.6)
    n = rng.standard_normal(len(t))
    out = np.zeros_like(n); y = 0
    cut = 0.02 + 0.25 * np.sin(np.pi * t / 0.6) ** 2
    for i, x in enumerate(n):
        y += cut[i] * (x - y); out[i] = y
    return 0.5 * out * np.sin(np.pi * t / 0.6) ** 2


def crackle(d):
    s = np.zeros(int(d * SR))
    for _ in range(int(d * 45)):
        i = rng.integers(0, len(s) - 400)
        L = rng.integers(60, 380)
        s[i:i + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 4)) * rng.uniform(.1, .35)
    return s


def notify():
    t = tt(0.18)
    a = np.sin(2 * np.pi * 1318 * t) * np.exp(-t * 18)
    b = np.sin(2 * np.pi * 1760 * t) * np.exp(-t * 14)
    s = np.zeros(int(0.32 * SR)); s[:len(a)] += a; s[int(.13 * SR):int(.13 * SR) + len(b)] += b
    return 0.25 * s


def slurp():
    t = tt(0.35)
    f = 180 + 500 * t / 0.35
    return 0.18 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.35) * (1 + 0.5 * np.sin(2 * np.pi * 28 * t))


GEN = {"bell": bell, "pop": pop, "whoosh": whoosh, "notify": notify, "slurp": slurp}
for e in ev["SFX"]:
    sig = crackle(e["d"]) if e["type"] == "crackle" else GEN[e["type"]]()
    add(fx, max(0, e["t"]), sig)

# ---- Musikbett: 100 BPM, C – Am – F – G, Pluck-Arpeggio + weiche Kick ----
BPM = 100; beat = 60 / BPM
chords = [[60, 64, 67, 72], [57, 60, 64, 69], [53, 57, 60, 65], [55, 59, 62, 67]]
hz = lambda m: 440 * 2 ** ((m - 69) / 12)


def pluck(f, d=0.5):
    t = tt(d)
    return (np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t)) * np.exp(-t * 6) * np.minimum(1, t / .004)


def kick():
    t = tt(0.3)
    f = 50 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 12)


def pad(notes, d):
    t = tt(d)
    s = sum(np.sin(2 * np.pi * hz(m - 12) * t) for m in notes[:3])
    return s * np.minimum(1, t / .4) * np.minimum(1, (d - t) / .4)


bar = 4 * beat
nb = int(T / bar) + 1
for b in range(nb):
    ch = chords[b % 4]; t0 = b * bar
    add(music, t0, 0.05 * pad(ch, bar))
    for k in range(8):
        add(music, t0 + k * beat / 2, 0.07 * pluck(hz(ch[[0, 1, 2, 3, 2, 1, 2, 3][k]] + 12)))
    if t0 > 5.3:  # Beat setzt nach dem Hook ein
        for k in range(4):
            add(music, t0 + k * beat, 0.22 * kick())

fade = np.ones(N); fl = int(2.5 * SR); fade[-fl:] = np.linspace(1, 0, fl)
mix = music * fade + fx
mix /= np.max(np.abs(mix)) / 0.89
stereo = np.stack([mix, mix], 1)
pcm = (stereo * 32767).astype(np.int16)
with wave.open(os.path.join(HERE, "out", "audio.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("audio.wav geschrieben,", round(T, 1), "s")
