"""Procedural audio for Idle Edu Empire — no external files needed."""
import array
import math
import pygame

SAMPLE_RATE = 44100
_sounds: dict = {}
_music_ch: pygame.mixer.Channel | None = None
_muted = False


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
        pass   # audio hardware unavailable — run silent


# ── Wave helpers ──────────────────────────────────────────────────────────────

def _sine(t: float, freq: float) -> float:
    return math.sin(2 * math.pi * freq * t)


def _note(freq: float, dur: float, vol: float = 0.35) -> array.array:
    """Generate one note as 16-bit mono samples."""
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


def _make(sequence: list[tuple[float, float]], vol: float = 0.35) -> pygame.mixer.Sound:
    """Build a Sound from a sequence of (freq_hz, duration_s) tuples."""
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

    _sounds = {
        # UI click — soft tap
        "click":       _make([(A4, 0.04)], 0.18),
        # Buy building — ascending two-note chime
        "buy":         _make([(E4, 0.07), (G4, 0.07), (C5, 0.14)], 0.32),
        # Buy upgrade — slightly higher
        "upgrade":     _make([(G4, 0.07), (C5, 0.07), (E5, 0.18)], 0.34),
        # Buy skill — warm three-note
        "skill":       _make([(C4, 0.08), (E4, 0.08), (G4, 0.08), (C5, 0.20)], 0.30),
        # Diploma shop purchase — triumphant
        "diploma":     _make([(G4, 0.08), (C5, 0.08), (E5, 0.08), (G5, 0.22)], 0.36),
        # Achievement — four-note fanfare
        "achievement": _make([(C4, 0.10), (E4, 0.10), (G4, 0.10), (C5, 0.10), (E5, 0.28)], 0.40),
        # Prestige / Graduate — full ascending arpeggio
        "prestige":    _make([(C4,0.09),(E4,0.09),(G4,0.09),(C5,0.09),(E5,0.09),(G5,0.30)], 0.42),
        # Milestone — bell-like double ring
        "milestone":   _make([(A4, 0.14), (A4, 0.05), (C5, 0.14), (C5, 0.05),
                               (E5, 0.40)], 0.38),
        # Random event spawns — notification ping
        "event":       _make([(G4, 0.06), (C5, 0.12)], 0.28),
        # Event collected — happy resolve
        "collect":     _make([(C5, 0.07), (E5, 0.07), (G5, 0.16)], 0.32),
        # Can't afford / error — low descending
        "error":       _make([(D4, 0.07), (B4-100, 0.10)], 0.22),
        # Story chapter unlocks — soft ambient chime
        "story":       _make([(F4, 0.14), (A4, 0.14), (C5, 0.28)], 0.22),
        # Combo tick (played each level) — rising bleep
        "combo":       _make([(440 + 40 * i, 0.03) for i in range(4)], 0.18),
        # Honors conversion — grand ceremony toll
        "honor":       _make([(A3, 0.14), (C4, 0.10), (E4, 0.10), (A4, 0.10),
                               (C5, 0.10), (E5, 0.10), (A4, 0.40)], 0.44),
        # Endowments conversion — epic multi-octave fanfare
        "endow":       _make([(C4, 0.08), (E4, 0.08), (G4, 0.08), (C5, 0.08),
                               (E5, 0.08), (G5, 0.08), (C6, 0.36)], 0.48),
        # Rare event spawn — distinctive two-tone ping with shimmer
        "rare_event":  _make([(E5, 0.06), (G5, 0.06), (E5, 0.04), (G5, 0.18)], 0.36),
        # Alumni Network conversion — ultimate layered fanfare
        "alumni":      _make([(A3, 0.06), (C4, 0.06), (E4, 0.06), (A4, 0.06),
                               (C5, 0.06), (E5, 0.06), (A4, 0.06), (C6, 0.06),
                               (E5, 0.06), (C6, 0.50)], 0.52),
        # Scholar hire — warm scholarly chord
        "scholar":     _make([(F4, 0.12), (A4, 0.12), (C5, 0.12), (E5, 0.30)], 0.30),
    }


# ── Background music ──────────────────────────────────────────────────────────

def _build_music() -> pygame.mixer.Sound:
    """Generate a looping 8-bar school-theme melody (pentatonic, ~100 BPM)."""
    C3 = 130.81
    C4, D4, E4, G4, A4 = 261.63, 293.66, 329.63, 392.00, 440.00
    C5, D5, E5, G5      = 523.25, 587.33, 659.25, 783.99

    bpm  = 100
    q    = 60 / bpm         # quarter note
    h    = q * 2
    e    = q * 0.5
    de   = q * 0.75

    # Simple pentatonic melody with a bass accompaniment
    melody = [
        # Bar 1
        (C4, e), (E4, e), (G4, e), (E4, e),
        # Bar 2
        (C4, de),(D4, e/2),(E4, q),
        # Bar 3
        (G4, e), (A4, e), (G4, e), (E4, e),
        # Bar 4
        (D4, h),
        # Bar 5
        (E4, e), (G4, e), (A4, e), (G4, e),
        # Bar 6
        (E4, de),(D4, e/2),(C4, q),
        # Bar 7
        (G4, e), (E4, e), (D4, e), (C4, e),
        # Bar 8
        (C4, h),
        # small rest before loop
        (C4, e/4),
    ]

    buf = array.array('h')
    for freq, dur in melody:
        n     = int(SAMPLE_RATE * dur)
        atk   = max(1, int(SAMPLE_RATE * 0.015))
        rel_s = max(atk, n - int(SAMPLE_RATE * min(0.08, dur * 0.3)))
        for i in range(n):
            t = i / SAMPLE_RATE
            # Melody: sine + slight overtone
            s = _sine(t, freq) * 0.75 + _sine(t, freq * 2) * 0.18
            # Subtle bass (octave below, quieter)
            s += _sine(t, freq * 0.5) * 0.07
            if i < atk:
                env = i / atk
            elif i >= rel_s:
                env = max(0.0, 1.0 - (i - rel_s) / max(1, n - rel_s))
            else:
                env = 1.0
            val = int(0.11 * 32767 * env * s)
            buf.append(max(-32767, min(32767, val)))

    return pygame.mixer.Sound(buffer=buf)


def _start_music():
    try:
        music = _build_music()
        _music_ch.play(music, loops=-1)
    except Exception:
        pass


# ── Public API ────────────────────────────────────────────────────────────────

def play(name: str):
    if _muted or name not in _sounds:
        return
    try:
        # Use channels 1-15 for SFX (channel 0 is reserved for music)
        pygame.mixer.find_channel(True).play(_sounds[name])
    except Exception:
        pass


def toggle_mute() -> bool:
    global _muted
    _muted = not _muted
    try:
        if _muted:
            _music_ch.pause()
        else:
            _music_ch.unpause()
    except Exception:
        pass
    return _muted


def is_muted() -> bool:
    return _muted
