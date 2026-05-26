"""Audio for Idle Edu Empire — dynamic music rotation + volume control."""
import array
import math
import os as _os
import pygame

SAMPLE_RATE = 44100

_sounds: dict  = {}
_music_ch: "pygame.mixer.Channel | None" = None
_muted         = False
_volume: float = 0.70   # 0.0–1.0 master volume

# Dynamic music state
_music_tracks: list = []   # list of pygame.mixer.Sound (built at init)
_music_idx:    int  = 0
_fade_t:       float = 0.0  # seconds since current track started (for fade-in)

_AUDIO_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                           "assets", "audio")

_FILE_MAP = {
    "click":   "click",
    "buy":     "buy",
    "upgrade": "upgrade",
    "skill":   "skill",
    "error":   "error",
    "event":   "event",
    "collect": "collect",
}


def _load_ogg(name: str) -> "pygame.mixer.Sound | None":
    path = _os.path.join(_AUDIO_DIR, name + ".ogg")
    if _os.path.exists(path):
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            pass
    return None


def pre_init():
    """Call before pygame.init()."""
    pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, 1024)


def init():
    """Call after pygame.init()."""
    global _music_ch
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(SAMPLE_RATE, -16, 1, 1024)
        pygame.mixer.set_num_channels(16)
        _build_sounds()
        _music_ch = pygame.mixer.Channel(0)
        _start_music()
    except Exception:
        pass


# ── Wave helpers ──────────────────────────────────────────────────────────────

def _sine(t: float, freq: float) -> float:
    return math.sin(2 * math.pi * freq * t)


def _note(freq: float, dur: float, vol: float = 0.35) -> array.array:
    n       = int(SAMPLE_RATE * dur)
    atk     = max(1, int(SAMPLE_RATE * min(0.025, dur * 0.15)))
    rel_s   = max(atk, n - int(SAMPLE_RATE * min(0.12, dur * 0.35)))
    buf     = array.array('h')
    for i in range(n):
        t = i / SAMPLE_RATE
        s = _sine(t, freq) + 0.28 * _sine(t, freq * 2) + 0.08 * _sine(t, freq * 3)
        if i < atk:
            env = i / atk
        elif i >= rel_s:
            env = max(0.0, 1.0 - (i - rel_s) / max(1, n - rel_s))
        else:
            env = 1.0
        buf.append(max(-32767, min(32767, int(vol * 32767 * env * s))))
    return buf


def _make(sequence: list, vol: float = 0.35) -> pygame.mixer.Sound:
    buf = array.array('h')
    for freq, dur in sequence:
        buf.extend(_note(freq, dur, vol))
    return pygame.mixer.Sound(buffer=buf)


# ── Sound library ─────────────────────────────────────────────────────────────

def _build_sounds():
    global _sounds
    C4, D4, E4, F4, G4, A4, B4 = 261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88
    C5, D5, E5, G5              = 523.25, 587.33, 659.25, 783.99
    A3, C6                      = 220.00, 1046.50

    proc = {
        "click":       _make([(A4, 0.04)], 0.18),
        "buy":         _make([(E4, 0.07), (G4, 0.07), (C5, 0.14)], 0.32),
        "upgrade":     _make([(G4, 0.07), (C5, 0.07), (E5, 0.18)], 0.34),
        "skill":       _make([(C4, 0.08), (E4, 0.08), (G4, 0.08), (C5, 0.20)], 0.30),
        "diploma":     _make([(G4, 0.08), (C5, 0.08), (E5, 0.08), (G5, 0.22)], 0.36),
        "achievement": _make([(C4, 0.10), (E4, 0.10), (G4, 0.10), (C5, 0.10), (E5, 0.28)], 0.40),
        "prestige":    _make([(C4,0.09),(E4,0.09),(G4,0.09),(C5,0.09),(E5,0.09),(G5,0.30)], 0.42),
        "milestone":   _make([(A4, 0.14), (A4, 0.05), (C5, 0.14), (C5, 0.05), (E5, 0.40)], 0.38),
        "event":       _make([(G4, 0.06), (C5, 0.12)], 0.28),
        "collect":     _make([(C5, 0.07), (E5, 0.07), (G5, 0.16)], 0.32),
        "error":       _make([(D4, 0.07), (B4-100, 0.10)], 0.22),
        "story":       _make([(F4, 0.14), (A4, 0.14), (C5, 0.28)], 0.22),
        "combo":       _make([(440 + 40 * i, 0.03) for i in range(4)], 0.18),
        "honor":       _make([(A3, 0.14), (C4, 0.10), (E4, 0.10), (A4, 0.10),
                               (C5, 0.10), (E5, 0.10), (A4, 0.40)], 0.44),
        "endow":       _make([(C4, 0.08), (E4, 0.08), (G4, 0.08), (C5, 0.08),
                               (E5, 0.08), (G5, 0.08), (C6, 0.36)], 0.48),
        "rare_event":  _make([(E5, 0.06), (G5, 0.06), (E5, 0.04), (G5, 0.18)], 0.36),
        "alumni":      _make([(A3, 0.06), (C4, 0.06), (E4, 0.06), (A4, 0.06),
                               (C5, 0.06), (E5, 0.06), (A4, 0.06), (C6, 0.06),
                               (E5, 0.06), (C6, 0.50)], 0.52),
        "scholar":     _make([(F4, 0.12), (A4, 0.12), (C5, 0.12), (E5, 0.30)], 0.30),
    }

    _sounds = dict(proc)
    for name, fname in _FILE_MAP.items():
        snd = _load_ogg(fname)
        if snd is not None:
            _sounds[name] = snd


# ── Background music — 4 distinct tracks ─────────────────────────────────────

def _build_track(bpm: float, notes: list, vol: float = 0.10) -> pygame.mixer.Sound:
    """Synthesise a music track from (freq_hz, beat_count) note pairs."""
    q   = 60.0 / bpm
    buf = array.array('h')
    for freq, beats in notes:
        dur   = q * beats
        n     = int(SAMPLE_RATE * dur)
        atk   = max(1, int(SAMPLE_RATE * 0.015))
        rel_s = max(atk, n - int(SAMPLE_RATE * min(0.08, dur * 0.28)))
        pi2   = 2 * math.pi
        for i in range(n):
            t   = i / SAMPLE_RATE
            s   = (math.sin(pi2 * freq * t) * 0.76
                   + math.sin(pi2 * freq * 2 * t) * 0.16
                   + math.sin(pi2 * freq * 0.5 * t) * 0.08)
            if i < atk:
                env = i / atk
            elif i >= rel_s:
                env = max(0.0, 1.0 - (i - rel_s) / max(1, n - rel_s))
            else:
                env = 1.0
            buf.append(max(-32767, min(32767, int(vol * 32767 * env * s))))
    return pygame.mixer.Sound(buffer=buf)


# Track note tables  (freq_hz, beat_count)  — all 8-bar loops + tiny tail
_TRACK0 = [  # "School Days"  C major pentatonic, 100 BPM
    (261.63,0.5),(329.63,0.5),(392.00,0.5),(329.63,0.5),
    (261.63,0.75),(293.66,0.25),(329.63,1.0),
    (392.00,0.5),(440.00,0.5),(392.00,0.5),(329.63,0.5),
    (293.66,2.0),
    (329.63,0.5),(392.00,0.5),(440.00,0.5),(392.00,0.5),
    (329.63,0.75),(293.66,0.25),(261.63,1.0),
    (392.00,0.5),(329.63,0.5),(293.66,0.5),(261.63,0.5),
    (261.63,2.0),
    (261.63,0.25),
]
_TRACK1 = [  # "Recess"  G major pentatonic, 112 BPM  — upbeat
    (392.00,0.5),(493.88,0.5),(587.33,0.5),(493.88,0.5),
    (392.00,0.5),(440.00,0.5),(493.88,1.0),
    (587.33,0.5),(659.25,0.5),(587.33,0.5),(493.88,0.5),
    (440.00,2.0),
    (493.88,0.5),(587.33,0.5),(659.25,0.5),(783.99,0.5),
    (659.25,0.5),(587.33,0.5),(493.88,1.0),
    (392.00,0.5),(440.00,0.5),(493.88,0.5),(587.33,0.5),
    (392.00,2.0),
    (392.00,0.25),
]
_TRACK2 = [  # "Study Hall"  F major pentatonic, 85 BPM  — calm
    (349.23,1.0),(440.00,0.5),(523.25,0.5),
    (440.00,0.75),(392.00,0.25),(349.23,2.0),
    (523.25,0.5),(587.33,0.5),(523.25,0.5),(440.00,0.5),
    (392.00,2.0),
    (440.00,0.5),(523.25,0.5),(587.33,0.5),(523.25,0.5),
    (440.00,0.75),(392.00,0.25),(349.23,1.0),
    (392.00,0.5),(440.00,0.5),(392.00,0.5),(349.23,0.5),
    (349.23,2.0),
    (349.23,0.25),
]
_TRACK3 = [  # "Science Lab"  A minor pentatonic, 95 BPM  — curious
    (220.00,0.5),(261.63,0.5),(293.66,0.5),(329.63,0.5),
    (392.00,0.75),(329.63,0.25),(293.66,1.0),
    (261.63,0.5),(293.66,0.5),(329.63,0.5),(392.00,0.5),
    (440.00,2.0),
    (392.00,0.5),(329.63,0.5),(293.66,0.5),(261.63,0.5),
    (293.66,0.5),(329.63,0.5),(392.00,1.0),
    (329.63,0.5),(293.66,0.5),(261.63,0.5),(220.00,0.5),
    (220.00,2.0),
    (220.00,0.25),
]

_TRACK_CONFIGS = [
    (_TRACK0, 100, 0.11),
    (_TRACK1, 112, 0.11),
    (_TRACK2,  85, 0.09),
    (_TRACK3,  95, 0.10),
]


def _start_music():
    global _music_tracks, _music_idx, _fade_t
    try:
        _music_tracks = []
        file_music = _load_ogg("music")
        if file_music is not None:
            _music_tracks.append(file_music)
        # Always generate all 4 procedural tracks
        for notes, bpm, vol in _TRACK_CONFIGS:
            _music_tracks.append(_build_track(bpm, notes, vol))
        _music_idx = 0
        _fade_t    = 0.0
        _music_ch.play(_music_tracks[0], loops=7)  # ~2 min per track before switching
        _music_ch.set_volume(0.0)   # fade in on first tick()
    except Exception:
        pass


# ── Public API ────────────────────────────────────────────────────────────────

def tick(dt: float):
    """Call once per frame to handle track rotation and fade-in."""
    global _music_idx, _fade_t
    if _music_ch is None or not _music_tracks:
        return
    if _muted:
        try:
            _music_ch.set_volume(0.0)
        except Exception:
            pass
        return

    _fade_t = min(_fade_t + dt, 3.0)

    if not _music_ch.get_busy():
        # Current track ended — advance to next
        _music_idx = (_music_idx + 1) % len(_music_tracks)
        _music_ch.play(_music_tracks[_music_idx], loops=7)
        _fade_t = 0.0

    try:
        _music_ch.set_volume(min(1.0, _fade_t / 3.0) * _volume)
    except Exception:
        pass


def play(name: str):
    if _muted or name not in _sounds:
        return
    try:
        ch = pygame.mixer.find_channel(True)
        ch.set_volume(_volume)
        ch.play(_sounds[name])
    except Exception:
        pass


def toggle_mute() -> bool:
    global _muted
    _muted = not _muted
    try:
        if _muted:
            _music_ch.set_volume(0.0)
        else:
            # Restore immediately at current volume (tick() will keep it there)
            _music_ch.set_volume(_volume)
            if not _music_ch.get_busy() and _music_tracks:
                _music_ch.play(_music_tracks[_music_idx], loops=7)
    except Exception:
        pass
    return _muted


def set_volume(v: float):
    global _volume
    _volume = max(0.0, min(1.0, round(v, 2)))
    if not _muted and _music_ch is not None:
        try:
            _music_ch.set_volume(_volume)
        except Exception:
            pass


def get_volume() -> float:
    return _volume


def is_muted() -> bool:
    return _muted
