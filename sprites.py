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
    """Pixel-art school bus that occasionally drives across the bottom of the panel."""

    def __init__(self):
        self._bus_timer = random.uniform(25, 60)
        self.active     = False
        self.x          = -90.0
        self.y          = float(TOP_H + 316)

    def update(self, dt: float):
        if not self.active:
            self._bus_timer -= dt
            if self._bus_timer <= 0:
                self.active = True
                self.x      = -90.0
            return
        self.x += 68.0 * dt
        if self.x > LEFT_W + 10:
            self.active     = False
            self._bus_timer = random.uniform(40, 90)

    def draw(self, surf: pygame.Surface):
        if not self.active:
            return
        x, y = int(self.x), int(self.y)
        pygame.draw.rect(surf, _YELLOW,  (x,      y - 18, 80, 18))
        pygame.draw.rect(surf, (180, 140, 10), (x, y - 18, 80, 18), 1)
        pygame.draw.rect(surf, _DARK,    (x,      y - 18, 18, 18))
        for wx in (22, 38, 54, 68):
            pygame.draw.rect(surf, _BUS_WIN, (x + wx, y - 15, 10, 10))
        pygame.draw.circle(surf, _DARK, (x + 14, y + 2), 6)
        pygame.draw.circle(surf, _DARK, (x + 62, y + 2), 6)
        pygame.draw.circle(surf, (80, 80, 80), (x + 14, y + 2), 3)
        pygame.draw.circle(surf, (80, 80, 80), (x + 62, y + 2), 3)


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
        # Left wizard — purple robes
        pygame.draw.rect(surf, (100,30,140), (10, y-20, 14, 22))
        pygame.draw.circle(surf, (220,180,140), (17, y-24), 6)
        pygame.draw.polygon(surf, (80,20,120), [(12,y-30),(17,y-42),(22,y-30)])
        # Right wizard — dark red warlock
        pygame.draw.rect(surf, (140,20,20), (LEFT_W-24, y-20, 14, 22))
        pygame.draw.circle(surf, (220,180,140), (LEFT_W-17, y-24), 6)
        pygame.draw.polygon(surf, (120,10,10), [(LEFT_W-22,y-30),(LEFT_W-17,y-42),(LEFT_W-12,y-30)])
        # Spell projectile
        if self.spell_timer >= self.cast_cooldown * 0.3:
            col = self.spell_color
            pygame.draw.circle(surf, col, (int(self.spell_x), y-12), 4)
            pygame.draw.circle(surf, (255,255,255), (int(self.spell_x), y-12), 2)


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
    """Black rubber puck sliding on ice."""

    def __init__(self, ground_y: int):
        self._gy = float(ground_y)
        self.x   = float(random.randint(30, LEFT_W - 30))
        self.vx  = random.uniform(-75, 75)

    def update(self, dt: float):
        self.x += self.vx * dt
        if self.x < 16:
            self.x, self.vx = 16.0, abs(self.vx)
        elif self.x > LEFT_W - 16:
            self.x, self.vx = float(LEFT_W - 16), -abs(self.vx)

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
    """Bouncing football."""

    def __init__(self, ground_y: int):
        self._gy = float(ground_y - 5)
        self.x   = float(random.randint(40, LEFT_W - 40))
        self.y   = self._gy
        self.vx  = random.uniform(-85, 85)
        self.vy  = 0.0
        self.t   = 0.0

    def update(self, dt: float):
        self.t  += dt * 5.0
        self.vy += 280 * dt
        self.y  += self.vy * dt
        self.x  += self.vx * dt
        if self.y >= self._gy:
            self.y  = self._gy
            self.vy = -abs(self.vy) * 0.55
            if abs(self.vy) < 15:
                self.vy = -random.uniform(28, 75)
                self.vx = random.uniform(-85, 85)
        if self.x < 26:
            self.x, self.vx = 26.0, abs(self.vx) * 0.8
        elif self.x > LEFT_W - 26:
            self.x, self.vx = float(LEFT_W - 26), -abs(self.vx) * 0.8

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


class SpriteManager:
    """Coordinates all animated sprites."""

    # Approximate horizon y for the left mini-view (TOP_H + sky_h ≈ TOP_H + ~110)
    _HORIZON_Y = TOP_H + 110

    def __init__(self):
        self.students: list[WalkingPerson] = [
            WalkingPerson(378, _BLUE),
            WalkingPerson(372, _RED),
            WalkingPerson(384, _BLUE),
        ]
        self.teacher               = TeacherCharacter(368)
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
        self.wizard_battles: list[WizardBattle] = [
            WizardBattle(TOP_H + 200),
            WizardBattle(TOP_H + 260),
            WizardBattle(TOP_H + 300),
        ]
        self.flying_cars: list[FlyingCar] = [FlyingCar() for _ in range(3)]
        self.spaceship_fighters = SpaceshipFighters()
        self.flying_heroes: list[FlyingHero] = [FlyingHero(i) for i in range(3)]
        self.ground_fighters: list[GroundFighter] = [
            GroundFighter(TOP_H + 215, 0),
            GroundFighter(TOP_H + 250, 1),
            GroundFighter(TOP_H + 285, 2),
        ]
        self.ghost_figures: list = [GhostFigure(i) for i in range(3)]
        self.ancient_warriors: list = [AncientWarrior(TOP_H + 295, i) for i in range(4)]
        self.trojan_horse = TrojanHorse()
        self.flying_angels: list = [FlyingAngel(i) for i in range(3)]
        self.halo_walkers: list = [HaloWalker(TOP_H + 295, i) for i in range(3)]
        self.flying_demons: list = [FlyingDemon(i) for i in range(3)]
        self.ground_demons: list = [GroundDemon(TOP_H + y, i) for i, y in enumerate([250, 290, 320])]
        self.crucified: list = [CrucifiedFigure(x, TOP_H + 235) for x in [55, 170, 285]]
        # Seasonal sprites (zone 1)
        self._season = "Spring"
        _gy = 378
        self.snowflakes: list       = [Snowflake()        for _ in range(12)]
        self.hockey_players: list   = [HockeyPlayer(_gy)  for _ in range(3)]
        self.hockey_puck            = HockeyPuck(_gy)
        self.christmas_tree         = ChristmasTree(36, _gy)
        self.santa_sleigh           = SantaSleigh()
        self.soccer_players: list   = [SoccerPlayer(_gy)  for _ in range(3)]
        self.soccer_goals: list     = [SoccerGoal(10, _gy, True),
                                        SoccerGoal(LEFT_W - 10, _gy, False)]
        self.soccer_ball            = SoccerBall(_gy)
        self.halloween_students: list = [HalloweenStudent(_gy, i) for i in range(3)]
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
                for hp in self.hockey_players:
                    hp.update(dt)
                self.hockey_puck.update(dt)
                self.christmas_tree.update(dt)
                self.santa_sleigh.update(dt)
            elif season == "Summer":
                for sp in self.soccer_players:
                    sp.update(dt)
                self.soccer_ball.update(dt)
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

        # Zone 3: flying cars and spaceship battles
        if zone_id == 3:
            for fc in self.flying_cars:
                fc.update(dt)
            self.spaceship_fighters.update(dt)

        # Zone 6: wizard battles
        if zone_id == 6:
            for wb in self.wizard_battles:
                wb.update(dt)

        # Zone 7: pterodactyls
        if zone_id == 7:
            for p in self.pterodactyls:
                p.update(dt)

        # Zone 8: wing sprites
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

        # Zone 9: lava particles
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

        # Zone 8: angels + halo walkers
        if zone_id == 8:
            for fa in self.flying_angels:
                fa.update(dt)
            for hw in self.halo_walkers:
                hw.update(dt)

        # Zone 9: demons (lava already handled above)
        if zone_id == 9:
            for fd in self.flying_demons:
                fd.update(dt)
            for gd in self.ground_demons:
                gd.update(dt)

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

    def draw_left(self, surf: pygame.Surface):
        """Birds, students — clipped to the left panel. Zone-aware."""
        zone = self._view_zone
        surf.set_clip(pygame.Rect(0, TOP_H, LEFT_W, H - TOP_H - TICKER_H))

        if zone == 1:
            season = self._season
            for c in self.clouds:
                c.draw(surf)
            if season == "Winter":
                for sf in self.snowflakes:
                    sf.draw(surf)
                self.santa_sleigh.draw(surf)
                self.christmas_tree.draw(surf)
                for hp in self.hockey_players:
                    hp.draw(surf)
                self.hockey_puck.draw(surf)
            elif season == "Summer":
                for b in self.birds:
                    b.draw(surf)
                for goal in self.soccer_goals:
                    goal.draw(surf)
                for sp in self.soccer_players:
                    sp.draw(surf)
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
            else:  # Spring
                for b in self.birds:
                    b.draw(surf)
                for pin in self.kubb_pins:
                    pin.draw(surf)
                for kp in self.kubb_players:
                    kp.draw(surf)
            self.teacher.draw(surf)
            self.bus.draw(surf)

        elif zone == 7:
            # Zone 7: pterodactyls instead of birds
            for c in self.clouds:
                c.draw(surf)
            for p in self.pterodactyls:
                p.draw(surf)

        elif zone == 8:
            # Zone 8: angel wings float upward, plus angels and halo walkers
            for c in self.clouds:
                c.draw(surf)
            for w in self.wing_sprites:
                w.draw(surf)
            for fa in self.flying_angels:
                fa.draw(surf)
            for hw in self.halo_walkers:
                hw.draw(surf)

        elif zone == 9:
            # Zone 9: lava particles drifting up, plus demons and crosses
            for lp in self.lava_particles:
                lp.draw(surf)
            for fd in self.flying_demons:
                fd.draw(surf)
            for gd in self.ground_demons:
                gd.draw(surf)
            for cf in self.crucified:
                cf.draw(surf)

        elif zone == 6:
            # Zone 6: sparkle clouds + wizard battles
            for c in self.clouds:
                c.draw(surf)
            for wb in self.wizard_battles:
                wb.draw(surf)

        elif zone == 3:
            # Zone 3: futuristic sky — flying cars and spaceship battle
            for c in self.clouds:
                c.draw(surf)
            for fc in self.flying_cars:
                fc.draw(surf)
            self.spaceship_fighters.draw(surf)

        elif zone == 10:
            # Zone 10: flying heroes soar above ground fighters
            for c in self.clouds:
                c.draw(surf)
            for fh in self.flying_heroes:
                fh.draw(surf)
            for gf in self.ground_fighters:
                gf.draw(surf)

        elif zone == 2:
            # Zone 2: clouds + drifting ghosts
            for c in self.clouds:
                c.draw(surf)
            for gf in self.ghost_figures:
                gf.draw(surf)

        elif zone == 4:
            # Zone 4: clouds + ancient warriors + trojan horse
            for c in self.clouds:
                c.draw(surf)
            for aw in self.ancient_warriors:
                aw.draw(surf)
            self.trojan_horse.draw(surf)

        else:
            # Zone 5: no clouds (moon has no atmosphere)
            pass

        surf.set_clip(None)

    def draw_right(self, surf: pygame.Surface, tab: str):
        """Particles (and gear on Settings) over the right panel."""
        surf.set_clip(pygame.Rect(LEFT_W, TOP_H, W - LEFT_W, H - TOP_H - TICKER_H))
        for p in self.particles:
            p.draw(surf)
        if tab == "Settings":
            self._gear.draw(surf)
        surf.set_clip(None)
