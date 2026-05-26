"""Pixel-art animated decorations for Idle Edu Empire."""
import os as _os
import pygame
import math
import random

_ASSETS_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "assets")

# Mirror layout constants from main.py
LEFT_W   = 340
TOP_H    = 72
H        = 760
W        = 1280
TICKER_H = 28

_SKIN    = (220, 185, 145)
_HAIR    = (80,  50,  30)
_BLUE    = (65, 124, 175)
_RED     = (180,  60,  60)
_PANTS   = (50,  50, 110)
_SHOES   = (35,  35,  35)
_GOLD    = (218, 165,  30)
_DARK    = (35,  35,  35)
_TEACHER = (160, 120,  40)
_YELLOW  = (240, 210,  40)
_BUS_WIN = (190, 230, 255)


_CHAR_DIR = _os.path.join(_ASSETS_DIR, "characters")
_CHAR_SCALE = 0.30   # 96×128 → ~29×38 px


class ToonWalker:
    """Animated Toon Character walker using Kenney PNG walk frames."""

    _cache: dict = {}   # char_name → (frames_right, frames_left)

    @classmethod
    def _load(cls, char: str) -> tuple:
        if char in cls._cache:
            return cls._cache[char]
        folder = _os.path.join(_CHAR_DIR, char)
        frames_r = []
        for i in range(8):
            path = _os.path.join(folder, f"walk{i}.png")
            if _os.path.exists(path):
                raw = pygame.image.load(path).convert_alpha()
                w = int(raw.get_width()  * _CHAR_SCALE)
                h = int(raw.get_height() * _CHAR_SCALE)
                frames_r.append(pygame.transform.smoothscale(raw, (w, h)))
        frames_l = [pygame.transform.flip(f, True, False) for f in frames_r]
        cls._cache[char] = (frames_r, frames_l)
        return frames_r, frames_l

    def __init__(self, y: int, char: str, speed_range=(20, 38)):
        self.x     = float(random.randint(20, LEFT_W - 20))
        self.y     = float(y)
        self.dir   = random.choice([-1, 1])
        self.speed = random.uniform(*speed_range)
        self.t     = random.uniform(0, 8.0)
        self._char = char
        self._fr, self._fl = self.__class__._load(char)
        self._w    = self._fr[0].get_width() if self._fr else 29
        self._h    = self._fr[0].get_height() if self._fr else 38

    def update(self, dt: float):
        self.x += self.dir * self.speed * dt
        self.t += dt * 8.0
        if self.x >= LEFT_W - 14:
            self.dir = -1
        elif self.x <= 14:
            self.dir = 1

    def steer_toward(self, target_x: float):
        """Redirect toward target_x when it's clearly on the other side."""
        if target_x < self.x - 18:
            self.dir = -1
        elif target_x > self.x + 18:
            self.dir = 1

    def draw(self, surf: pygame.Surface):
        frames = self._fr if self.dir > 0 else self._fl
        if not frames:
            return
        frame = frames[int(self.t) % len(frames)]
        surf.blit(frame, (int(self.x) - self._w // 2, int(self.y) - self._h))


class WalkingPerson:
    """Stick-figure person that walks back and forth across the left panel."""

    def __init__(self, y: int, shirt=_BLUE):
        self.x     = float(random.randint(20, LEFT_W - 20))
        self.y     = float(y)
        self.shirt = shirt
        self.speed = random.uniform(20, 38)
        self.dir   = random.choice([-1, 1])
        self.t     = random.uniform(0, math.pi * 2)

    def update(self, dt: float):
        self.x += self.dir * self.speed * dt
        self.t += dt * 5
        if self.x >= LEFT_W - 14:
            self.dir = -1
        elif self.x <= 14:
            self.dir = 1

    def draw(self, surf: pygame.Surface):
        x, y = int(self.x), int(self.y)
        walk = math.sin(self.t)
        pygame.draw.circle(surf, _SKIN, (x, y - 13), 5)
        pygame.draw.arc(surf, _HAIR,
                        pygame.Rect(x - 5, y - 18, 10, 8), 0, math.pi, 3)
        pygame.draw.rect(surf, self.shirt, (x - 4, y - 7, 8, 9))
        arm = int(walk * 4)
        pygame.draw.line(surf, _SKIN, (x - 4, y - 6), (x - 8, y - 2 + arm), 2)
        pygame.draw.line(surf, _SKIN, (x + 4, y - 6), (x + 8, y - 2 - arm), 2)
        leg = int(walk * 5)
        pygame.draw.line(surf, _PANTS, (x - 2, y + 2), (x - 3 + leg, y + 10), 2)
        pygame.draw.line(surf, _PANTS, (x + 2, y + 2), (x + 3 - leg, y + 10), 2)
        pygame.draw.circle(surf, _SHOES, (x - 3 + leg, y + 11), 2)
        pygame.draw.circle(surf, _SHOES, (x + 3 - leg, y + 11), 2)


class TeacherCharacter(WalkingPerson):
    """Teacher with a brown shirt who holds a pointer when facing right."""

    def __init__(self, y: int):
        super().__init__(y, shirt=_TEACHER)
        self.speed = random.uniform(14, 22)

    def draw(self, surf: pygame.Surface):
        super().draw(surf)
        x, y = int(self.x), int(self.y)
        # pointer stick extending from hand
        tip_x = x + self.dir * 18
        pygame.draw.line(surf, _DARK, (x + self.dir * 8, y - 4), (tip_x, y - 10), 2)
        pygame.draw.circle(surf, _RED, (tip_x, y - 10), 2)


class MovingCloud:
    """Soft white blob that drifts slowly across the sky area."""

    def __init__(self, y_base: int, speed: float):
        self.y_base = float(y_base)
        self.speed  = speed
        self._reset(initial=True)

    def _reset(self, initial: bool = False):
        self.x = float(random.randint(0, LEFT_W) if initial else -60)
        self.y = self.y_base + random.uniform(-8, 8)
        self.w = random.randint(38, 60)
        self.h = random.randint(14, 22)

    def update(self, dt: float):
        self.x += self.speed * dt
        if self.x > LEFT_W + 70:
            self._reset()

    def draw(self, surf: pygame.Surface):
        x, y, w, h = int(self.x), int(self.y), self.w, self.h
        col = (240, 240, 245)
        pygame.draw.ellipse(surf, col, (x,          y,          w,     h))
        pygame.draw.ellipse(surf, col, (x + w // 4, y - h // 2, w // 2, h))
        pygame.draw.ellipse(surf, col, (x + w // 2, y - h // 3, w // 3, h - 4))


class SchoolBus:
    """School bus that drives across Zone 1 — front-facing right, direction of travel."""

    _BW = 102   # bus width
    _BH = 28    # bus body height

    def __init__(self):
        self._bus_timer = random.uniform(25, 60)
        self.active     = False
        self.x          = float(-self._BW - 10)
        self.y          = float(TOP_H + 316)
        self._t         = 0.0

    def update(self, dt: float):
        if not self.active:
            self._bus_timer -= dt
            if self._bus_timer <= 0:
                self.active = True
                self.x      = float(-self._BW - 10)
            return
        self._t += dt
        self.x  += 72.0 * dt
        if self.x > LEFT_W + 10:
            self.active     = False
            self._bus_timer = random.uniform(40, 90)

    def draw(self, surf: pygame.Surface):
        if not self.active:
            return
        x, y = int(self.x), int(self.y)
        bw, bh = self._BW, self._BH

        # ── Main body ──────────────────────────────────────────────
        pygame.draw.rect(surf, _YELLOW,         (x,      y - bh, bw,  bh), border_radius=3)
        pygame.draw.rect(surf, (165, 128, 10),  (x,      y - bh, bw,  bh), 2,  border_radius=3)

        # ── Black belt stripe along middle ─────────────────────────
        pygame.draw.rect(surf, (25, 25, 25), (x + 2, y - bh//2 - 1, bw - 24, 3))

        # ── Passenger windows (4) ──────────────────────────────────
        for i in range(4):
            wx = x + 4 + i * 19
            pygame.draw.rect(surf, _BUS_WIN,       (wx, y - bh + 3, 14, 15), border_radius=2)
            pygame.draw.rect(surf, (145, 198, 230), (wx, y - bh + 3, 14, 15), 1, border_radius=2)
            pygame.draw.line(surf, (220, 248, 255),
                             (wx + 2, y - bh + 4), (wx + 2, y - bh + 14), 1)

        # ── Front cab (right side — direction of travel) ───────────
        pygame.draw.rect(surf, (215, 175, 18), (x + bw - 24, y - bh, 24, bh), border_radius=3)
        pygame.draw.rect(surf, (165, 128, 10), (x + bw - 24, y - bh, 24, bh), 2, border_radius=3)

        # Windshield
        pygame.draw.rect(surf, _BUS_WIN,        (x + bw - 22, y - bh + 2, 17, 16), border_radius=2)
        pygame.draw.rect(surf, (145, 198, 230),  (x + bw - 22, y - bh + 2, 17, 16), 1, border_radius=2)
        pygame.draw.line(surf, (220, 248, 255),
                         (x + bw - 20, y - bh + 3), (x + bw - 20, y - bh + 16), 1)

        # Headlight
        pygame.draw.ellipse(surf, (255, 248, 160), (x + bw - 8,  y - 8, 10, 6))
        pygame.draw.ellipse(surf, (255, 220, 60),  (x + bw - 8,  y - 8, 10, 6), 1)

        # Front bumper
        pygame.draw.rect(surf, (85, 85, 95), (x + bw - 2, y - 10, 5, 8), border_radius=1)

        # ── Rear details ───────────────────────────────────────────
        # Rear lights (red taillights)
        pygame.draw.rect(surf, (210, 40, 40), (x, y - bh + 4, 4, 6), border_radius=1)
        # Exhaust pipe
        pygame.draw.rect(surf, (72, 72, 78), (x - 5, y - 6, 7, 3), border_radius=1)
        # Rear bumper
        pygame.draw.rect(surf, (85, 85, 95), (x - 5, y - 10, 5, 8), border_radius=1)

        # ── Stop sign (small, on side) ─────────────────────────────
        _ss_x = x + bw - 26
        pygame.draw.rect(surf, (210, 30, 30), (_ss_x, y - bh - 6, 8, 8), border_radius=1)
        pygame.draw.rect(surf, (255, 255, 255), (_ss_x + 1, y - bh - 5, 6, 6), 1, border_radius=1)

        # ── Wheels ────────────────────────────────────────────────
        wheel_angle = self._t * 5.0
        for wx_c in (x + 20, x + bw - 20):
            pygame.draw.circle(surf, (22, 22, 22), (wx_c, y + 3), 10)
            pygame.draw.circle(surf, (72, 72, 76),  (wx_c, y + 3),  6)
            pygame.draw.circle(surf, (152, 152, 158),(wx_c, y + 3),  2)
            for _sa in range(0, 3):
                _ang = wheel_angle + _sa * (math.pi * 2 / 3)
                _ex  = wx_c + int(math.cos(_ang) * 5)
                _ey  = y + 3 + int(math.sin(_ang) * 5)
                pygame.draw.line(surf, (55, 55, 60), (wx_c, y + 3), (_ex, _ey), 1)


class FlyingBird:
    """Tiny V-wing bird that flies across the sky zone of the left panel."""

    def __init__(self, initial: bool = True):
        self._spawn(initial)

    def _spawn(self, initial: bool = False):
        self.y     = float(random.randint(TOP_H + 8, TOP_H + 50))
        self.dir   = random.choice([-1, 1])
        self.x     = float(random.randint(0, LEFT_W) if initial
                           else (-20 if self.dir > 0 else LEFT_W + 20))
        self.speed = random.uniform(30, 65)
        self.t     = random.uniform(0, math.pi * 2)
        self.flap  = random.uniform(4.0, 8.0)

    def update(self, dt: float):
        self.x += self.dir * self.speed * dt
        self.t += dt * self.flap
        if self.x > LEFT_W + 28 or self.x < -28:
            self._spawn()

    def draw(self, surf: pygame.Surface):
        x, y  = int(self.x), int(self.y)
        flap  = int(math.sin(self.t) * 4)
        pygame.draw.line(surf, _DARK, (x, y), (x - 7, y - flap), 2)
        pygame.draw.line(surf, _DARK, (x, y), (x + 7, y - flap), 2)


class Pterodactyl:
    """Large V-wing pterodactyl that flies across zone 7 sky."""

    def __init__(self, initial: bool = True):
        self._spawn(initial)

    def _spawn(self, initial: bool = False):
        self.y     = float(random.randint(TOP_H + 15, TOP_H + 70))
        self.dir   = random.choice([-1, 1])
        self.x     = float(random.randint(0, LEFT_W) if initial
                           else (-30 if self.dir > 0 else LEFT_W + 30))
        self.speed = random.uniform(40, 80)
        self.t     = random.uniform(0, math.pi * 2)
        self.flap  = random.uniform(2.5, 5.0)

    def update(self, dt: float):
        self.x += self.dir * self.speed * dt
        self.t += dt * self.flap
        if self.x > LEFT_W + 40 or self.x < -40:
            self._spawn()

    def draw(self, surf: pygame.Surface):
        x, y  = int(self.x), int(self.y)
        flap  = int(math.sin(self.t) * 7)
        col   = (60, 40, 20)
        # Large V-shape wings (15px span each side)
        pygame.draw.line(surf, col, (x, y), (x - 15, y - flap), 2)
        pygame.draw.line(surf, col, (x, y), (x + 15, y - flap), 2)
        # Wing tips angled down slightly
        pygame.draw.line(surf, col, (x - 15, y - flap), (x - 22, y - flap + 4), 2)
        pygame.draw.line(surf, col, (x + 15, y - flap), (x + 22, y - flap + 4), 2)
        # Head/beak nub
        bx = x + self.dir * 5
        pygame.draw.line(surf, col, (x, y), (bx, y - 2), 2)
        pygame.draw.line(surf, col, (bx, y - 2), (bx + self.dir * 7, y - 1), 1)


def _tint_brownish(surf: pygame.Surface) -> pygame.Surface:
    """Recolour a teal/blue sprite to warm brown using luminance remapping."""
    try:
        import numpy as np
        arr   = pygame.surfarray.pixels3d(surf)
        alpha = pygame.surfarray.pixels_alpha(surf)
        R, G, B = arr[:,:,0].astype(float), arr[:,:,1].astype(float), arr[:,:,2].astype(float)
        lum = 0.30*R + 0.59*G + 0.11*B
        arr[:,:,0] = np.clip(lum * 1.20, 0, 255).astype(np.uint8)   # warm red
        arr[:,:,1] = np.clip(lum * 0.85, 0, 255).astype(np.uint8)   # mid green
        arr[:,:,2] = np.clip(lum * 0.45, 0, 255).astype(np.uint8)   # low blue
        del arr, alpha
    except Exception:
        pass
    return surf


class SpritePterodactyl(Pterodactyl):
    """Pterodactyl using pterosaur PNG sprites; falls back to procedural."""
    _frames: list = []
    _loaded: bool = False

    @classmethod
    def _ensure_frames(cls):
        if cls._loaded:
            return
        cls._loaded = True
        try:
            base = _os.path.join(_ASSETS_DIR, "dinosaurs", "dinosaurs")
            f1 = pygame.image.load(_os.path.join(base, "pterosaur1.png")).convert_alpha()
            f2 = pygame.image.load(_os.path.join(base, "pterosaur2.png")).convert_alpha()
            size = (52, 52)
            r1 = _tint_brownish(pygame.transform.smoothscale(f1, size))
            r2 = _tint_brownish(pygame.transform.smoothscale(f2, size))
            cls._frames = [r1, r2,
                           pygame.transform.flip(r1, True, False),
                           pygame.transform.flip(r2, True, False)]
        except Exception:
            cls._frames = []

    def __init__(self, initial: bool = True):
        super().__init__(initial)
        self.__class__._ensure_frames()

    def draw(self, surf: pygame.Surface):
        x, y = int(self.x), int(self.y)
        wlift = int(math.sin(self.t) * 13)   # -13..+13 px — clearly visible flap

        c_wing = (165, 115, 55)    # warm tan
        c_under = (120,  80, 38)   # darker underside
        c_body  = (190, 140, 75)   # lighter body
        c_dark  = ( 85,  58, 25)   # outlines / beak

        # Both wings pivot from body centre and lift/drop together
        lx, ly = x - 26, y - wlift    # left  wing-tip
        rx, ry = x + 26, y - wlift    # right wing-tip

        # Filled wing fans (four-point quads)
        pygame.draw.polygon(surf, c_wing,  [(x, y+1), (lx, ly), (lx - 5, ly + 7), (x - 4, y + 5)])
        pygame.draw.polygon(surf, c_under, [(x, y+1), (rx, ry), (rx + 5, ry + 7), (x + 4, y + 5)])
        # Wing-edge lines for crispness
        pygame.draw.line(surf, c_dark, (x, y), (lx, ly), 1)
        pygame.draw.line(surf, c_dark, (x, y), (rx, ry), 1)

        # Body
        pygame.draw.ellipse(surf, c_body, (x - 7, y - 3, 14, 7))
        # Head
        hx = x + self.dir * 9
        pygame.draw.ellipse(surf, c_body, (hx - 4, y - 5, 9, 7))
        # Long beak in flight direction
        pygame.draw.line(surf, c_dark, (hx + self.dir * 3, y - 1), (hx + self.dir * 15, y - 1), 2)
        # Short tail
        tx = x - self.dir * 7
        pygame.draw.line(surf, c_dark, (tx, y + 1), (tx - self.dir * 7, y + 4), 2)


class SpriteStudent(WalkingPerson):
    """Walking student using roguelike character sprites; falls back to procedural."""
    _chars: list = []  # list of (right_surf, left_surf)
    _loaded: bool = False

    @classmethod
    def _ensure_chars(cls):
        if cls._loaded:
            return
        cls._loaded = True
        CELL = 17
        try:
            path = _os.path.join(_ASSETS_DIR, "kenney_roguelike-characters",
                                 "Spritesheet", "roguelikeChar_transparent.png")
            sheet = pygame.image.load(path).convert_alpha()
            for row in (0, 1, 2, 3, 5, 6):
                sub = sheet.subsurface(0, row * CELL, CELL, CELL)
                scaled = pygame.transform.scale(sub, (34, 34))
                cls._chars.append((scaled, pygame.transform.flip(scaled, True, False)))
        except Exception:
            cls._chars = []

    def __init__(self, y: int, shirt=_BLUE):
        super().__init__(y, shirt)
        self.__class__._ensure_chars()
        self._char_idx = (random.randint(0, max(0, len(self._chars) - 1))
                          if self._chars else 0)

    def draw(self, surf: pygame.Surface):
        if not self._chars:
            super().draw(surf)
            return
        char_r, char_l = self._chars[self._char_idx % len(self._chars)]
        frame = char_r if self.dir > 0 else char_l
        bob = int(math.sin(self.t) * 2)
        surf.blit(frame, (int(self.x) - 17, int(self.y) - 30 + bob))


class WingSprite:
    """Small white feather/wing shape that floats upward and fades for zone 8."""

    def __init__(self):
        self.x     = float(random.randint(10, LEFT_W - 10))
        self.y     = float(random.randint(TOP_H + 20, TOP_H + 90))
        self.vy    = random.uniform(-18, -8)
        self.vx    = random.uniform(-5, 5)
        self.alpha = float(random.randint(180, 255))
        self.size  = random.randint(5, 10)
        self.t     = random.uniform(0, math.pi * 2)

    def update(self, dt: float):
        self.y     += self.vy * dt
        self.x     += self.vx * dt
        self.t     += dt * 2.0
        self.alpha -= 55 * dt

    def draw(self, surf: pygame.Surface):
        a = max(0, int(self.alpha))
        if a == 0:
            return
        x, y = int(self.x), int(self.y)
        s = self.size
        wing_surf = pygame.Surface((s * 5, s * 3), pygame.SRCALPHA)
        cx, cy = s * 2, s
        # Left wing arc
        pygame.draw.ellipse(wing_surf, (255, 255, 255, a),
                            (0, cy - s // 2, s * 2, s))
        # Right wing arc
        pygame.draw.ellipse(wing_surf, (255, 255, 255, a),
                            (cx + 2, cy - s // 2, s * 2, s))
        # Center body dot
        pygame.draw.circle(wing_surf, (240, 235, 210, a), (cx, cy), max(1, s // 3))
        surf.blit(wing_surf, (x - s * 2, y - s))

    @property
    def alive(self) -> bool:
        return self.alpha > 0


class LavaParticle:
    """Small orange-red dot that drifts upward from the horizon for zone 9."""

    def __init__(self, horizon_y: int):
        self.x     = float(random.randint(10, LEFT_W - 10))
        self.y     = float(random.randint(horizon_y, horizon_y + 30))
        self.vy    = random.uniform(-22, -8)
        self.vx    = random.uniform(-4, 4)
        self.alpha = float(random.randint(160, 255))
        self.size  = random.randint(1, 3)
        r = random.randint(200, 255)
        g = random.randint(40, 110)
        self.color = (r, g, 5)

    def update(self, dt: float):
        self.y     += self.vy * dt
        self.x     += self.vx * dt
        self.alpha -= 80 * dt

    def draw(self, surf: pygame.Surface):
        a = max(0, int(self.alpha))
        if a == 0:
            return
        s = pygame.Surface((self.size * 2 + 2, self.size * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, a),
                           (self.size + 1, self.size + 1), self.size)
        surf.blit(s, (int(self.x) - self.size - 1, int(self.y) - self.size - 1))

    @property
    def alive(self) -> bool:
        return self.alpha > 0


class FlyingCar:
    def __init__(self):
        self._reset()

    def _reset(self):
        self.direction = random.choice([-1, 1])
        if self.direction == 1:
            self.x = float(-60)
        else:
            self.x = float(LEFT_W + 60)
        self.y      = float(TOP_H + random.randint(55, 130))
        self.speed  = float(random.randint(38, 75))
        self.bob_t  = random.uniform(0, math.pi * 2)
        self.bob_sp = random.uniform(1.5, 3.0)
        # Color: silver/cyan futuristic body
        r = random.choice([(180,210,230), (160,200,220), (200,220,240), (140,180,210)])
        self.color  = r
        self.width  = random.randint(22, 34)
        self.height = 9

    def update(self, dt: float):
        self.x     += self.speed * self.direction * dt
        self.bob_t += self.bob_sp * dt
        if self.direction == 1 and self.x > LEFT_W + 70:
            self._reset()
        elif self.direction == -1 and self.x < -70:
            self._reset()

    def draw(self, surf: pygame.Surface):
        bx = int(self.x)
        by = int(self.y + math.sin(self.bob_t) * 3)
        w, h = self.width, self.height
        # Main body (rounded rectangle approximation)
        pygame.draw.rect(surf, self.color, (bx, by, w, h), border_radius=4)
        # Windshield (cyan tint)
        win_x = bx + (w // 4 if self.direction == 1 else w // 2)
        pygame.draw.rect(surf, (100, 220, 240), (win_x, by + 1, w // 4, h - 2), border_radius=2)
        # Underbody glow (bright cyan line)
        pygame.draw.line(surf, (0, 200, 255),
                         (bx + 2, by + h), (bx + w - 2, by + h), 1)
        # Exhaust trail (small dots behind the car)
        ex = bx - 4 * self.direction
        for i in range(3):
            ex2 = ex - i * 4 * self.direction
            pygame.draw.circle(surf, (0, 180, 255), (ex2, by + h // 2), max(1, 2 - i))


class SpaceshipFighters:
    def __init__(self):
        self._timer   = 0.0
        self._cooldown= 8.0   # seconds between passes
        self._active  = False
        self.ship_a   = {"x": -80.0, "y": float(TOP_H + 40), "dir": 1}   # Alliance (left→right)
        self.ship_b   = {"x": float(LEFT_W + 80), "y": float(TOP_H + 55), "dir": -1}  # Empire (right→left)
        self._lasers  = []   # list of {"x","y","dx","color"}
        self._laser_t = 0.0

    def update(self, dt: float):
        self._timer += dt
        if not self._active:
            if self._timer >= self._cooldown:
                self._timer   = 0.0
                self._cooldown= random.uniform(7.0, 14.0)
                self._active  = True
                self.ship_a["x"] = -80.0
                self.ship_b["x"] = float(LEFT_W + 80)
                self._lasers.clear()
            return

        speed = 65.0
        self.ship_a["x"] += speed * dt
        self.ship_b["x"] -= speed * dt

        # Fire lasers periodically while active
        self._laser_t += dt
        if self._laser_t >= 0.25:
            self._laser_t = 0.0
            if self.ship_a["x"] > 0:
                self._lasers.append({
                    "x": self.ship_a["x"] + 20,
                    "y": self.ship_a["y"] + 4,
                    "dx": 180.0,
                    "color": (255, 50, 50),  # red Alliance laser
                })
            if self.ship_b["x"] < LEFT_W:
                self._lasers.append({
                    "x": self.ship_b["x"] - 20,
                    "y": self.ship_b["y"] + 4,
                    "dx": -180.0,
                    "color": (0, 255, 100),  # green Empire laser
                })

        # Move lasers
        for laser in self._lasers:
            laser["x"] += laser["dx"] * dt

        # Cull off-screen lasers
        self._lasers = [l for l in self._lasers if -20 <= l["x"] <= LEFT_W + 20]

        # Deactivate when both ships have crossed
        if self.ship_a["x"] > LEFT_W + 100 and self.ship_b["x"] < -100:
            self._active = False
            self._lasers.clear()

    def _draw_ship_a(self, surf, x, y):
        """Alliance X-wing style (blue/white, T-shape body)."""
        xi, yi = int(x), int(y)
        # Main fuselage
        pygame.draw.rect(surf, (200, 210, 230), (xi, yi + 3, 28, 6), border_radius=2)
        # Wings (4 small fins)
        pygame.draw.line(surf, (160, 180, 210), (xi + 8, yi), (xi + 20, yi + 3), 2)
        pygame.draw.line(surf, (160, 180, 210), (xi + 8, yi + 12), (xi + 20, yi + 9), 2)
        # Nose
        pygame.draw.polygon(surf, (220, 230, 255),
                            [(xi + 28, yi + 5), (xi + 28, yi + 7), (xi + 36, yi + 6)])
        # Engine glow
        pygame.draw.circle(surf, (80, 160, 255), (xi, yi + 6), 3)

    def _draw_ship_b(self, surf, x, y):
        """Empire TIE-fighter style (dark grey, hexagonal wing panels)."""
        xi, yi = int(x), int(y)
        # Center pod
        pygame.draw.rect(surf, (80, 80, 90), (xi - 6, yi + 2, 12, 8), border_radius=2)
        # Left hexagonal panel
        panel_pts_l = [(xi - 20, yi), (xi - 8, yi + 1), (xi - 8, yi + 11), (xi - 20, yi + 12)]
        pygame.draw.polygon(surf, (60, 62, 72), panel_pts_l)
        pygame.draw.polygon(surf, (90, 95, 110), panel_pts_l, 1)
        # Right hexagonal panel
        panel_pts_r = [(xi + 8, yi + 1), (xi + 20, yi), (xi + 20, yi + 12), (xi + 8, yi + 11)]
        pygame.draw.polygon(surf, (60, 62, 72), panel_pts_r)
        pygame.draw.polygon(surf, (90, 95, 110), panel_pts_r, 1)
        # Engine dot
        pygame.draw.circle(surf, (220, 80, 0), (xi + 6, yi + 6), 2)

    def draw(self, surf: pygame.Surface):
        if not self._active:
            return
        # Draw lasers
        for laser in self._lasers:
            lx, ly = int(laser["x"]), int(laser["y"])
            pygame.draw.line(surf, laser["color"], (lx, ly), (lx + int(laser["dx"] * 0.06), ly), 2)
        # Draw ships
        self._draw_ship_a(surf, self.ship_a["x"], self.ship_a["y"])
        self._draw_ship_b(surf, self.ship_b["x"], self.ship_b["y"])


class WizardBattle:
    """Two wizards shooting spells at each other across the mini-view (zone 6)."""

    def __init__(self, y_pos: int):
        self.y = y_pos
        self.active = True
        self.spell_x = 30.0
        self.spell_dir = 1
        self.spell_color = random.choice([(255,80,30),(80,160,255),(200,255,100)])
        self.spell_timer = 0.0
        self.cast_cooldown = random.uniform(1.5, 3.0)

    def update(self, dt: float):
        self.spell_timer += dt
        if self.spell_timer >= self.cast_cooldown:
            self.spell_x += self.spell_dir * 120 * dt
            if self.spell_x > LEFT_W - 30 or self.spell_x < 30:
                self.spell_dir *= -1
                self.spell_color = random.choice([(255,80,30),(80,160,255),(200,255,100)])
                self.spell_timer = 0.0
                self.cast_cooldown = random.uniform(1.5, 3.0)

    def draw(self, surf: pygame.Surface):
        y = self.y
        skin = (220, 185, 145)
        lx, rx = 20, LEFT_W - 20
        # Left wizard — bright orange-gold (contrasts with purple crystals)
        pygame.draw.rect(surf, (215, 100, 18), (lx - 11, y - 38, 22, 38))
        pygame.draw.rect(surf, (255, 160, 0),  (lx - 13, y - 54, 26, 5))   # hat brim
        pygame.draw.polygon(surf, (200, 85, 10),
                            [(lx - 13, y - 54), (lx, y - 82), (lx + 13, y - 54)])
        pygame.draw.circle(surf, skin, (lx, y - 44), 10)
        pygame.draw.line(surf, skin, (lx + 11, y - 30), (lx + 26, y - 20), 3)
        # Right wizard — electric blue (contrasts with orange + crystals)
        pygame.draw.rect(surf, (20, 85, 215),  (rx - 11, y - 38, 22, 38))
        pygame.draw.rect(surf, (55, 150, 255), (rx - 13, y - 54, 26, 5))   # hat brim
        pygame.draw.polygon(surf, (15, 60, 185),
                            [(rx - 13, y - 54), (rx, y - 82), (rx + 13, y - 54)])
        pygame.draw.circle(surf, skin, (rx, y - 44), 10)
        pygame.draw.line(surf, skin, (rx - 11, y - 30), (rx - 26, y - 20), 3)
        # Spell projectile with soft glow
        if self.spell_timer >= self.cast_cooldown * 0.3:
            col = self.spell_color
            sx, sy = int(self.spell_x), y - 20
            glow = pygame.Surface((28, 28), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*col, 70), (14, 14), 14)
            surf.blit(glow, (sx - 14, sy - 14))
            pygame.draw.circle(surf, col,           (sx, sy), 8)
            pygame.draw.circle(surf, (255, 255, 255),(sx, sy), 4)


class FloatingDeco:
    """Small pixel-art icon (star, book, cap…) that bobs up and down."""

    _PIX: dict = {
        "star": [
            (1,0,_GOLD),
            (0,1,_GOLD),(1,1,_GOLD),(2,1,_GOLD),
            (1,2,_GOLD),
        ],
        "book": [
            (0,0,(45,100,170)),(1,0,(230,230,230)),(2,0,(45,100,170)),
            (0,1,(45,100,170)),(1,1,(230,230,230)),(2,1,(45,100,170)),
            (0,2,(45,100,170)),(1,2,(45,100,170)),(2,2,(45,100,170)),
        ],
        "cap": [
            (0,1,(40,40,40)),(1,1,(40,40,40)),(2,1,(40,40,40)),(3,1,(40,40,40)),
            (1,0,(40,40,40)),(2,0,(40,40,40)),
            (2,2,(190,50,50)),
        ],
        "gear": [
            (1,0,(120,120,120)),
            (0,1,(120,120,120)),(1,1,(160,160,160)),(2,1,(120,120,120)),
            (1,2,(120,120,120)),
        ],
        "atom": [
            (1,0,(65,124,175)),(2,0,(65,124,175)),
            (0,1,(65,124,175)),(3,1,(65,124,175)),
            (1,2,(65,124,175)),(2,2,(65,124,175)),
        ],
    }

    def __init__(self, x: int, y: int, kind: str = "star", scale: int = 4):
        self.x      = float(x)
        self.base_y = float(y)
        self.kind   = kind
        self.scale  = scale
        self.t      = random.uniform(0, math.pi * 2)
        self.bob    = random.uniform(1.0, 1.8)

    def update(self, dt: float):
        self.t += dt * self.bob

    def draw(self, surf: pygame.Surface):
        yo = int(math.sin(self.t) * 4)
        x, y = int(self.x), int(self.base_y) + yo
        s = self.scale
        for dx, dy, col in self._PIX.get(self.kind, self._PIX["star"]):
            pygame.draw.rect(surf, col, (x + dx * s, y + dy * s, s, s))


class TabParticle:
    """Tiny speck that drifts upward and fades out."""

    _COLORS = [_GOLD, (100, 200, 100), (120, 180, 255)]

    def __init__(self, x: int, y: int):
        self.x     = float(x) + random.uniform(-12, 12)
        self.y     = float(y)
        self.vx    = random.uniform(-10, 10)
        self.vy    = random.uniform(-28, -52)
        self.alpha = float(random.randint(180, 255))
        self.size  = random.randint(2, 3)
        self.color = random.choice(self._COLORS)
        s = self.size * 2
        self._surf = pygame.Surface((s, s))
        self._surf.fill(self.color)

    def update(self, dt: float):
        self.x     += self.vx * dt
        self.y     += self.vy * dt
        self.alpha -= 160 * dt

    def draw(self, surf: pygame.Surface):
        a = max(0, int(self.alpha))
        if a == 0:
            return
        self._surf.set_alpha(a)
        surf.blit(self._surf, (int(self.x) - self.size, int(self.y) - self.size))

    @property
    def alive(self) -> bool:
        return self.alpha > 0


class SpinningGear:
    """Decorative spinning gear for the Settings tab."""

    def __init__(self, x: int, y: int, r: int = 24, teeth: int = 10):
        self.x, self.y = x, y
        self.r         = r
        self.teeth     = teeth
        self.angle     = 0.0

    def update(self, dt: float):
        self.angle += 0.55 * dt

    def draw(self, surf: pygame.Surface):
        n     = self.teeth * 2
        r_out = self.r
        r_in  = self.r - 7
        pts   = []
        for i in range(n):
            a = self.angle + i * (math.pi * 2 / n)
            r = r_out if i % 2 == 0 else r_in
            pts.append((self.x + math.cos(a) * r, self.y + math.sin(a) * r))
        if pts:
            pygame.draw.polygon(surf, (130, 130, 130), pts)
        pygame.draw.circle(surf, (85, 85, 85),   (self.x, self.y), r_in - 2)
        pygame.draw.circle(surf, (125, 125, 125), (self.x, self.y), 4)


# ── Per-tab deco definitions ──────────────────────────────────────────────────

_TAB_DECOS: dict[str, list[tuple[str, int]]] = {
    "Buildings":   [("book", 2), ("star", 1)],
    "Upgrades":    [("atom", 2), ("star", 1)],
    "Curriculum":  [("book", 2), ("cap", 1)],
    "Report Card": [("star", 2), ("cap", 1)],
    "Prestige":    [("cap", 3)],
    "Legacy":      [("cap", 2), ("star", 1)],
    "Settings":    [("gear", 2)],
}

# Positions around the school building on the left panel
_LEFT_DECO_SLOTS = [
    (28,  188),
    (298, 192),
    (28,  248),
    (298, 252),
    (82,   96),
    (252,  96),
]


class FlyingHero:
    """Caped hero arcing across the sky for Zone 10."""
    _COLORS = [
        ((60, 100, 220), (220, 40,  40)),
        ((200, 60,  60), (255, 200,  0)),
        ((60, 180,  80), (120, 60, 200)),
    ]

    def __init__(self, idx: int = 0):
        self._ci = idx % len(self._COLORS)
        self.body_col, self.cape_col = self._COLORS[self._ci]
        self.x = float(random.randint(0, LEFT_W))
        self.y = float(random.randint(TOP_H + 20, TOP_H + 90))
        self.dir = random.choice([-1, 1])
        self.speed = random.uniform(55, 95)
        self.t = random.uniform(0, math.tau)
        self.trail: list = []

    def _reset(self):
        self.body_col, self.cape_col = self._COLORS[self._ci]
        self.dir = random.choice([-1, 1])
        self.x = float(-30) if self.dir > 0 else float(LEFT_W + 30)
        self.y = float(random.randint(TOP_H + 20, TOP_H + 90))
        self.speed = random.uniform(55, 95)
        self.trail = []

    def update(self, dt: float):
        self.t += dt * 2.5
        self.x += self.dir * self.speed * dt
        self.y += math.sin(self.t * 0.7) * 18 * dt
        self.trail.append((int(self.x), int(self.y), 0))
        self.trail = [(tx, ty, ta + 1) for tx, ty, ta in self.trail if ta < 9]
        if (self.dir > 0 and self.x > LEFT_W + 40) or (self.dir < 0 and self.x < -40):
            self._reset()

    def draw(self, surf: pygame.Surface):
        for tx, ty, ta in self.trail:
            r = max(1, 3 - ta // 3)
            pygame.draw.circle(surf, (255, 240, 80), (tx, ty), r)
        x, y = int(self.x), int(self.y)
        cape_pts = [(x, y), (x - self.dir * 10, y - 3), (x - self.dir * 8, y + 4)]
        pygame.draw.polygon(surf, self.cape_col, cape_pts)
        pygame.draw.rect(surf, self.body_col, (x - 3, y - 3, 6, 7), border_radius=2)
        pygame.draw.circle(surf, (220, 175, 120), (x, y - 5), 4)
        pygame.draw.circle(surf, self.body_col, (x + self.dir * 6, y - 1), 2)


class GroundFighter:
    """Hero-vs-villain brawl on the ground for Zone 10."""
    _PAIRS = [
        ((60, 100, 220), (160, 30,  30)),
        ((60, 180,  80), ( 80, 30, 100)),
        ((220, 180, 40), ( 40, 40,  40)),
    ]

    def __init__(self, y: float, idx: int = 0):
        self._ci = idx % len(self._PAIRS)
        self.hero_col, self.villain_col = self._PAIRS[self._ci]
        self.cx = float(random.randint(30, LEFT_W - 30))
        self.y = y
        self.t = random.uniform(0, math.tau)
        self.sparks: list = []

    def update(self, dt: float):
        self.t += dt * 3.0
        if math.sin(self.t) > 0.85:
            for _ in range(3):
                self.sparks.append([
                    int(self.cx), int(self.y - 8),
                    random.uniform(-40, 40), random.uniform(-50, -10), 1.0,
                ])
        for sp in self.sparks:
            sp[0] += int(sp[2] * dt)
            sp[1] += int(sp[3] * dt)
            sp[4] -= dt * 2.5
        self.sparks = [sp for sp in self.sparks if sp[4] > 0]

    def draw(self, surf: pygame.Surface):
        swing = math.sin(self.t) * 6
        hx = int(self.cx - 10 + swing)
        vx = int(self.cx + 10 - swing)
        y  = int(self.y)
        for fx, col in ((hx, self.hero_col), (vx, self.villain_col)):
            pygame.draw.rect(surf, col, (fx - 3, y - 14, 6, 8), border_radius=1)
            pygame.draw.circle(surf, (220, 175, 120), (fx, y - 18), 4)
            pygame.draw.line(surf, col, (fx, y - 6), (fx - 3, y), 2)
            pygame.draw.line(surf, col, (fx, y - 6), (fx + 3, y), 2)
        pygame.draw.line(surf, self.hero_col,    (hx + 3, y - 12), (hx + 9, y - 10), 2)
        pygame.draw.line(surf, self.villain_col, (vx - 3, y - 12), (vx - 9, y - 10), 2)
        for sp in self.sparks:
            pygame.draw.circle(surf, (255, 220, 50), (int(sp[0]), int(sp[1])), 2)


class GhostFigure:
    """Floating pale ghost silhouette that drifts across Zone 2 (Ruins)."""

    def __init__(self, idx: int = 0):
        self.x = float(random.randint(10, LEFT_W - 10))
        self.y = float(random.randint(TOP_H + 80, TOP_H + 180))
        self.speed = random.uniform(12, 22)
        self.t = random.uniform(0, math.pi * 2)

    def update(self, dt: float):
        self.x += self.speed * dt
        self.t += dt * 1.8
        if self.x > LEFT_W + 20:
            self.x = -20.0
            self.y = float(random.randint(TOP_H + 80, TOP_H + 180))

    def draw(self, surf: pygame.Surface):
        x, y = int(self.x), int(self.y + math.sin(self.t) * 6)
        ghost = pygame.Surface((22, 28), pygame.SRCALPHA)
        # Round head
        pygame.draw.ellipse(ghost, (230, 230, 240, 160), (3, 0, 16, 16))
        # Body tapering to ragged bottom
        pygame.draw.ellipse(ghost, (230, 230, 240, 140), (1, 8, 20, 18))
        surf.blit(ghost, (x - 11, y - 14))


class AncientWarrior(WalkingPerson):
    """Bronze-armored soldier with spear and shield for Zone 4 (Ancient Academy)."""

    def __init__(self, y: int, idx: int = 0):
        super().__init__(y)
        self.speed = random.uniform(18, 28)
        self._armor = (184, 142, 50)   # bronze
        self._shield = (165, 110, 35)

    def draw(self, surf: pygame.Surface):
        x, y = int(self.x), int(self.y)
        walk = math.sin(self.t)
        leg = int(walk * 5)
        # Legs
        pygame.draw.line(surf, (80, 60, 20), (x - 2, y + 2), (x - 3 + leg, y + 10), 2)
        pygame.draw.line(surf, (80, 60, 20), (x + 2, y + 2), (x + 3 - leg, y + 10), 2)
        # Body / armor plate
        pygame.draw.rect(surf, self._armor, (x - 5, y - 8, 10, 10), border_radius=1)
        # Helmet with red crest
        pygame.draw.circle(surf, self._armor, (x, y - 14), 5)
        pygame.draw.rect(surf, (200, 30, 30), (x - 1, y - 20, 3, 6))   # crest
        # Round shield on off-side arm
        shield_x = x - self.dir * 8
        pygame.draw.circle(surf, self._shield, (shield_x, y - 4), 5)
        pygame.draw.circle(surf, (200, 160, 60), (shield_x, y - 4), 5, 1)
        # Spear arm pointing forward
        arm = int(walk * 4)
        spear_tip_x = x + self.dir * 18
        pygame.draw.line(surf, _SKIN, (x + self.dir * 4, y - 5), (spear_tip_x, y - 9 - arm), 1)
        pygame.draw.line(surf, (160, 160, 160), (x + self.dir * 8, y - 7 - arm),
                         (spear_tip_x, y - 9 - arm), 2)
        pygame.draw.polygon(surf, (200, 200, 200),
                            [(spear_tip_x, y - 12 - arm),
                             (spear_tip_x + self.dir * 4, y - 9 - arm),
                             (spear_tip_x, y - 6 - arm)])


class TrojanHorse:
    """Large wooden horse that scrolls slowly across Zone 4."""

    _WOOD = (135, 95, 50)
    _EDGE = (90, 60, 30)

    def __init__(self):
        self.x = float(random.randint(0, LEFT_W))
        self.speed = 14.0

    def update(self, dt: float):
        self.x -= self.speed * dt
        if self.x < -80:
            self.x = float(LEFT_W + 80)

    def draw(self, surf: pygame.Surface):
        x = int(self.x)
        y = TOP_H + 265
        W_ = self._WOOD
        E = self._EDGE
        # Body (large ellipse)
        pygame.draw.ellipse(surf, W_, (x - 28, y - 18, 56, 28))
        pygame.draw.ellipse(surf, E, (x - 28, y - 18, 56, 28), 1)
        # Neck + head
        pygame.draw.rect(surf, W_, (x + 18, y - 30, 10, 18))
        pygame.draw.rect(surf, E, (x + 18, y - 30, 10, 18), 1)
        pygame.draw.rect(surf, W_, (x + 15, y - 38, 18, 12), border_radius=3)
        pygame.draw.rect(surf, E, (x + 15, y - 38, 18, 12), border_radius=3, width=1)
        # Snout line
        pygame.draw.line(surf, E, (x + 33, y - 32), (x + 38, y - 30), 2)
        # Tail
        pygame.draw.line(surf, E, (x - 28, y - 8), (x - 36, y - 2), 2)
        pygame.draw.line(surf, E, (x - 36, y - 2), (x - 38, y + 6), 2)
        # 4 stick legs
        for lx_off, ly_off in ((-18, 0), (-6, 2), (6, 2), (18, 0)):
            pygame.draw.line(surf, E, (x + lx_off, y + 10), (x + lx_off, y + 22), 3)
        # 4 wheels underneath (one per leg)
        for wx in (x - 18, x - 6, x + 6, x + 18):
            pygame.draw.circle(surf, E, (wx, y + 24), 5, 2)
            pygame.draw.line(surf, E, (wx - 5, y + 24), (wx + 5, y + 24), 1)
            pygame.draw.line(surf, E, (wx, y + 19), (wx, y + 29), 1)
        # Small door outline on flank
        pygame.draw.rect(surf, E, (x - 10, y - 14, 10, 12), 1)


class FlyingAngel:
    """White-robed angel with golden halo flying across Zone 8 sky."""

    def __init__(self, idx: int = 0):
        self.x = float(random.randint(0, LEFT_W))
        self.y = float(random.randint(TOP_H + 25, TOP_H + 100))
        self.dir = random.choice([-1, 1])
        self.speed = random.uniform(30, 55)
        self.t = random.uniform(0, math.tau)

    def _reset(self):
        self.dir = random.choice([-1, 1])
        self.x = float(-30) if self.dir > 0 else float(LEFT_W + 30)
        self.y = float(random.randint(TOP_H + 25, TOP_H + 100))
        self.speed = random.uniform(30, 55)

    def update(self, dt: float):
        self.t += dt * 2.0
        self.x += self.dir * self.speed * dt
        if (self.dir > 0 and self.x > LEFT_W + 40) or (self.dir < 0 and self.x < -40):
            self._reset()

    def draw(self, surf: pygame.Surface):
        x, y = int(self.x), int(self.y)
        flap = int(math.sin(self.t) * 10)
        # White wings (symmetric)
        pygame.draw.polygon(surf, (240, 240, 255),
                            [(x, y), (x - 20, y - flap), (x - 12, y + 6)])
        pygame.draw.polygon(surf, (240, 240, 255),
                            [(x, y), (x + 20, y - flap), (x + 12, y + 6)])
        pygame.draw.line(surf, (200, 200, 230), (x, y), (x - 20, y - flap), 1)
        pygame.draw.line(surf, (200, 200, 230), (x, y), (x + 20, y - flap), 1)
        # White robe body
        pygame.draw.rect(surf, (245, 245, 255), (x - 4, y, 8, 10), border_radius=2)
        # Skin head
        pygame.draw.circle(surf, _SKIN, (x, y - 5), 4)
        # Golden halo (thin ellipse above head)
        pygame.draw.ellipse(surf, _GOLD, (x - 6, y - 14, 12, 4), 1)


class HaloWalker(WalkingPerson):
    """White-robed walking person with golden halo for Zone 8."""

    _SKIN_VARIANTS = [_SKIN, (200, 160, 120), (240, 210, 170)]

    def __init__(self, y: int, idx: int = 0):
        super().__init__(y)
        self.speed = random.uniform(16, 28)
        self._skin_col = self._SKIN_VARIANTS[idx % len(self._SKIN_VARIANTS)]

    def draw(self, surf: pygame.Surface):
        x, y = int(self.x), int(self.y)
        walk = math.sin(self.t)
        leg = int(walk * 5)
        # White robe
        pygame.draw.rect(surf, (245, 245, 255), (x - 4, y - 8, 8, 10), border_radius=2)
        # Skin head
        pygame.draw.circle(surf, self._skin_col, (x, y - 13), 5)
        # Golden halo above head
        pygame.draw.ellipse(surf, _GOLD, (x - 7, y - 22, 14, 5), 1)
        # Legs under robe
        pygame.draw.line(surf, (220, 220, 240), (x - 2, y + 2), (x - 3 + leg, y + 10), 2)
        pygame.draw.line(surf, (220, 220, 240), (x + 2, y + 2), (x + 3 - leg, y + 10), 2)


class FlyingDemon:
    """Bat-winged demon flying across Zone 9 sky."""

    def __init__(self, idx: int = 0):
        self.x = float(random.randint(0, LEFT_W))
        self.y = float(random.randint(TOP_H + 20, TOP_H + 100))
        self.dir = random.choice([-1, 1])
        self.speed = random.uniform(55, 90)
        self.t = random.uniform(0, math.tau)

    def _reset(self):
        self.dir = random.choice([-1, 1])
        self.x = float(-35) if self.dir > 0 else float(LEFT_W + 35)
        self.y = float(random.randint(TOP_H + 20, TOP_H + 100))
        self.speed = random.uniform(55, 90)

    def update(self, dt: float):
        self.t += dt * 3.0
        self.x += self.dir * self.speed * dt
        if (self.dir > 0 and self.x > LEFT_W + 45) or (self.dir < 0 and self.x < -45):
            self._reset()

    def draw(self, surf: pygame.Surface):
        x, y = int(self.x), int(self.y)
        flap = int(math.sin(self.t) * 10)
        body_col = (170, 20, 20)
        wing_col = (120, 10, 10)
        # Jagged bat wings
        pygame.draw.polygon(surf, wing_col,
                            [(x, y), (x - 22, y - flap),
                             (x - 15, y - flap + 8), (x - 8, y + 4)])
        pygame.draw.polygon(surf, wing_col,
                            [(x, y), (x + 22, y - flap),
                             (x + 15, y - flap + 8), (x + 8, y + 4)])
        # Body
        pygame.draw.rect(surf, body_col, (x - 3, y - 2, 6, 8), border_radius=1)
        # Head
        pygame.draw.circle(surf, body_col, (x, y - 5), 4)
        # Tiny horns
        pygame.draw.line(surf, (90, 0, 0), (x - 2, y - 9), (x - 4, y - 13), 2)
        pygame.draw.line(surf, (90, 0, 0), (x + 2, y - 9), (x + 4, y - 13), 2)
        # Glowing red dot eyes
        pygame.draw.circle(surf, (255, 50, 0), (x - 2, y - 5), 1)
        pygame.draw.circle(surf, (255, 50, 0), (x + 2, y - 5), 1)


class GroundDemon:
    """Red demon walking with pitchfork for Zone 9."""

    def __init__(self, y: float, idx: int = 0):
        self.x = float(random.randint(20, LEFT_W - 20))
        self.y = y
        self.dir = random.choice([-1, 1])
        self.speed = random.uniform(18, 30)
        self.t = random.uniform(0, math.pi * 2)

    def update(self, dt: float):
        self.x += self.dir * self.speed * dt
        self.t += dt * 5
        if self.x >= LEFT_W - 14:
            self.dir = -1
        elif self.x <= 14:
            self.dir = 1

    def draw(self, surf: pygame.Surface):
        x, y = int(self.x), int(self.y)
        walk = math.sin(self.t)
        leg = int(walk * 5)
        body_col = (170, 20, 20)
        # Legs
        pygame.draw.line(surf, (120, 10, 10), (x - 2, y + 2), (x - 3 + leg, y + 10), 2)
        pygame.draw.line(surf, (120, 10, 10), (x + 2, y + 2), (x + 3 - leg, y + 10), 2)
        # Body
        pygame.draw.rect(surf, body_col, (x - 4, y - 8, 8, 10), border_radius=1)
        # Tiny wings on back
        pygame.draw.polygon(surf, (100, 5, 5),
                            [(x, y - 4), (x - self.dir * 10, y - 8), (x - self.dir * 6, y)])
        # Head + horns
        pygame.draw.circle(surf, body_col, (x, y - 13), 5)
        pygame.draw.line(surf, (90, 0, 0), (x - 3, y - 18), (x - 5, y - 22), 2)
        pygame.draw.line(surf, (90, 0, 0), (x + 3, y - 18), (x + 5, y - 22), 2)
        # Glowing red eyes
        pygame.draw.circle(surf, (255, 80, 0), (x - 2, y - 13), 1)
        pygame.draw.circle(surf, (255, 80, 0), (x + 2, y - 13), 1)
        # Pitchfork held forward
        fork_x = x + self.dir * 10
        pygame.draw.line(surf, (160, 160, 160), (x + self.dir * 4, y - 5),
                         (fork_x, y - 18), 2)
        # 3 tines at top
        for tx in (fork_x - 3, fork_x, fork_x + 3):
            pygame.draw.line(surf, (180, 180, 180), (tx, y - 18), (tx, y - 23), 1)


class CrucifiedFigure:
    """Static wooden cross with stick figure — prop for Zone 9."""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def update(self, dt: float):
        pass   # static

    def draw(self, surf: pygame.Surface):
        x, y = self.x, self.y
        wood = (110, 72, 35)
        # Vertical beam
        pygame.draw.line(surf, wood, (x, y), (x, y + 50), 4)
        # Horizontal beam
        pygame.draw.line(surf, wood, (x - 22, y + 10), (x + 22, y + 10), 4)
        # Figure: arms spread along crossbeam
        pygame.draw.line(surf, _SKIN, (x - 18, y + 10), (x + 18, y + 10), 2)
        # Torso
        pygame.draw.line(surf, _SKIN, (x, y + 14), (x, y + 32), 2)
        # Head drooping
        pygame.draw.circle(surf, _SKIN, (x, y + 8), 5)
        # Legs together
        pygame.draw.line(surf, _SKIN, (x, y + 32), (x - 3, y + 44), 2)
        pygame.draw.line(surf, _SKIN, (x, y + 32), (x + 3, y + 44), 2)


# ── Seasonal sprite classes ───────────────────────────────────────────────────

class Snowflake:
    """Falling snowflake for Winter."""

    def __init__(self):
        self._reset(initial=True)

    def _reset(self, initial: bool = False):
        self.x  = float(random.randint(0, LEFT_W))
        self.y  = float(random.randint(TOP_H, TOP_H + 80) if initial else TOP_H - 4)
        self.vy = random.uniform(18, 42)
        self.vx = random.uniform(-10, 10)
        self.t  = random.uniform(0, math.tau)
        self.sz = random.randint(2, 4)

    def update(self, dt: float):
        self.t  += dt * 1.8
        self.y  += self.vy * dt
        self.x  += self.vx * dt + math.sin(self.t) * 12 * dt
        if self.y > H - TICKER_H or self.x < -6 or self.x > LEFT_W + 6:
            self._reset()

    def draw(self, surf: pygame.Surface):
        pygame.draw.circle(surf, (218, 232, 252), (int(self.x), int(self.y)), self.sz)


class HockeyPlayer(WalkingPerson):
    """Ice-hockey player with stick and helmet."""

    _JERSEYS = [(190, 20, 20), (20, 40, 190), (20, 135, 55), (160, 135, 20)]

    def __init__(self, y: int):
        super().__init__(y)
        self.shirt = random.choice(self._JERSEYS)
        self.speed = random.uniform(30, 55)

    def draw(self, surf: pygame.Surface):
        super().draw(surf)
        x, y = int(self.x), int(self.y)
        pygame.draw.arc(surf, (45, 48, 58),
                        pygame.Rect(x - 6, y - 19, 12, 8), 0, math.pi, 4)
        sx = x + self.dir * 6
        pygame.draw.line(surf, (118, 78, 38), (sx, y - 4), (sx + self.dir * 10, y + 7), 2)
        bx = sx + self.dir * 10
        pygame.draw.line(surf, (118, 78, 38), (bx - 4, y + 7), (bx + 4, y + 7), 2)


class HockeyPuck:
    """Black rubber puck — only slides when a player hits it."""

    def __init__(self, ground_y: int):
        self._gy    = float(ground_y)
        self.x      = float(LEFT_W // 2)
        self.vx     = 0.0
        self._hit_cd = 0.0

    def update(self, dt: float, players=None):
        self._hit_cd = max(0.0, self._hit_cd - dt)

        # Slide with ice friction (very low friction)
        if self.vx != 0:
            sign     = 1 if self.vx > 0 else -1
            self.vx -= sign * min(abs(self.vx), 28 * dt)
            if abs(self.vx) < 2:
                self.vx = 0.0
        self.x += self.vx * dt

        # Wall bounce
        if self.x < 16:
            self.x, self.vx = 16.0, abs(self.vx) * 0.85
        elif self.x > LEFT_W - 16:
            self.x, self.vx = float(LEFT_W - 16), -abs(self.vx) * 0.85

        # Hit detection — player stick reaches ~18 px ahead
        if players and self._hit_cd <= 0:
            for p in players:
                stick_x = p.x + p.dir * 18
                if abs(stick_x - self.x) < 16 and abs(p.y - self._gy) < 16:
                    self.vx      = p.dir * random.uniform(90, 170)
                    self._hit_cd = 1.0
                    break

    def draw(self, surf: pygame.Surface):
        pygame.draw.ellipse(surf, (28, 28, 28),
                            (int(self.x) - 5, int(self._gy) - 2, 10, 4))


class ChristmasTree:
    """Static pixel-art Christmas tree with blinking coloured lights."""

    _LIGHTS = [(255, 40, 40), (40, 215, 40), (255, 195, 0), (40, 140, 255), (255, 80, 200)]

    def __init__(self, x: int, ground_y: int):
        self.x = x
        self.y = ground_y
        self.t = random.uniform(0, math.tau)
        rng    = random
        self._bulbs = [
            (lx, ly, rng.choice(self._LIGHTS), rng.uniform(0, math.tau))
            for lx, ly in [(-8,-14),(-2,-10),(6,-9),(-4,-22),(3,-19),
                            (-1,-30),(5,-27),(-6,-18),(7,-16)]
        ]

    def update(self, dt: float):
        self.t += dt

    def draw(self, surf: pygame.Surface):
        x, y = self.x, self.y
        pygame.draw.rect(surf, (95, 58, 18), (x - 4, y - 12, 8, 12))
        for w, dy in ((36, -12), (26, -24), (16, -36)):
            pts = [(x, y + dy - 12), (x - w // 2, y + dy), (x + w // 2, y + dy)]
            pygame.draw.polygon(surf, (22, 108, 26), pts)
            pygame.draw.polygon(surf, (14, 78, 20), pts, 1)
        sy = y - 50
        for i in range(5):
            a1 = math.radians(i * 72 - 90)
            a2 = math.radians(i * 72 + 36 - 90)
            pygame.draw.polygon(surf, (255, 218, 0), [
                (x + math.cos(a1) * 5, sy + math.sin(a1) * 5),
                (x + math.cos(a2) * 2, sy + math.sin(a2) * 2),
                (x + math.cos(a1 + math.tau / 5) * 5,
                 sy + math.sin(a1 + math.tau / 5) * 5),
            ])
        for lx, ly, col, phase in self._bulbs:
            if (math.sin(self.t * 2.8 + phase) + 1) / 2 > 0.4:
                pygame.draw.circle(surf, col, (x + lx, y + ly), 2)


class SantaSleigh:
    """Periodic Santa + reindeer + sleigh flying right→left across the sky."""

    def __init__(self):
        self._timer = random.uniform(80, 160)
        self.active = False
        self.x      = float(LEFT_W + 220)
        self.y      = float(TOP_H + 38)

    def update(self, dt: float):
        if not self.active:
            self._timer -= dt
            if self._timer <= 0:
                self.active = True
                self.x      = float(LEFT_W + 220)
                self.y      = float(random.randint(TOP_H + 18, TOP_H + 68))
            return
        self.x -= 44.0 * dt
        if self.x < -260:
            self.active = False
            self._timer = random.uniform(80, 180)

    def draw(self, surf: pygame.Surface):
        if not self.active:
            return
        x, y = int(self.x), int(self.y)
        pygame.draw.line(surf, (88, 52, 24), (x - 4, y + 6), (x - 145, y + 4), 1)
        for i in range(5):
            rx = x - 40 - i * 25
            ry = y + (2 if i % 2 == 0 else -2)
            pygame.draw.ellipse(surf, (108, 62, 28), (rx, ry, 18, 8))
            pygame.draw.circle(surf, (108, 62, 28), (rx + 20, ry + 2), 4)
            for bxo, tips in ((-2, [(-2,-8),(-4,-12)]), (2, [(2,-8),(4,-12)])):
                base = (rx + 20 + bxo, ry - 2)
                pygame.draw.line(surf, (78, 46, 16), base,
                                 (rx + 20 + tips[0][0], ry + tips[0][1]), 1)
                pygame.draw.line(surf, (78, 46, 16),
                                 (rx + 20 + tips[0][0], ry + tips[0][1]),
                                 (rx + 20 + tips[1][0], ry + tips[1][1]), 1)
            pygame.draw.line(surf, (78, 46, 16), (rx + 4, ry + 8), (rx + 2, ry + 14), 1)
            pygame.draw.line(surf, (78, 46, 16), (rx + 13, ry + 8), (rx + 12, ry + 14), 1)
            if i == 0:
                pygame.draw.circle(surf, (255, 48, 48), (rx + 24, ry + 2), 2)
        pygame.draw.polygon(surf, (175, 18, 18),
                            [(x, y), (x+30, y), (x+34, y+14), (x-4, y+14)])
        pygame.draw.rect(surf, (182, 20, 20),   (x+4,  y-10, 12, 12))
        pygame.draw.circle(surf, _SKIN,          (x+10, y-14), 5)
        pygame.draw.rect(surf, (242, 242, 242), (x+3,  y-13, 13,  3))
        pygame.draw.rect(surf, (182, 20, 20),   (x+7,  y-22,  9,  9))
        pygame.draw.circle(surf, (242, 242, 242), (x+8, y-22), 3)


class SoccerPlayer(WalkingPerson):
    """Football/soccer player with coloured jersey."""

    _JERSEYS = [
        (198, 38, 38), (38, 68, 198), (28, 158, 58),
        (178, 158, 18), (138, 38, 138),
    ]

    def __init__(self, y: int):
        super().__init__(y)
        self.shirt = random.choice(self._JERSEYS)
        self.speed = random.uniform(22, 42)


class SoccerGoal:
    """Static football goal (white posts + net)."""

    def __init__(self, x: int, ground_y: int, facing_right: bool = True):
        self.x = x
        self.y = ground_y
        self.d = 1 if facing_right else -1

    def update(self, dt: float):
        pass

    def draw(self, surf: pygame.Surface):
        x, y, d = self.x, self.y, self.d
        c_post = (208, 208, 208)
        c_net  = (165, 165, 165)
        pygame.draw.line(surf, c_post, (x,       y - 22), (x,       y), 3)
        pygame.draw.line(surf, c_post, (x+d*22,  y - 22), (x+d*22,  y), 3)
        pygame.draw.line(surf, c_post, (x,       y - 22), (x+d*22,  y - 22), 3)
        for i in range(1, 5):
            pygame.draw.line(surf, c_net, (x+d*i*4, y-22), (x+d*i*4+d*2, y), 1)
        for j in (8, 15):
            pygame.draw.line(surf, c_net, (x, y-j), (x+d*22, y-j), 1)


class SoccerBall:
    """Football that only moves when a player kicks it."""

    def __init__(self, ground_y: int):
        self._gy    = float(ground_y - 5)
        self.x      = float(LEFT_W // 2)
        self.y      = self._gy
        self.vx     = 0.0
        self.vy     = 0.0
        self.t      = 0.0
        self._kick_cd = 0.0

    def update(self, dt: float, players=None):
        self.t       += dt * 5.0
        self._kick_cd = max(0.0, self._kick_cd - dt)

        # Gravity when airborne
        if self.y < self._gy or self.vy < 0:
            self.vy += 280 * dt

        self.y += self.vy * dt
        self.x += self.vx * dt

        # Ground
        if self.y >= self._gy:
            self.y = self._gy
            if abs(self.vy) > 25:
                self.vy = -abs(self.vy) * 0.52
            else:
                self.vy = 0.0

        # Rolling friction
        if self.vx != 0:
            sign = 1 if self.vx > 0 else -1
            self.vx -= sign * min(abs(self.vx), 60 * dt)
            if abs(self.vx) < 2:
                self.vx = 0.0

        # Walls
        if self.x < 26:
            self.x, self.vx = 26.0, abs(self.vx) * 0.7
        elif self.x > LEFT_W - 26:
            self.x, self.vx = float(LEFT_W - 26), -abs(self.vx) * 0.7

        # Kick when a player walks into the ball
        if players and self._kick_cd <= 0:
            for p in players:
                if abs(p.x - self.x) < 22 and abs(p.y - (self._gy + 5)) < 20:
                    pdir = getattr(p, 'dir', 1)
                    self.vx = pdir * random.uniform(75, 140)
                    self.vy = -random.uniform(55, 105)
                    self._kick_cd = 1.4
                    break

    def draw(self, surf: pygame.Surface):
        x, y = int(self.x), int(self.y)
        pygame.draw.circle(surf, (242, 242, 242), (x, y), 5)
        pygame.draw.circle(surf, (22,  22,  22),  (x, y), 5, 1)
        for i in range(5):
            a = self.t + math.tau * i / 5
            pygame.draw.circle(surf, (22, 22, 22),
                               (x + int(math.cos(a) * 2), y + int(math.sin(a) * 2)), 1)


class HalloweenStudent(WalkingPerson):
    """Student in Halloween costume: ghost / vampire / witch."""

    def __init__(self, y: int, variant: int = 0):
        super().__init__(y)
        self.variant = variant % 3

    def draw(self, surf: pygame.Surface):
        x, y  = int(self.x), int(self.y)
        walk  = math.sin(self.t)
        leg   = int(walk * 5)

        if self.variant == 0:
            ghost = pygame.Surface((24, 28), pygame.SRCALPHA)
            pygame.draw.ellipse(ghost, (228, 228, 236, 210), (0, 0, 24, 24))
            for wx in (3, 9, 15, 21):
                pygame.draw.circle(ghost, (232, 225, 198, 155), (wx, 24), 3)
            pygame.draw.circle(ghost, (18, 18, 18, 255), (8,  10), 2)
            pygame.draw.circle(ghost, (18, 18, 18, 255), (16, 10), 2)
            surf.blit(ghost, (x - 12, y - 22 + int(math.sin(self.t * 1.2) * 3)))

        elif self.variant == 1:
            pygame.draw.line(surf, (22, 22, 72), (x-2,y+2), (x-3+leg,y+10), 2)
            pygame.draw.line(surf, (22, 22, 72), (x+2,y+2), (x+3-leg,y+10), 2)
            pygame.draw.rect(surf, (28, 28, 82), (x-4, y-7, 8, 9))
            pygame.draw.polygon(surf, (68, 8, 8),
                                [(x-4*self.dir,y-7),(x-14*self.dir,y-2),(x-12*self.dir,y+2)])
            pygame.draw.circle(surf, (212, 198, 202), (x, y-13), 5)
            pygame.draw.arc(surf, (28, 28, 80),
                            pygame.Rect(x-5, y-18, 10, 8), 0, math.pi, 3)
            pygame.draw.line(surf, (238, 238, 238), (x-2, y-8), (x-2, y-5), 1)
            pygame.draw.line(surf, (238, 238, 238), (x+2, y-8), (x+2, y-5), 1)

        else:
            pygame.draw.line(surf, (32, 18, 52), (x-2,y+2), (x-3+leg,y+10), 2)
            pygame.draw.line(surf, (32, 18, 52), (x+2,y+2), (x+3-leg,y+10), 2)
            pygame.draw.rect(surf, (38, 20, 58), (x-4, y-7, 8, 9))
            pygame.draw.circle(surf, _SKIN, (x, y-13), 5)
            pygame.draw.rect(surf, (20, 10, 30), (x-7, y-18, 14, 3))
            pygame.draw.polygon(surf, (20, 10, 30), [(x, y-30),(x-5,y-18),(x+5,y-18)])
            bx = x + self.dir * 14
            pygame.draw.line(surf, (98, 60, 20), (x+self.dir*4, y-4), (bx, y+4), 2)
            pygame.draw.ellipse(surf, (128, 82, 28), (bx-3, y+2, 7, 6))


class LeafPile:
    """Static pile of autumn leaves on the ground."""

    _COLS = [(172, 96, 20), (196, 80, 16), (155, 115, 26), (215, 85, 26)]

    def __init__(self, x: int, ground_y: int):
        self.x = x
        self.y = ground_y
        rng    = random
        self._leaves = [
            (rng.randint(-13, 13), rng.randint(-5, 5), rng.choice(self._COLS))
            for _ in range(10)
        ]

    def update(self, dt: float):
        pass

    def draw(self, surf: pygame.Surface):
        for lx, ly, col in self._leaves:
            pygame.draw.ellipse(surf, col, (self.x+lx-5, self.y+ly-3, 10, 6))


class FallingLeaf:
    """Leaf particle that drifts down and resets."""

    _COLS = [(172, 96, 20), (196, 80, 16), (155, 115, 26), (215, 85, 26), (225, 58, 10)]

    def __init__(self):
        self._reset(initial=True)

    def _reset(self, initial: bool = False):
        self.x   = float(random.randint(0, LEFT_W))
        self.y   = float(random.randint(TOP_H, TOP_H + 80) if initial else TOP_H - 4)
        self.vy  = random.uniform(18, 38)
        self.vx  = random.uniform(-18, 18)
        self.t   = random.uniform(0, math.tau)
        self.col = random.choice(self._COLS)
        self.sz  = random.randint(3, 6)

    def update(self, dt: float):
        self.t  += dt * 3.0
        self.y  += self.vy * dt
        self.x  += self.vx * dt + math.sin(self.t) * 16 * dt
        if self.y > H - TICKER_H or self.x < -8 or self.x > LEFT_W + 8:
            self._reset()

    def draw(self, surf: pygame.Surface):
        x, y = int(self.x), int(self.y)
        s = self.sz
        angle = self.t % math.pi
        ca, sa = math.cos(angle), math.sin(angle)
        pts = [
            (x + int(ca*s - sa*(s//2)), y + int(sa*s + ca*(s//2))),
            (x + int(ca*s + sa*(s//2)), y + int(sa*s - ca*(s//2))),
            (x - int(ca*s - sa*(s//2)), y - int(sa*s + ca*(s//2))),
            (x - int(ca*s + sa*(s//2)), y - int(sa*s - ca*(s//2))),
        ]
        pygame.draw.polygon(surf, self.col, pts)


class KubbPlayer(WalkingPerson):
    """Kubb player — mostly stationary, periodically throws a baton."""

    def __init__(self, x: int, ground_y: int, dir_: int = 1):
        super().__init__(ground_y)
        self.x     = float(x)
        self.dir   = dir_
        self.speed = 0.0
        self._throw_t   = 0.0
        self._throw_dur = 0.0

    def throw(self, duration: float = 1.4):
        self._throw_t   = 0.0
        self._throw_dur = duration

    def update(self, dt: float):
        self.t += dt * 3
        if self._throw_dur > 0:
            self._throw_t += dt
            if self._throw_t >= self._throw_dur:
                self._throw_dur = 0.0

    def draw(self, surf: pygame.Surface):
        x, y = int(self.x), int(self.y)
        walk = math.sin(self.t)
        leg  = int(walk * 5)
        pygame.draw.circle(surf, _SKIN,  (x, y-13), 5)
        pygame.draw.arc(surf, _HAIR, pygame.Rect(x-5, y-18, 10, 8), 0, math.pi, 3)
        pygame.draw.rect(surf, self.shirt, (x-4, y-7, 8, 9))
        arm = int(walk * 4)
        pygame.draw.line(surf, _SKIN, (x-4, y-6), (x-8, y-2+arm), 2)
        pygame.draw.line(surf, _SKIN, (x+4, y-6), (x+8, y-2-arm), 2)
        pygame.draw.line(surf, _PANTS, (x-2, y+2), (x-3+leg, y+10), 2)
        pygame.draw.line(surf, _PANTS, (x+2, y+2), (x+3-leg, y+10), 2)
        pygame.draw.circle(surf, _SHOES, (x-3+leg, y+11), 2)
        pygame.draw.circle(surf, _SHOES, (x+3-leg, y+11), 2)
        if self._throw_dur > 0:
            p  = self._throw_t / self._throw_dur
            ag = math.pi / 2 - p * math.pi
            bx = x + self.dir*8 + int(math.cos(ag) * 18 * self.dir)
            by = y - 4          + int(math.sin(-ag) * 18)
            pygame.draw.line(surf, (135, 88, 38), (x+self.dir*8, y-4), (bx, by), 3)
        else:
            pygame.draw.line(surf, (135, 88, 38),
                             (x+self.dir*8, y-6), (x+self.dir*8, y-20), 3)


class KubbPin:
    """Wooden Kubb pin or king."""

    def __init__(self, x: int, ground_y: int, is_king: bool = False):
        self.x        = x
        self.ground_y = ground_y
        self.is_king  = is_king

    def update(self, dt: float):
        pass

    def draw(self, surf: pygame.Surface):
        x, y = self.x, self.ground_y
        col  = (183, 138, 43)
        edge = (163, 118, 33)
        if self.is_king:
            pygame.draw.rect(surf, col,  (x-5, y-22, 10, 22))
            pygame.draw.rect(surf, edge, (x-5, y-22, 10, 22), 1)
            for cx in (x-5, x-1, x+3):
                pygame.draw.rect(surf, col,  (cx, y-26, 3, 5))
                pygame.draw.rect(surf, edge, (cx, y-26, 3, 5), 1)
        else:
            pygame.draw.rect(surf, col,  (x-4, y-14, 8, 14))
            pygame.draw.rect(surf, edge, (x-4, y-14, 8, 14), 1)


# ── Zone 5: Moon Colony ──────────────────────────────────────────────────────

class MoonStar:
    """Twinkling star in Zone 5's dark sky."""
    def __init__(self):
        self.x   = random.randint(4, LEFT_W - 4)
        self.y   = random.randint(TOP_H + 4, TOP_H + 210)
        self.r   = random.choices([1, 2], weights=[3, 1])[0]
        self.t   = random.uniform(0, math.pi * 2)
        self.spd = random.uniform(0.4, 1.4)
        b        = random.randint(180, 255)
        self.col = (b, b, min(255, b + random.randint(0, 30)))

    def update(self, dt: float):
        self.t += self.spd * dt

    def draw(self, surf: pygame.Surface):
        bright = int(self.col[0] * (0.45 + 0.55 * (0.5 + 0.5 * math.sin(self.t))))
        pygame.draw.circle(surf, (bright, bright, min(255, bright + 20)), (self.x, self.y), self.r)


class MoonRock:
    """Static grey rock on the lunar surface."""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.w = random.randint(10, 26)
        self.h = random.randint(5, 12)
        g      = random.randint(120, 170)
        self.col = (g - 10, g, g + 10)

    def draw(self, surf: pygame.Surface):
        pygame.draw.ellipse(surf, self.col,
                            (self.x - self.w // 2, self.y - self.h, self.w, self.h))
        pygame.draw.ellipse(surf, (max(0, self.col[0] - 30),) * 3,
                            (self.x - self.w // 2, self.y - self.h, self.w, self.h), 1)


class MoonFlag:
    """Edu Empire flag planted on the moon surface."""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.t = 0.0

    def update(self, dt: float):
        self.t += dt * 0.6

    def draw(self, surf: pygame.Surface):
        x, y = self.x, self.y
        pygame.draw.line(surf, (200, 200, 210), (x, y), (x, y - 30), 2)
        pygame.draw.line(surf, (200, 200, 210), (x, y - 30), (x + 18, y - 30), 2)
        wave = int(math.sin(self.t) * 2)
        pts  = [(x, y - 30), (x + 18, y - 28 + wave), (x + 18, y - 22 + wave), (x, y - 24)]
        pygame.draw.polygon(surf, (40, 70, 200), pts)
        # Star on flag
        pygame.draw.circle(surf, (255, 210, 30), (x + 9, y - 26 + wave // 2), 3)


class Astronaut(WalkingPerson):
    """Spacesuit-clad astronaut with low-gravity bouncy walk for Zone 5."""
    _SUIT   = (228, 228, 232)
    _VISOR  = (60,  150, 220)
    _DARK   = (160, 160, 168)

    def __init__(self, y: int):
        super().__init__(y, shirt=Astronaut._SUIT)
        self.speed    = random.uniform(10, 18)   # slower in bulky suits
        self._bounce  = random.uniform(0, math.pi * 2)

    def update(self, dt: float):
        super().update(dt)
        self._bounce += dt * 0.9   # low-gravity rhythm

    def draw(self, surf: pygame.Surface):
        x  = int(self.x)
        y  = int(self.y) - int(abs(math.sin(self._bounce)) * 7)
        wk = math.sin(self.t)
        # Helmet
        pygame.draw.circle(surf, self._SUIT,  (x, y - 15), 8)
        pygame.draw.ellipse(surf, self._VISOR, (x - 4, y - 18, 9, 7))
        # Life-support backpack
        pygame.draw.rect(surf, self._DARK, (x + 4, y - 8, 5, 9), border_radius=1)
        # Torso
        pygame.draw.rect(surf, self._SUIT, (x - 6, y - 7, 11, 10), border_radius=2)
        # Arms (stubby)
        arm = int(wk * 3)
        pygame.draw.line(surf, self._SUIT, (x - 6, y - 5), (x - 10, y - 1 + arm), 3)
        pygame.draw.line(surf, self._SUIT, (x + 5, y - 5), (x + 9,  y - 1 - arm), 3)
        # Legs
        leg = int(wk * 4)
        pygame.draw.line(surf, self._DARK, (x - 3, y + 3), (x - 4 + leg, y + 12), 3)
        pygame.draw.line(surf, self._DARK, (x + 3, y + 3), (x + 4 - leg, y + 12), 3)
        # Boots
        pygame.draw.rect(surf, (120, 120, 130), (x - 7 + leg, y + 11, 6, 3), border_radius=1)
        pygame.draw.rect(surf, (120, 120, 130), (x + 1 - leg, y + 11, 6, 3), border_radius=1)


class SpriteManager:
    """Coordinates all animated sprites."""

    # Approximate horizon y for the left mini-view (TOP_H + sky_h ≈ TOP_H + ~110)
    _HORIZON_Y = TOP_H + 110

    def __init__(self):
        self.students: list = [
            ToonWalker(378, "male_person"),
            ToonWalker(372, "female_person"),
            ToonWalker(384, "male_person"),
            ToonWalker(378, "female_person"),
        ]
        self.teacher               = ToonWalker(368, "male_person", speed_range=(14, 22))
        self.clouds: list[MovingCloud] = [
            MovingCloud(TOP_H + 12, 7.0),
            MovingCloud(TOP_H + 30, 4.5),
        ]
        self.bus                   = SchoolBus()
        self.birds: list[FlyingBird]   = [FlyingBird(), FlyingBird()]
        self.decos: list[FloatingDeco] = []
        self.particles: list[TabParticle] = []
        self._p_acc = 0.0
        self._gear  = SpinningGear(W - 85, TOP_H + 130, r=26, teeth=10)
        self._tab   = ""
        self._view_zone = 1
        self.pterodactyls: list[Pterodactyl] = [SpritePterodactyl() for _ in range(3)]
        self.wing_sprites: list[WingSprite] = []
        self._wing_acc = 0.0
        self.lava_particles: list[LavaParticle] = []
        self._lava_acc = 0.0
        self.wizard_battles: list[WizardBattle] = [WizardBattle(TOP_H + 295)]
        self.flying_cars: list[FlyingCar] = [FlyingCar() for _ in range(3)]
        self.spaceship_fighters = SpaceshipFighters()
        self.flying_heroes: list[FlyingHero] = [FlyingHero(i) for i in range(3)]
        self.ground_fighters: list = [GroundFighter(TOP_H + 295, i) for i in range(3)]
        self.ghost_figures: list = [ToonWalker(TOP_H + 295, "zombie") for _ in range(3)]
        self.ancient_warriors: list = [AncientWarrior(TOP_H + 295, i) for i in range(4)]
        # Zone 3: robot ground characters
        self.z3_robots: list = [ToonWalker(TOP_H + 295, "robot") for _ in range(3)]
        self.trojan_horse = TrojanHorse()
        self.flying_angels: list = [FlyingAngel(i) for i in range(3)]
        self.halo_walkers: list = [HaloWalker(TOP_H + 295, i) for i in range(3)]
        self.flying_demons: list = [FlyingDemon(i) for i in range(3)]
        self.ground_demons: list = [GroundDemon(TOP_H + y, i) for i, y in enumerate([283, 285, 287])]
        self.crucified: list = [CrucifiedFigure(x, TOP_H + 245) for x in [198, 242, 296]]
        self._z5_t = 0.0   # celestial drift timer for Zone 5
        # Zone 5: Moon Colony
        _moon_gy = TOP_H + 295
        self.moon_stars:  list = [MoonStar() for _ in range(40)]
        self.moon_rocks:  list = [MoonRock(x, _moon_gy) for x in (40, 90, 145, 200, 260, 310)]
        self.moon_flag         = MoonFlag(60, _moon_gy)
        self.astronauts:  list = [Astronaut(_moon_gy) for _ in range(3)]
        # Seasonal sprites (zone 1)
        self._season = "Spring"
        _gy = 378
        _persons = ["male_person", "female_person"]
        self.snowflakes: list       = [Snowflake()        for _ in range(12)]
        self.hockey_players: list   = [ToonWalker(_gy, random.choice(_persons)) for _ in range(3)]
        self.hockey_puck            = HockeyPuck(_gy)
        self.christmas_tree         = ChristmasTree(36, _gy)
        self.soccer_players: list   = [ToonWalker(_gy, random.choice(_persons)) for _ in range(3)]
        self.soccer_goals: list     = [SoccerGoal(10, _gy, True),
                                        SoccerGoal(LEFT_W - 10, _gy, False)]
        self.soccer_ball            = SoccerBall(_gy)
        self.halloween_students: list = [ToonWalker(_gy, random.choice(_persons)) for _ in range(3)]
        self.leaf_piles: list       = [LeafPile(x, _gy) for x in (62, 152, 262)]
        self.falling_leaves: list   = [FallingLeaf()      for _ in range(8)]
        self.kubb_players: list     = [
            KubbPlayer(22,  _gy, dir_= 1), KubbPlayer(46,  _gy, dir_= 1),
            KubbPlayer(LEFT_W-22, _gy, dir_=-1), KubbPlayer(LEFT_W-46, _gy, dir_=-1),
        ]
        self.kubb_pins: list        = [
            KubbPin( 75, _gy), KubbPin(108, _gy), KubbPin(141, _gy),
            KubbPin(LEFT_W-75, _gy), KubbPin(LEFT_W-108, _gy), KubbPin(LEFT_W-141, _gy),
            KubbPin(LEFT_W // 2, _gy, is_king=True),
        ]
        self._kubb_throw_timer = random.uniform(3, 8)
        # Zone 1: foliage trees (Kenney Foliage Pack, side-view)
        _foliage_dir = _os.path.join(_ASSETS_DIR, "kenney_foliage-pack", "PNG", "Default size")
        self._trees: list = []
        for _fname, _th in [("foliagePack_005.png", 68), ("foliagePack_006.png", 65), ("foliagePack_011.png", 72)]:
            _path = _os.path.join(_foliage_dir, _fname)
            try:
                _raw = pygame.image.load(_path).convert_alpha()
                _scale = _th / _raw.get_height()
                _tw = int(_raw.get_width() * _scale)
                self._trees.append(pygame.transform.smoothscale(_raw, (_tw, _th)))
            except Exception:
                pass
        self._spawn_decos("Buildings")

    def _spawn_decos(self, tab: str):
        self.decos.clear()
        idx = 0
        for kind, count in _TAB_DECOS.get(tab, []):
            for _ in range(count):
                if idx >= len(_LEFT_DECO_SLOTS):
                    break
                sx, sy = _LEFT_DECO_SLOTS[idx]
                sx += random.randint(-6, 6)
                sy += random.randint(-4, 4)
                self.decos.append(FloatingDeco(sx, sy, kind, scale=4))
                idx += 1

    def update(self, dt: float, kps: float, tab: str, zone_id: int = 1, season: str = "Spring"):
        self._view_zone = zone_id
        self._season    = season

        if tab != self._tab:
            self._tab = tab
            self._spawn_decos(tab)

        for s in self.students:
            s.update(dt)
        self.teacher.update(dt)
        for b in self.birds:
            b.update(dt)
        for c in self.clouds:
            c.update(dt)
        self.bus.update(dt)
        for d in self.decos:
            d.update(dt)
        self._gear.update(dt)

        # Zone 1 seasonal sprites
        if zone_id == 1:
            if season == "Winter":
                for sf in self.snowflakes:
                    sf.update(dt)
                puck_x = self.hockey_puck.x
                for hp in self.hockey_players:
                    if abs(hp.x - puck_x) < 140:
                        hp.steer_toward(puck_x)
                    hp.update(dt)
                self.hockey_puck.update(dt, self.hockey_players)
                self.christmas_tree.update(dt)
            elif season == "Summer":
                for sp in self.soccer_players:
                    sp.update(dt)
                self.soccer_ball.update(dt, self.soccer_players)
            elif season == "Autumn":
                for hs in self.halloween_students:
                    hs.update(dt)
                for fl in self.falling_leaves:
                    fl.update(dt)
            elif season == "Spring":
                for kp in self.kubb_players:
                    kp.update(dt)
                self._kubb_throw_timer -= dt
                if self._kubb_throw_timer <= 0:
                    self._kubb_throw_timer = random.uniform(3, 8)
                    random.choice(self.kubb_players).throw(duration=1.4)

        # Zone 3: flying cars, spaceship battles, and robot ground walkers
        if zone_id == 3:
            for fc in self.flying_cars:
                fc.update(dt)
            self.spaceship_fighters.update(dt)
            for rb in self.z3_robots:
                rb.update(dt)

        # Zone 6: wizard battles
        if zone_id == 6:
            for wb in self.wizard_battles:
                wb.update(dt)

        # Zone 7: pterodactyls
        if zone_id == 7:
            for p in self.pterodactyls:
                p.update(dt)

        # Zone 8: floating wing sprites + angels + halo walkers
        if zone_id == 8:
            self._wing_acc += dt * 1.8
            while self._wing_acc >= 1.0:
                self._wing_acc -= 1.0
                self.wing_sprites.append(WingSprite())
            for w in self.wing_sprites:
                w.update(dt)
            self.wing_sprites = [w for w in self.wing_sprites if w.alive]
            if len(self.wing_sprites) > 20:
                self.wing_sprites = self.wing_sprites[-20:]
            for fa in self.flying_angels:
                fa.update(dt)
            for hw in self.halo_walkers:
                hw.update(dt)

        # Zone 9: lava particles + demons
        if zone_id == 9:
            self._lava_acc += dt * 4.0
            while self._lava_acc >= 1.0:
                self._lava_acc -= 1.0
                self.lava_particles.append(LavaParticle(self._HORIZON_Y))
            for lp in self.lava_particles:
                lp.update(dt)
            self.lava_particles = [lp for lp in self.lava_particles if lp.alive]
            if len(self.lava_particles) > 40:
                self.lava_particles = self.lava_particles[-40:]
            for fd in self.flying_demons:
                fd.update(dt)
            for gd in self.ground_demons:
                gd.update(dt)

        # Zone 10: flying heroes and ground fighters
        if zone_id == 10:
            for fh in self.flying_heroes:
                fh.update(dt)
            for gf in self.ground_fighters:
                gf.update(dt)

        # Zone 2: ghosts drift
        if zone_id == 2:
            for gf in self.ghost_figures:
                gf.update(dt)

        # Zone 4: ancient warriors + trojan horse
        if zone_id == 4:
            for aw in self.ancient_warriors:
                aw.update(dt)
            self.trojan_horse.update(dt)

        # Zone 5: moon colony
        if zone_id == 5:
            self._z5_t += dt
            for ms in self.moon_stars:
                ms.update(dt)
            self.moon_flag.update(dt)
            for ast in self.astronauts:
                ast.update(dt)

        if kps > 0.5:
            rate = min(kps / 25.0, 5.0)
            self._p_acc += rate * dt
            while self._p_acc >= 1.0:
                self._p_acc -= 1.0
                px = random.randint(LEFT_W + 20, W - 20)
                py = random.randint(150, H - TICKER_H - 40)
                self.particles.append(TabParticle(px, py))

        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]
        if len(self.particles) > 60:
            self.particles = self.particles[-60:]

    @staticmethod
    def _draw_hat(surf: pygame.Surface, walker, season: str):
        """Draw a small season-appropriate hat on top of a ToonWalker character."""
        if not hasattr(walker, '_h'):
            return
        cx   = int(walker.x)
        ty   = int(walker.y) - walker._h   # sprite top-left y (screen coords)
        hw   = walker._w // 2              # half character width (~14 px)
        nhw  = hw - 6                      # narrowed half-width: 2px hat on each side
        # Character head content starts at ~ty+9; hat sits just above it
        ht   = ty + 6
        face = getattr(walker, 'dir', 1)   # +1 facing right, -1 left

        if season == "Winter":
            # Red beanie with white band and white pompom
            pygame.draw.ellipse(surf, (190, 22, 22),  (cx - nhw, ht,     nhw*2, 8))
            pygame.draw.rect(surf,   (190, 22, 22),   (cx - nhw, ht + 4, nhw*2, 4))
            pygame.draw.rect(surf,   (240, 240, 245), (cx - nhw, ht + 7, nhw*2, 2))
            pygame.draw.circle(surf, (248, 248, 252), (cx, ht - 1), 3)

        elif season == "Summer":
            # Orange baseball cap dome + directional brim
            pygame.draw.ellipse(surf, (255, 148, 10), (cx - nhw, ht + 1, nhw*2, 7))
            pygame.draw.rect(surf,   (230, 128,  8),  (cx - nhw, ht + 5, nhw*2, 3))
            if face >= 0:
                pygame.draw.rect(surf, (210, 108, 6), (cx + nhw - 1, ht + 6, 7, 2))
            else:
                pygame.draw.rect(surf, (210, 108, 6), (cx - nhw - 6, ht + 6, 7, 2))

        elif season == "Autumn":
            # Warm orange/brown beanie with leaf pip
            pygame.draw.ellipse(surf, (172, 78, 16),  (cx - nhw, ht,     nhw*2, 8))
            pygame.draw.rect(surf,   (172, 78, 16),   (cx - nhw, ht + 4, nhw*2, 4))
            pygame.draw.rect(surf,   (208, 108, 30),  (cx - nhw, ht + 7, nhw*2, 2))
            # Small orange leaf on side
            pygame.draw.circle(surf, (205, 72, 12), (cx + nhw, ht + 3), 3)
            pygame.draw.circle(surf, (230, 110, 22),(cx + nhw, ht + 3), 1)

        elif season == "Spring":
            # Flower crown — three small blooms in pink / yellow / green
            for _ox, _pc in ((-nhw + 2, (255, 105, 160)),
                              (0,        (255, 218, 48)),
                              ( nhw - 2, (100, 205,  95))):
                pygame.draw.circle(surf, _pc,           (cx + _ox, ht + 3), 3)
                pygame.draw.circle(surf, (255, 255, 210),(cx + _ox, ht + 3), 1)

    def draw_left(self, surf: pygame.Surface):
        """Birds, students — clipped to the left panel. Zone-aware."""
        zone = self._view_zone
        surf.set_clip(pygame.Rect(0, TOP_H, LEFT_W, H - TOP_H - TICKER_H))

        if zone == 1:
            season = self._season
            for c in self.clouds:
                c.draw(surf)
            # Foliage trees at campus edges (drawn before characters)
            _tree_gy = TOP_H + 308
            for _tx, _ti in ((14, 0), (62, 2), (262, 1), (316, 0)):
                if _ti < len(self._trees):
                    _t = self._trees[_ti]
                    surf.blit(_t, (_tx - _t.get_width() // 2, _tree_gy - _t.get_height()))
            if season == "Winter":
                for sf in self.snowflakes:
                    sf.draw(surf)
                self.christmas_tree.draw(surf)
                for hp in self.hockey_players:
                    hp.draw(surf)
                    self._draw_hat(surf, hp, "Winter")
                self.hockey_puck.draw(surf)
            elif season == "Summer":
                for b in self.birds:
                    b.draw(surf)
                for goal in self.soccer_goals:
                    goal.draw(surf)
                for sp in self.soccer_players:
                    sp.draw(surf)
                    self._draw_hat(surf, sp, "Summer")
                self.soccer_ball.draw(surf)
            elif season == "Autumn":
                for b in self.birds:
                    b.draw(surf)
                for pile in self.leaf_piles:
                    pile.draw(surf)
                for fl in self.falling_leaves:
                    fl.draw(surf)
                for hs in self.halloween_students:
                    hs.draw(surf)
                    self._draw_hat(surf, hs, "Autumn")
            else:  # Spring
                for b in self.birds:
                    b.draw(surf)
                for pin in self.kubb_pins:
                    pin.draw(surf)
                for kp in self.kubb_players:
                    kp.draw(surf)
                    self._draw_hat(surf, kp, "Spring")
            for s in self.students:
                s.draw(surf)
                self._draw_hat(surf, s, season)
            self.teacher.draw(surf)
            self._draw_hat(surf, self.teacher, season)
            self.bus.draw(surf)

        elif zone == 7:
            # Zone 7: let campus view show through — pterodactyls on top
            for c in self.clouds:
                c.draw(surf)
            for p in self.pterodactyls:
                p.draw(surf)

        elif zone == 8:
            # Zone 8: golden heaven sky, pearly gates, golden temple, angels
            _GY = TOP_H + 295
            pygame.draw.rect(surf, (245, 232, 185), (0, TOP_H, LEFT_W, H - TOP_H - TICKER_H))
            pygame.draw.rect(surf, (255, 255, 252), (0, _GY, LEFT_W, H - _GY - TICKER_H))
            # Sun — upper-right, clear of the gates
            pygame.draw.circle(surf, (255, 212, 30), (LEFT_W - 52, TOP_H + 52), 30)
            pygame.draw.circle(surf, (255, 238, 120), (LEFT_W - 52, TOP_H + 52), 40, 5)
            # Golden temple — right background (rises from cloud floor)
            pygame.draw.rect(surf, (185, 150, 40), (246, _GY - 10, 90, 10))       # step
            pygame.draw.rect(surf, (210, 175, 52), (252, _GY - 68, 78, 58))       # body
            pygame.draw.polygon(surf, (230, 195, 65),
                                [(248, _GY - 68), (291, _GY - 98), (334, _GY - 68)])
            pygame.draw.circle(surf, (220, 190, 58), (291, _GY - 98), 12)         # dome crown
            for _tc in (260, 275, 300, 316):
                pygame.draw.rect(surf, (240, 235, 200), (_tc - 3, _GY - 68, 6, 58))
            # Pearly gates — center stage
            pygame.draw.polygon(surf, (210, 178, 52),
                                [(134, _GY - 130), (170, _GY - 164), (206, _GY - 130)])
            pygame.draw.polygon(surf, (235, 208, 90),
                                [(140, _GY - 130), (170, _GY - 158), (200, _GY - 130)])
            pygame.draw.circle(surf, (255, 245, 130), (170, _GY - 167), 6)        # crown star
            pygame.draw.rect(surf, (235, 235, 245), (134, _GY - 130, 18, 130))    # left pillar
            pygame.draw.rect(surf, (190, 188, 200), (134, _GY - 130, 18, 130), 2)
            pygame.draw.rect(surf, (210, 210, 225), (137, _GY - 128, 12, 4))      # capital
            pygame.draw.rect(surf, (235, 235, 245), (188, _GY - 130, 18, 130))    # right pillar
            pygame.draw.rect(surf, (190, 188, 200), (188, _GY - 130, 18, 130), 2)
            pygame.draw.rect(surf, (210, 210, 225), (191, _GY - 128, 12, 4))
            for _gb in range(158, 190, 7):                                          # gate bars
                pygame.draw.line(surf, (215, 182, 55), (_gb, _GY - 118), (_gb, _GY - 8), 2)
            # Fluffy cloud horizon — overlapping circles mask the flat edge
            for cx in range(0, LEFT_W + 30, 28):
                pygame.draw.circle(surf, (255, 255, 255), (cx, _GY), 18)
            for c in self.clouds:
                c.draw(surf)
            for w in self.wing_sprites:
                w.draw(surf)
            for fa in self.flying_angels:
                fa.draw(surf)
            for hw in self.halo_walkers:
                hw.draw(surf)

        elif zone == 9:
            # Zone 9: near-black hellscape, dark fortress, skulls, lava, demons
            _GY = TOP_H + 295
            pygame.draw.rect(surf, (22, 4, 4),  (0, TOP_H, LEFT_W, H - TOP_H - TICKER_H))
            pygame.draw.rect(surf, (38, 8, 4),  (0, _GY, LEFT_W, H - _GY - TICKER_H))
            # Faint red glow in upper sky
            pygame.draw.rect(surf, (38, 6, 4),  (0, TOP_H,      LEFT_W, 60))
            pygame.draw.rect(surf, (30, 5, 4),  (0, TOP_H + 60, LEFT_W, 60))
            # Distant spire silhouettes (right background)
            for _spx, _sph, _spw in ((210,150,10),(228,130,8),(248,162,10),(268,138,8),(288,145,10)):
                pygame.draw.rect(surf, (28, 10, 10), (_spx, _GY - _sph, _spw, _sph))
                pygame.draw.polygon(surf, (28, 10, 10),
                                    [(_spx - 2, _GY - _sph),
                                     (_spx + _spw // 2, _GY - _sph - 28),
                                     (_spx + _spw + 2, _GY - _sph)])
            # Dark fortress — left/center
            pygame.draw.rect(surf, (38, 30, 30), (14, _GY - 168, 32, 168))        # left tower
            pygame.draw.polygon(surf, (32, 25, 25),
                                [(10, _GY - 168), (30, _GY - 200), (50, _GY - 168)])
            for _mx in (16, 24, 32, 38):
                pygame.draw.rect(surf, (22, 4, 4), (_mx, _GY - 170, 6, 10))       # merlons
            pygame.draw.rect(surf, (35, 28, 28), (46, _GY - 118, 105, 118))       # castle body
            for _mx in range(50, 148, 14):
                pygame.draw.rect(surf, (22, 4, 4), (_mx, _GY - 120, 10, 10))
            for _wx in (58, 82, 112, 132):
                pygame.draw.rect(surf, (22, 4, 4), (_wx, _GY - 90, 4, 14))        # arrow slits
            pygame.draw.rect(surf, (18, 3, 3), (88, _GY - 44, 22, 44))            # doorway
            pygame.draw.circle(surf, (18, 3, 3), (99, _GY - 44), 11)
            pygame.draw.rect(surf, (38, 30, 30), (151, _GY - 148, 30, 148))       # right tower
            pygame.draw.polygon(surf, (32, 25, 25),
                                [(147, _GY - 148), (166, _GY - 184), (185, _GY - 148)])
            for _mx in (153, 161, 169, 177):
                pygame.draw.rect(surf, (22, 4, 4), (_mx, _GY - 150, 6, 10))
            # Skull decorations along ground
            for _skx in (55, 105, 175, 248, 295):
                pygame.draw.circle(surf, (78, 70, 66), (_skx, _GY + 10), 10)
                pygame.draw.rect(surf, (78, 70, 66), (_skx - 8, _GY + 12, 16, 10))
                pygame.draw.circle(surf, (22, 4, 4), (_skx - 4, _GY + 10), 3)
                pygame.draw.circle(surf, (22, 4, 4), (_skx + 4, _GY + 10), 3)
            # Lava crack lines at ground edge (thin, glowing)
            for lx, lw2 in ((25, 40), (88, 30), (160, 50), (232, 36), (292, 28)):
                pygame.draw.line(surf, (185, 35, 5), (lx, _GY + 1), (lx + lw2, _GY + 2), 3)
                pygame.draw.line(surf, (255, 90, 20), (lx + 4, _GY + 1), (lx + lw2 - 4, _GY + 1), 1)
            for lp in self.lava_particles:
                lp.draw(surf)
            for fd in self.flying_demons:
                fd.draw(surf)
            for gd in self.ground_demons:
                gd.draw(surf)
            for cf in self.crucified:
                cf.draw(surf)

        elif zone == 6:
            # Zone 6: magical realm — gradient sky, portal orb, sparkle stars, vivid crystals
            _GY = TOP_H + 295
            # Sky gradient — deep dark-purple at top, slightly warmer near horizon
            pygame.draw.rect(surf, (5,  1, 16),  (0, TOP_H,       LEFT_W, 60))
            pygame.draw.rect(surf, (10, 2, 28),  (0, TOP_H + 60,  LEFT_W, 60))
            pygame.draw.rect(surf, (14, 4, 36),  (0, TOP_H + 120, LEFT_W, 60))
            pygame.draw.rect(surf, (18, 6, 44),  (0, TOP_H + 180, LEFT_W, 60))
            pygame.draw.rect(surf, (22, 8, 52),  (0, TOP_H + 240, LEFT_W, 55))
            # Aurora-like color bands across sky
            pygame.draw.rect(surf, (0,  50, 68),  (0, TOP_H + 52,  LEFT_W, 12))
            pygame.draw.rect(surf, (44, 0,  76),  (0, TOP_H + 130, LEFT_W, 9))
            pygame.draw.rect(surf, (0,  36, 60),  (0, TOP_H + 202, LEFT_W, 7))
            # Magical portal orb — upper-left sky
            pygame.draw.circle(surf, (25, 5,  70),   (68, TOP_H + 58), 30)
            pygame.draw.circle(surf, (70, 15, 150),  (68, TOP_H + 58), 30, 4)
            pygame.draw.circle(surf, (110, 35, 210), (68, TOP_H + 58), 35, 3)
            pygame.draw.circle(surf, (155, 70, 255), (68, TOP_H + 58), 40, 2)
            for _pr in (10, 18, 26):
                pygame.draw.circle(surf, (85, 35, 170), (68, TOP_H + 58), _pr, 1)
            # Magical sparkle stars scattered in sky
            for _spx, _spy, _spc in (
                (22,  TOP_H + 20,  (180, 100, 255)),
                (118, TOP_H + 14,  (100, 210, 255)),
                (158, TOP_H + 42,  (255, 120, 210)),
                (198, TOP_H + 16,  (100, 255, 200)),
                (242, TOP_H + 32,  (200, 150, 255)),
                (286, TOP_H + 10,  (160, 255, 160)),
                (320, TOP_H + 50,  (255, 160, 120)),
                (42,  TOP_H + 130, (80,  200, 255)),
                (172, TOP_H + 112, (255, 100, 200)),
                (312, TOP_H + 118, (180,  80, 255)),
                (136, TOP_H + 70,  (255, 220, 100)),
                (268, TOP_H + 80,  (100, 255, 160)),
            ):
                pygame.draw.circle(surf, _spc,            (_spx, _spy), 2)
                pygame.draw.circle(surf, (255, 255, 255), (_spx, _spy), 1)
            # Dark magical ground — deep blue-teal, not green
            pygame.draw.rect(surf, (5, 15, 24),  (0, _GY, LEFT_W, H - _GY - TICKER_H))
            pygame.draw.rect(surf, (0, 88, 120), (0, _GY, LEFT_W, 3))
            # Crystal formations — 3 colour families: violet, teal, magenta
            _crystals = [
                (28,  155, (50, 14, 100), (140, 65, 215), (205, 125, 255)),
                (68,  88,  (14, 55, 80),  (45, 155, 195), (90,  215, 255)),
                (108, 148, (75, 8,  88),  (175, 28, 195), (235, 75,  255)),
                (150, 115, (14, 26, 88),  (45,  75, 205), (95,  145, 255)),
                (200, 152, (50, 14, 100), (140, 65, 215), (205, 125, 255)),
                (252, 98,  (14, 55, 80),  (45, 155, 195), (90,  215, 255)),
                (302, 130, (75, 8,  88),  (175, 28, 195), (235, 75,  255)),
            ]
            for _cx, _ch, _col, _edge, _tip in _crystals:
                _mid_y = _GY - _ch // 3
                _pts = [(_cx, _GY + 6), (_cx - 13, _mid_y),
                        (_cx, _GY - _ch), (_cx + 13, _mid_y)]
                pygame.draw.polygon(surf, _col, _pts)
                pygame.draw.polygon(surf, _edge, _pts, 2)
                _inner = [(_cx, _GY - _ch + 10), (_cx - 6, _mid_y - 8),
                          (_cx, _mid_y - 22),     (_cx + 6, _mid_y - 8)]
                pygame.draw.polygon(surf, _edge, _inner)
                pygame.draw.circle(surf, _tip, (_cx, _GY - _ch), 5)
                pygame.draw.ellipse(surf, (_edge[0]//3, _edge[1]//3, _edge[2]//3),
                                    (_cx - 14, _GY + 1, 28, 8))
            for c in self.clouds:
                c.draw(surf)
            for wb in self.wizard_battles:
                wb.draw(surf)

        elif zone == 3:
            # Zone 3: dark sci-fi sky, neon towers, energy columns, tech ground
            _GY = TOP_H + 295
            pygame.draw.rect(surf, (6, 10, 24),   (0, TOP_H, LEFT_W, H - TOP_H - TICKER_H))
            pygame.draw.rect(surf, (14, 18, 38),  (0, _GY, LEFT_W, H - _GY - TICKER_H))
            # Neon horizon line
            pygame.draw.rect(surf, (0, 180, 255), (0, _GY, LEFT_W, 2))
            # Perspective grid on ground
            for gx in range(0, LEFT_W + 1, 38):
                pygame.draw.line(surf, (0, 40, 88), (gx, _GY), (LEFT_W // 2, H - TICKER_H))
            for gy in range(_GY + 28, H - TICKER_H, 32):
                pygame.draw.line(surf, (0, 40, 88), (0, gy), (LEFT_W, gy))
            # Futuristic towers — sleek glass spires with neon edges
            for tx, tw, th in [(8,18,180),(44,14,140),(80,20,200),(128,12,115),
                                (162,22,170),(208,15,145),(254,18,185),(292,14,125)]:
                # Tower body (dark glass)
                pygame.draw.rect(surf, (16, 28, 55), (tx, _GY - th, tw, th))
                # Neon edge highlights
                pygame.draw.line(surf, (0, 160, 255), (tx, _GY - th), (tx, _GY), 1)
                pygame.draw.line(surf, (0, 160, 255), (tx + tw, _GY - th), (tx + tw, _GY), 1)
                # Glowing spire top
                pygame.draw.polygon(surf, (0, 200, 255),
                                    [(tx + tw//2, _GY - th - 18),
                                     (tx, _GY - th), (tx + tw, _GY - th)])
                # Horizontal neon window bands
                for wy in range(_GY - th + 12, _GY - 8, 18):
                    pygame.draw.rect(surf, (0, 100, 200), (tx + 2, wy, tw - 4, 3))
                # Antenna beacon at top
                pygame.draw.circle(surf, (0, 240, 255), (tx + tw // 2, _GY - th - 20), 3)
            for c in self.clouds:
                c.draw(surf)
            for fc in self.flying_cars:
                fc.draw(surf)
            self.spaceship_fighters.draw(surf)
            for rb in self.z3_robots:
                rb.draw(surf)

        elif zone == 10:
            # Zone 10: let campus view show through — heroes on top
            for c in self.clouds:
                c.draw(surf)
            for fh in self.flying_heroes:
                fh.draw(surf)
            for gf in self.ground_fighters:
                gf.draw(surf)

        elif zone == 2:
            # Zone 2: sandy sky, stone ground, ruined columns with cracks
            _GY = TOP_H + 295
            pygame.draw.rect(surf, (196, 162, 102), (0, TOP_H, LEFT_W, H - TOP_H - TICKER_H))
            pygame.draw.rect(surf, (145, 118, 72),  (0, _GY, LEFT_W, H - _GY - TICKER_H))
            pygame.draw.rect(surf, (108, 86, 50),   (0, _GY, LEFT_W, 4))
            # Scattered rubble along ground edge
            for rx in range(12, LEFT_W - 12, 30):
                rw2 = 8 + ((rx * 7) % 10)
                rh2 = 4 + ((rx * 11) % 5)
                pygame.draw.rect(surf, (165, 138, 88), (rx, _GY - rh2, rw2, rh2))
            # Ruined columns — tall, reaching into sky
            for cx in (42, 148, 258):
                col_top = TOP_H + 70
                pygame.draw.rect(surf, (172, 150, 100), (cx - 7, col_top, 14, _GY - col_top))
                # Capital (top slab)
                pygame.draw.rect(surf, (152, 130, 84), (cx - 10, col_top - 6, 20, 8))
                # Base
                pygame.draw.rect(surf, (152, 130, 84), (cx - 9, _GY - 5, 18, 6))
                # Cracks
                pygame.draw.line(surf, (118, 96, 58),
                                 (cx - 1, col_top + 40), (cx + 5, col_top + 90), 1)
                pygame.draw.line(surf, (118, 96, 58),
                                 (cx + 2, col_top + 100), (cx - 3, col_top + 140), 1)
            for c in self.clouds:
                c.draw(surf)
            for gf in self.ghost_figures:
                gf.draw(surf)

        elif zone == 4:
            # Zone 4: clear Mediterranean sky, marble plaza, intact columns
            _GY = TOP_H + 295
            pygame.draw.rect(surf, (88, 155, 205),  (0, TOP_H, LEFT_W, H - TOP_H - TICKER_H))
            pygame.draw.rect(surf, (210, 198, 165),  (0, _GY, LEFT_W, H - _GY - TICKER_H))
            pygame.draw.rect(surf, (185, 172, 140),  (0, _GY, LEFT_W, 4))
            # Marble tile lines on ground
            for ty in range(_GY + 20, _GY + 80, 28):
                pygame.draw.line(surf, (195, 183, 150), (0, ty), (LEFT_W, ty), 1)
            for tx in range(0, LEFT_W, 45):
                pygame.draw.line(surf, (195, 183, 150), (tx, _GY), (tx, _GY + 80), 1)
            # Intact marble columns — full height
            for cx in (32, 160, 288):
                col_top = TOP_H + 55
                pygame.draw.rect(surf, (238, 230, 210), (cx - 6, col_top, 12, _GY - col_top))
                # Fluted detail (vertical lines)
                for fx in (cx - 3, cx, cx + 3):
                    pygame.draw.line(surf, (218, 210, 190),
                                     (fx, col_top + 8), (fx, _GY - 6), 1)
                # Capital
                pygame.draw.rect(surf, (218, 208, 188), (cx - 10, col_top - 7, 20, 9))
                # Base
                pygame.draw.rect(surf, (218, 208, 188), (cx - 9,  _GY - 6,    18, 7))
            for c in self.clouds:
                c.draw(surf)
            for aw in self.ancient_warriors:
                aw.draw(surf)
            self.trojan_horse.draw(surf)

        elif zone == 5:
            # Zone 5: dark space sky, stars, Earth, Sun, moon surface, astronauts
            pygame.draw.rect(surf, (6, 6, 18),
                             (0, TOP_H, LEFT_W, H - TOP_H - TICKER_H))
            for ms in self.moon_stars:
                ms.draw(surf)
            # Earth — upper-right sky, slowly drifting (simulated lunar rotation)
            _t = self._z5_t
            ex = LEFT_W - 68 + int(12 * math.sin(_t * 0.08))
            ey = TOP_H + 68 + int(6 * math.cos(_t * 0.06))
            er = 44
            pygame.draw.circle(surf, (25, 75, 195), (ex, ey), er)
            pygame.draw.ellipse(surf, (60, 150, 55), (ex - 20, ey - 30, 22, 30))
            pygame.draw.ellipse(surf, (55, 140, 50), (ex + 5,  ey - 35, 20, 25))
            pygame.draw.ellipse(surf, (65, 145, 55), (ex - 10, ey + 5,  25, 20))
            pygame.draw.ellipse(surf, (70, 140, 50), (ex + 10, ey + 8,  18, 16))
            pygame.draw.circle(surf, (120, 180, 255), (ex, ey), er + 4, 3)
            # Sun — upper-left sky, smaller (farther away), slowly drifting with rotating rays
            sx = 50 + int(18 * math.sin(_t * 0.05 + 1.2))
            sy = TOP_H + 50 + int(8 * math.cos(_t * 0.04 + 0.8))
            sr = 13
            _ray_off = _t * 12.0
            for _a in range(0, 360, 45):
                _r = math.radians(_a + _ray_off)
                pygame.draw.line(surf, (255, 220, 30),
                                 (sx + int((sr + 3) * math.cos(_r)),
                                  sy + int((sr + 3) * math.sin(_r))),
                                 (sx + int((sr + 10) * math.cos(_r)),
                                  sy + int((sr + 10) * math.sin(_r))), 2)
            pygame.draw.circle(surf, (255, 230, 50), (sx, sy), sr)
            pygame.draw.circle(surf, (255, 255, 200), (sx, sy), sr - 5)
            # Grey moon surface strip
            pygame.draw.rect(surf, (130, 128, 140),
                             (0, TOP_H + 296, LEFT_W, H - TOP_H - TICKER_H - 296))
            for mr in self.moon_rocks:
                mr.draw(surf)
            self.moon_flag.draw(surf)
            for ast in self.astronauts:
                ast.draw(surf)

        surf.set_clip(None)

    def draw_right(self, surf: pygame.Surface, tab: str):
        """Particles (and gear on Settings) over the right panel."""
        surf.set_clip(pygame.Rect(LEFT_W, TOP_H, W - LEFT_W, H - TOP_H - TICKER_H))
        for p in self.particles:
            p.draw(surf)
        if tab == "Settings":
            self._gear.draw(surf)
        surf.set_clip(None)
