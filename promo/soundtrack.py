"""Generates soundtrack.wav for the promo: an original 120 BPM synth bed plus
sound effects timed to the animation in promo.html (same timeline for 16:9 and 9:16).

    python3 soundtrack.py            # needs numpy only
"""
import wave, os
import numpy as np

SR = 48000
DUR = 30.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)
BEAT = 0.5  # 120 BPM


def t_(d):
    return np.arange(int(d * SR)) / SR


def add(sig, at, gain=1.0, pan=0.0):
    """Mix mono sig at time `at` (s); pan -1..1."""
    i = int(at * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    L[i:i + len(sig)] += sig * np.sqrt((1 - pan) / 2) * 1.414
    R[i:i + len(sig)] += sig * np.sqrt((1 + pan) / 2) * 1.414


def fft_filter(x, lo=None, hi=None):
    """Band-limit with a smooth spectral mask (lo/hi in Hz)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.ones_like(f)
    if hi:
        m *= 1 / (1 + (f / hi) ** 4)
    if lo:
        m *= 1 / (1 + (lo / np.maximum(f, 1e-3)) ** 4)
    return np.fft.irfft(X * m, len(x))


def onepole_sweep(x, f0, f1):
    """Low-pass whose cutoff glides from f0 to f1 (for whooshes / risers)."""
    fc = np.geomspace(f0, f1, len(x))
    a = 1 - np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x); s = 0.0
    for i in range(len(x)):
        s += a[i] * (x[i] - s); y[i] = s
    return y


def env_ad(n, a, d_curve):
    a_n = max(1, int(a * SR))
    e = np.ones(n)
    e[:a_n] = np.linspace(0, 1, a_n)
    e[a_n:] = np.exp(-np.arange(n - a_n) / (d_curve * SR))
    return e


def saw(freq, d, detune=(0,)):
    t = t_(d)
    return sum(2 * ((t * freq * (1 + c)) % 1) - 1 for c in detune) / len(detune)


def midi(n):
    return 440 * 2 ** ((n - 69) / 12)


# ---------------- instruments
def kick(g=1.0):
    t = t_(0.45)
    f = 45 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7.5) * g


def clap():
    n = rng.standard_normal(int(0.25 * SR))
    n = fft_filter(n, 900, 4000)
    e = env_ad(len(n), 0.002, 0.06)
    return n * e * 0.9


def hat(open_=False):
    n = rng.standard_normal(int((0.18 if open_ else 0.06) * SR))
    n = fft_filter(n, 7000, None)
    return n * env_ad(len(n), 0.001, 0.05 if open_ else 0.012) * 0.35


def bass_note(note, d):
    x = saw(midi(note), d, (0, 0.004))
    x = fft_filter(x, None, 380)
    return x * env_ad(len(x), 0.005, d * 0.9) * 0.55


def pluck(note, d=0.22):
    t = t_(d)
    x = (np.sin(2 * np.pi * midi(note) * t) + 0.35 * np.sin(4 * np.pi * midi(note) * t))
    return x * env_ad(len(x), 0.002, 0.07) * 0.22


def pad(notes, d):
    x = sum(saw(midi(n), d, (-0.006, 0, 0.007)) for n in notes) / len(notes)
    x = fft_filter(x, 120, 1600)
    e = np.minimum(1, t_(d) / 0.6) * np.minimum(1, (d - t_(d)) / 0.5)
    return x * e * 0.33


# chords per 2 bars (4 s): Am F C G
CHORDS = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
ROOTS = [45, 41, 36, 43]


def chord_at(t):
    k = int(t // 4) % 4
    return CHORDS[k], ROOTS[k]

# ---------------- music
# pad all the way (louder in hook / outro)
for k in range(8):
    ch, _ = chord_at(k * 4)
    start = k * 4
    g = 1.4 if start < 3 else (0.9 if start >= 26 else 0.6)
    add(pad(ch, 4.4), start, g, 0)

# drums + bass + arp in the main sections
def in_groove(t):
    return (3.0 <= t < 26.0)

beats = np.arange(0, DUR, BEAT)
for b in beats:
    if not in_groove(b):
        continue
    demo = 6.9 <= b < 20.5
    lvl = 0.75 if demo else 1.0
    add(kick(), b, 0.95 * lvl)
    beat_idx = int(round(b / BEAT))
    if beat_idx % 2 == 1:
        add(clap(), b, 0.55 * lvl, 0.1)
    add(hat(), b + BEAT / 2, 0.8 * lvl, 0.35)
    add(hat(), b + BEAT / 4, 0.35 * lvl, -0.35)
    add(hat(), b + 3 * BEAT / 4, 0.35 * lvl, -0.35)
    ch, root = chord_at(b)
    add(bass_note(root, 0.24), b, 0.9 * lvl)
    add(bass_note(root + 12 if beat_idx % 4 == 3 else root, 0.22), b + 0.25, 0.7 * lvl)

# 16th-note arp (quiet in hook, brighter in pipeline)
for i, s in enumerate(np.arange(0.0, 28.5, 0.125)):
    ch, _ = chord_at(s)
    note = ch[[0, 1, 2, 1][i % 4]] + 12 + (12 if (i // 8) % 2 and s >= 21 else 0)
    g = 0.6 if s < 3 else (0.55 if 6.9 <= s < 20.5 else 0.9)
    if s >= 26:
        g = 0.45
    add(pluck(note), s, g, -0.4 if i % 2 else 0.4)

# ---------------- SFX
def click():
    t = t_(0.05)
    return (np.sin(2 * np.pi * 2300 * t) * np.exp(-t * 160) + rng.standard_normal(len(t)) * np.exp(-t * 400) * 0.6) * 0.8


def key_tick():
    n = rng.standard_normal(int(0.03 * SR))
    n = fft_filter(n, 1800 + rng.uniform(0, 1500), 9000)
    return n * env_ad(len(n), 0.0005, 0.006) * 0.55


def blip(f0, f1, d=0.12):
    t = t_(d)
    f = np.geomspace(f0, f1, len(t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(len(t), 0.003, d * 0.35) * 0.5


def whoosh(d=0.7, f0=300, f1=6000, up=True):
    n = rng.standard_normal(int(d * SR))
    y = onepole_sweep(n, f0, f1) if up else onepole_sweep(n, f1, f0)
    t = t_(d)
    e = np.sin(np.pi * t / d) ** 2
    return y * e * 0.9


def riser(d=1.0):
    t = t_(d)
    n = onepole_sweep(rng.standard_normal(len(t)), 200, 9000) * (t / d) ** 2
    tone = np.sin(2 * np.pi * np.cumsum(np.geomspace(220, 880, len(t))) / SR) * (t / d) ** 3 * 0.25
    return (n * 0.8 + tone)


def impact():
    t = t_(1.6)
    sub = np.sin(2 * np.pi * np.cumsum(38 + 80 * np.exp(-t * 12)) / SR) * np.exp(-t * 2.5)
    n = fft_filter(rng.standard_normal(len(t)), 80, 3000) * np.exp(-t * 6) * 0.5
    return (sub + n) * 1.1


def chime(notes, d=1.6):
    t = t_(d)
    x = sum(np.sin(2 * np.pi * midi(n) * t) * np.exp(-t * (2.5 + i)) + 0.3 * np.sin(2 * np.pi * midi(n) * 2.01 * t) * np.exp(-t * 6)
            for i, n in enumerate(notes))
    return x * env_ad(len(t), 0.004, 10) / len(notes) * 0.6


def pop(f):
    t = t_(0.14)
    return np.sin(2 * np.pi * np.cumsum(f * (1 + 0.6 * np.exp(-t * 40))) / SR) * np.exp(-t * 28) * 0.55


def hit():
    k, c = kick(1.0), clap()
    k[:len(c)] += c * 0.8
    return k


# hook: soft ticks per word (9 words)
for i in range(9):
    add(pop(1100 + i * 40), 0.15 + i * 0.16, 0.35, (i - 4) / 6)
add(riser(1.0), 2.0, 0.7)
add(impact(), 3.0, 0.9)
add(chime([69, 72, 76, 81]), 3.6, 0.5)            # logo letters
add(whoosh(0.8, 400, 5000), 6.2, 0.45, -0.3)       # pad to corner / window in
add(whoosh(0.6, 500, 4000), 6.9, 0.35, 0.3)
add(click(), 10.85, 0.9)                           # A press
add(blip(660, 990), 12.2, 0.6)                      # dictation on
for i in range(48):                                 # typing
    add(key_tick(), 12.8 + (i + 0.5) * 3.0 / 49 + rng.uniform(-0.01, 0.01), 0.5, rng.uniform(-0.3, 0.3))
add(blip(990, 660), 15.9, 0.5)                      # dictation off
add(click(), 16.35, 0.8)                            # send
add(whoosh(0.5, 800, 7000), 16.35, 0.45)
for i in range(5):                                  # reply lines
    add(pop(700 + i * 90), 17.3 + i * 0.45, 0.35, 0.2)
add(chime([72, 76, 79, 84], 1.8), 19.55, 0.6)        # tests passed
add(whoosh(0.9, 300, 6000), 20.3, 0.5)              # window out
for i, n in enumerate([60, 64, 67, 72, 76]):        # pipeline nodes
    add(pop(midi(n + 12)), 21.6 + i * 0.45, 0.45, (i - 2) / 3)
add(riser(1.2), 24.8, 0.55)
for i in range(4):                                  # slogan words
    add(hit(), 26.0 + i * 0.32, 0.8 if i < 3 else 1.0)
add(impact(), 26.96, 0.6)
add(chime([69, 76, 81, 84, 88], 2.2), 28.2, 0.7)   # CTA

# ---------------- master
mix = np.stack([L, R], 1)
mix = np.tanh(mix * 0.9)
fade = np.ones(N)
fs, fe = int(29.3 * SR), N
fade[fs:fe] = np.linspace(1, 0, fe - fs) ** 1.5
mix *= fade[:, None]
fi = int(0.02 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
mix /= np.max(np.abs(mix)) / 0.89

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'soundtrack.wav')
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('wrote', out)
