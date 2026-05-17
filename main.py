import pygame
import sys
import time
from typing import Optional
import audio
import sprites as spr
from campus import CampusView

from data import (BUILDINGS, UPGRADES, SKILLS, ACHIEVEMENTS, NEWS,
                  EVENTS, STORY, SYNERGIES, DIPLOMA_UPGRADES,
                  HONOR_UPGRADES, ENDOW_UPGRADES, ALUMNI_UPGRADES, SCHOLARS,
                  BUILDING_SACRIFICE, CW_SHOP, COSMETIC_THEMES,
                  QUIZ_QUESTIONS, QUIZ_REWARDS)
from game import Game, fmt, COMBO_WINDOW, FOCUS_ABILITIES
from world import WorldManager
from zones_data import ZONE_DEFS

audio.pre_init()
pygame.init()
pygame.font.init()
audio.init()

# ── Window ────────────────────────────────────────────────────────────────────
VERSION    = "0.12.0"
W, H       = 1280, 760
LEFT_W     = 340
TOP_H      = 72
TICKER_H   = 28
CONTENT_Y  = TOP_H + 46
CONTENT_H  = H - CONTENT_Y - TICKER_H
FPS        = 60

# ── Palette ───────────────────────────────────────────────────────────────────
BG         = (245, 245, 240)
PANEL      = (228, 222, 210)
TOPBAR     = (38,  68, 108)
TICKER_BG  = (28,  52,  86)
ACCENT     = (65, 124, 175)
GREEN      = (52, 155, 70)
GRAY       = (145, 145, 145)
DARK       = (35,  35,  35)
WHITE      = (255, 255, 255)
CREAM      = (250, 248, 244)
GOLD       = (218, 165, 30)
LBLUE      = (168, 212, 228)
CARD_OK    = (238, 233, 222)
CARD_DIM   = (216, 210, 198)
CARD_LOCK  = (196, 190, 180)
PRESTIGE   = (148,  48, 148)
MERIT      = (42,  148, 148)
ENDOW_COL  = (42,  180, 148)
ALUMNI_COL = (130,  80, 210)
SANDBOX_C  = (210,  50,  50)

GRADE_COL = {
    "A+": (218, 165, 30),
    "A":  (60,  160, 80),
    "B+": (65,  124, 175),
    "B":  (100, 140, 190),
    "C":  (130, 130, 130),
    "S":  (210, 100, 30),
    "S+": (200,  40, 160),
}

PATH_BG = {
    "Foundation": (205, 205, 210),
    "Academic":   (200, 220, 242),
    "Innovation": (200, 238, 210),
    "Prestige":   (230, 210, 242),
    "Active":     (245, 225, 200),
    "Mastery":    (255, 240, 180),
}
PATH_FG = {
    "Foundation": (55,  55,  65),
    "Academic":   (38,  88, 148),
    "Innovation": (30, 118,  52),
    "Prestige":   (98,  28, 118),
    "Active":     (148,  76,  18),
    "Mastery":    (140,  90,   0),
}
PATH_LABELS = {
    "Foundation": "Foundation Skills",
    "Academic":   "Academic Excellence  (requires Valedictorian)",
    "Innovation": "Innovation Path  (requires Tech Savvy)",
    "Prestige":   "Prestige Mastery  (requires Scholarship)",
    "Active":     "Active Learning  (open to all)",
    "Mastery":    "Mastery Path  (requires Perfect Score — very expensive)",
}

# ── Fonts ─────────────────────────────────────────────────────────────────────
F_SM = pygame.font.SysFont("DejaVu Sans", 13)
F_MD = pygame.font.SysFont("DejaVu Sans", 17)
F_LG = pygame.font.SysFont("DejaVu Sans", 21, bold=True)
F_XL = pygame.font.SysFont("DejaVu Sans", 28, bold=True)
F_XS = pygame.font.SysFont("DejaVu Sans", 11)

AUTO_SAVE_INTERVAL = 30.0

SEASON_COL = {'Spring': (100, 185, 80), 'Summer': (220, 170, 30),
              'Autumn': (195, 110, 45), 'Winter': (90, 145, 210)}
SEASON_BONUS = {'Spring': '+8% KPS', 'Summer': '+12% Click',
                'Autumn': '+15% Diplomas', 'Winter': '+25% Offline'}
TABS = ["Buildings", "Upgrades", "Curriculum", "Report Card", "Campus", "Prestige", "Legacy", "Worlds", "Settings"]
PATH_ORDER = ["Foundation", "Academic", "Innovation", "Prestige", "Active", "Mastery"]

BUY_OPTS = [(1, "×1"), (2, "×2"), (5, "×5"), (10, "×10"), (100, "×100"), ("max", "Max")]

TAB_HINTS = {
    "Buildings":   "Buy buildings to earn KP/s passively.\n"
                   "Each new building requires you to SACRIFICE a number of the previous one.\n"
                   "e.g. 1 Library costs 10 Classrooms — they are consumed on purchase.\n"
                   "The red/green badge shows if you have enough to buy right now.",
    "Upgrades":    "Upgrades multiply a building's KP/s output — buy them as soon as you can!\n"
                   "Upgrades survive prestige resets and stack multiplicatively.",
    "Curriculum":  "Spend Merit Points (MP) on permanent skills that survive every prestige.\n"
                   "MP is earned from achievements. Choose your paths wisely — you cannot\n"
                   "afford all 6 paths. Each path gets exponentially more expensive.",
    "Report Card": "Complete achievements to earn Merit Points.\nHigher grades give bigger rewards!",
    "Campus":      "Watch your school grow in real time!\n"
                   "Buildings appear as you purchase them. The day/night cycle and seasons are visual only.",
    "Prestige":    "Graduate to earn Diplomas — they survive ALL resets forever.\n"
                   "Each diploma permanently adds to your global KPS multiplier.\n"
                   "You need 2M KP to graduate. The more KP you have, the more Diplomas you earn.",
    "Legacy":      "Convert Diplomas → Honors → Endowments → Alumni Points for stacking permanent bonuses.\n"
                   "Each tier is more powerful but costs more of the tier below. Never resets.",
    "Worlds":      "Explore 10 unique zones — each with its own buildings, prestige system, and mechanic.\n"
                   "Zones unlock by prestiging or earning Alumni Points in earlier zones.\n"
                   "Zone 10 (Hero World) lets you create a hero using your Curriculum investments.",
    "Settings":    "Name your school — it appears in the news ticker!\n"
                   "Fullscreen toggle, audio mute, stats, and the reset button are all here.",
}


def fmt_time(secs: float) -> str:
    secs = int(secs)
    h, m, s = secs // 3600, (secs % 3600) // 60, secs % 60
    if h:  return f"{h}h {m}m"
    if m:  return f"{m}m {s}s"
    return f"{s}s"


# ── Floating "+KP" text ───────────────────────────────────────────────────────
class Float:
    def __init__(self, x: int, y: int, text: str, color=(255, 230, 40)):
        self.x, self.y = float(x), float(y)
        self.text  = text
        self.color = color
        self.alpha = 255

    def tick(self, dt: float):
        self.y     -= 90 * dt
        self.alpha -= 255 * dt * 0.8

    def draw(self, surf):
        s = F_LG.render(self.text, True, self.color)
        s.set_alpha(max(0, int(self.alpha)))
        surf.blit(s, (int(self.x), int(self.y)))

    @property
    def alive(self): return self.alpha > 0


# ── App ───────────────────────────────────────────────────────────────────────
class App:
    ITEM_H = 80
    ITEM_G = 5

    def __init__(self):
        self._fullscreen = False
        try:
            self.screen = pygame.display.set_mode(
                (W, H), pygame.RESIZABLE | pygame.SCALED)
        except pygame.error:
            self.screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
        pygame.display.set_caption(f"Idle Edu Empire  v{VERSION}")
        self.clock  = pygame.time.Clock()
        self.game   = Game()
        self.game.load()

        self.tab       = "Buildings"
        self.b_scroll  = 0
        self.u_scroll  = 0
        self.sk_scroll = 0
        self.ac_scroll = 0
        self.lg_scroll_h = 0
        self.lg_scroll_e = 0
        self.lg_subtab   = "Honors"
        self.floats: list[Float] = []

        self.tick_idx = 0
        self.tick_x   = float(W)
        self.tick_spd = 85.0

        self.tooltip: Optional[tuple] = None
        self.popup:   Optional[dict]  = None
        if self.game.show_offline_popup:
            self.popup = {"type": "offline"}

        self._reset_confirm = False

        self._study_btn: Optional[pygame.Rect] = None
        self._grad_btn:  Optional[pygame.Rect] = None
        self._exit_btn:  Optional[pygame.Rect] = None
        self._event_btn: Optional[pygame.Rect] = None
        self._tab_rects: list[tuple[pygame.Rect, str]] = []
        self._buy_items: list[tuple[pygame.Rect, object, str]] = []

        self._last_save      = time.time()
        self.milestone_flash: Optional[dict] = None

        self._ticker_dynamic:   Optional[str] = None
        self._name_input_active = False
        self._name_input_text   = ""
        self._name_input_rect:  Optional[pygame.Rect] = None

        self._hm_show_tab = ""
        self._hm_x        = float(W + 10)
        self._hm_timer    = 0.0

        self.buy_mult: int | str = 1
        self.b_filter: str = "all"   # "all" | "affordable" | "owned"
        self.lg_scroll_s = 0
        self.lg_scroll_a = 0

        self._mouse_held      = False
        self._hold_acc        = 0.0
        self._hold_float_timer = 0.0

        # Multi-zone (Worlds tab)
        self.world             = WorldManager()
        self.worlds_sel_zone   = 2           # which zone card is selected
        self.worlds_subtab     = "Overview"  # Overview | Buildings | Upgrades | Prestige
        self.worlds_b_scroll   = 0
        self.worlds_u_scroll   = 0
        self._prev_world_save  = time.time()
        self.ps_scroll         = 0
        self._owned_expanded   = True

        self.sprites = spr.SpriteManager()
        self.campus  = CampusView()
        self.campus._time = self.game.game_time   # sync campus calendar to saved game clock
        self._shadow_cache: dict = {}

        # Pre-baked edge-shadow strips (created once, blitted each frame)
        self._topbar_shadow = pygame.Surface((W, 10), pygame.SRCALPHA)
        for _i in range(10):
            pygame.draw.line(self._topbar_shadow, (0,0,0, int(68*(1-_i/10))), (0,_i),(W,_i))
        self._panel_shadow = pygame.Surface((10, H), pygame.SRCALPHA)
        for _i in range(10):
            pygame.draw.line(self._panel_shadow, (0,0,0, int(58*(1-_i/10))), (_i,0),(_i,H))
        self._prev_ach_count  = len(self.game.achievements_unlocked)
        self._prev_story_len  = len(self.game.story_queue)
        self._prev_event      = self.game.pending_event
        self._prev_daily_done = self.game._total_daily_done
        self._normal_game: Optional[Game] = None

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _r(self, color, rect, radius=0, border=0, bc=DARK):
        pygame.draw.rect(self.screen, color, rect, border_radius=radius)
        if border:
            pygame.draw.rect(self.screen, bc, rect, border, border_radius=radius)

    def _t(self, font, text, color, x, y):
        self.screen.blit(font.render(str(text), True, color), (x, y))

    def _tc(self, font, text, color, rect: pygame.Rect):
        s = font.render(str(text), True, color)
        self.screen.blit(s, (rect.centerx - s.get_width()//2,
                              rect.centery - s.get_height()//2))

    def _clip(self, r: pygame.Rect):
        self.screen.set_clip(r)

    def _unclip(self):
        self.screen.set_clip(None)

    def _shadow(self, rect: pygame.Rect, offset: int = 3, radius: int = 8, alpha: int = 50):
        key = (rect.width, rect.height, offset, radius, alpha)
        if key not in self._shadow_cache:
            s = pygame.Surface((rect.width + offset, rect.height + offset), pygame.SRCALPHA)
            pygame.draw.rect(s, (0, 0, 0, alpha),
                             pygame.Rect(offset, offset, rect.width, rect.height),
                             border_radius=radius)
            self._shadow_cache[key] = s
        self.screen.blit(self._shadow_cache[key], (rect.x, rect.y))

    # ── Top bar ───────────────────────────────────────────────────────────────

    def _draw_topbar(self):
        g = self.game
        self._r(TOPBAR, pygame.Rect(0, 0, W, TOP_H))

        # KP display
        self._t(F_LG, f"Knowledge Points: {fmt(g.kp)}", WHITE, 18, 8)

        if g.active_boost:
            ab  = g.active_boost
            pct = ab["remaining"] / ab["duration"]
            bar = pygame.Rect(20, 46, 240, 14)
            pygame.draw.rect(self.screen, (60, 80, 60), bar, border_radius=4)
            pygame.draw.rect(self.screen, GOLD,
                             pygame.Rect(20, 46, int(240 * pct), 14), border_radius=4)
            lbl = "KPS" if ab["type"] == "kps_boost" else "Click"
            col = (255, 180, 60) if ab.get("rarity") == "rare" else GOLD
            self._t(F_SM, f"{lbl} ×{ab['value']:.0f}  {ab['remaining']:.0f}s",
                    col, 268, 44)
        else:
            self._t(F_SM,
                    f"per second: {fmt(g.kps())}  |  total: {fmt(g.all_time_kp)}  |  click: {fmt(g.click_power)} KP",
                    (185, 210, 250), 20, 44)

        # Sandbox badge
        if g.sandbox_mode:
            bw = 160
            bx = W // 2 - bw // 2
            self._r(SANDBOX_C, pygame.Rect(bx, 4, bw, 20), radius=4)
            self._t(F_XS, "SANDBOX MODE — no saves", WHITE, bx + 8, 8)

        # Currencies (right side, 3-column grid)
        cx1 = W - 510
        cx2 = W - 350
        cx3 = W - 170
        self._t(F_MD, f"Diplomas: {g.diplomas}",         GOLD,            cx1, 10)
        self._t(F_MD, f"Honors: {g.honors}",             (200, 230, 100), cx1, 36)
        self._t(F_MD, f"Endow: {g.endowments}",         ENDOW_COL,       cx2, 10)
        self._t(F_MD, f"Alumni: {g.alumni_points}",      ALUMNI_COL,      cx2, 36)
        self._t(F_MD, f"Merit: {g.merit_points}",        (100, 220, 220), cx3, 10)
        self._t(F_XS, f"v{VERSION}", (100, 130, 170), cx3, 36)

        # Exit button
        ex_btn = pygame.Rect(W - 80, 14, 68, 32)
        mx, my = pygame.mouse.get_pos()
        hov    = ex_btn.collidepoint(mx, my)
        self._r((190, 55, 55) if hov else (155, 40, 40), ex_btn, radius=6)
        self._tc(F_MD, "Exit", WHITE, ex_btn)
        self._exit_btn = ex_btn
        self.screen.blit(self._topbar_shadow, (0, TOP_H))

    # ── Tab bar ───────────────────────────────────────────────────────────────

    def _draw_tabs(self):
        self._r((215, 208, 194), pygame.Rect(LEFT_W, TOP_H, W - LEFT_W, CONTENT_Y - TOP_H))
        tw = (W - LEFT_W - 12) // len(TABS)
        self._tab_rects = []
        for i, name in enumerate(TABS):
            r      = pygame.Rect(LEFT_W + 6 + i * tw, TOP_H + 5, tw - 4, 34)
            active = self.tab == name
            self._r(CREAM if active else (175, 168, 155), r, radius=6)
            col = DARK if active else WHITE
            self._tc(F_SM if len(name) > 9 else F_MD, name, col, r)
            self._tab_rects.append((r, name))

    # ── Left panel ────────────────────────────────────────────────────────────

    def _draw_left(self):
        g  = self.game
        cx = LEFT_W // 2
        self._grad_btn = None   # reset each frame; only set if button is actually drawn
        viewing_zone = (self.worlds_sel_zone if self.tab == "Worlds" and self.worlds_sel_zone not in (0, 1) else 1)
        self._r(PANEL, pygame.Rect(0, TOP_H, LEFT_W, H - TOP_H))
        pygame.draw.line(self.screen, (165, 158, 145), (LEFT_W, TOP_H), (LEFT_W, H), 2)
        self.screen.blit(self._panel_shadow, (LEFT_W + 2, 0))

        mini_rect = pygame.Rect(0, TOP_H, LEFT_W, 330)
        _zone1_theme = self.game.cosmetic_theme if viewing_zone == 1 else None
        self.campus.draw(self.screen, mini_rect, self.game, tile_base=36,
                         zone_id=viewing_zone, theme=_zone1_theme)

        # Season badge (overlaid on bottom of campus mini view)
        season = self.game.season
        scol   = SEASON_COL.get(season, GRAY)
        sbonus = SEASON_BONUS.get(season, '')
        stext  = f"{season}  {sbonus}"
        sw     = F_XS.size(stext)[0] + 14
        ssurf  = pygame.Surface((sw, 17), pygame.SRCALPHA)
        ssurf.fill((*scol, 200))
        pygame.draw.rect(ssurf, (255, 255, 255, 80), (0, 0, sw, 17), 1, border_radius=4)
        self.screen.blit(ssurf, (6, TOP_H + 330 - 20))
        self._t(F_XS, stext, WHITE, 12, TOP_H + 330 - 17)

        if self.tab == "Worlds":
            self._draw_left_zone_info(viewing_zone)
            return

        btn = pygame.Rect(cx - 100, 410, 200, 58)
        mx, my = pygame.mouse.get_pos()
        hov = btn.collidepoint(mx, my)
        self._shadow(btn, offset=4, radius=11, alpha=60)
        self._r((90, 160, 218) if hov else ACCENT, btn, radius=11, border=2, bc=(30, 68, 125))
        self._tc(F_LG, "STUDY!", WHITE, btn)
        sub = F_SM.render(f"+{fmt(g.click_power)} KP per click", True, (215, 238, 255))
        self.screen.blit(sub, (cx - sub.get_width()//2, btn.bottom + 5))
        self._study_btn = btn

        # ── Flowing layout below Study button ────────────────────────────────
        _fy = btn.bottom + 8   # current flow y-cursor

        # 1. Strike / Combo / Auto indicator (mutually exclusive, ≤44px)
        if g._staff_strike_active:
            sr = pygame.Rect(cx - 120, _fy, 240, 44)
            self._r((180, 40, 40), sr, radius=7)
            self._tc(F_SM, f"⚠ STAFF STRIKE  {g._staff_strike_timer:.0f}s",
                     WHITE, pygame.Rect(cx-120, _fy+1, 240, 22))
            resolve_lbl = "Resolve (5 merit)" if g.merit_points >= 5 else "Strike in progress"
            resolve_col = (200, 200, 80) if g.merit_points >= 5 else (160, 160, 160)
            self._tc(F_XS, resolve_lbl, resolve_col, pygame.Rect(cx-120, _fy+22, 240, 20))
            self._buy_items.append((sr, None, "resolve_strike"))
            _fy += 52
        elif g.combo > 0:
            cmult = g.combo_mult
            ctxt  = F_MD.render(f"×{cmult:.2f} COMBO!", True, GOLD)
            self.screen.blit(ctxt, (cx - ctxt.get_width()//2, _fy))
            bar_w = 160
            pct   = g.combo_timer / COMBO_WINDOW
            pygame.draw.rect(self.screen, (55, 55, 45),
                             pygame.Rect(cx - bar_w//2, _fy + 24, bar_w, 7), border_radius=3)
            pygame.draw.rect(self.screen, GOLD,
                             pygame.Rect(cx - bar_w//2, _fy + 24, int(bar_w * pct), 7),
                             border_radius=3)
            _fy += 38
        else:
            auto_rate = g._dipl_sum("auto_click_rate")
            if auto_rate > 0:
                ar_rect = pygame.Rect(cx - 80, _fy, 160, 22)
                self._r((50, 80, 50), ar_rect, radius=4)
                self._tc(F_XS, f"Auto: {auto_rate:.1f} clicks/s", (150, 230, 150), ar_rect)
                _fy += 28

        # 2. Graduate button (if eligible)
        self._grad_btn = None
        if g.prestige_eligible:
            gb   = pygame.Rect(cx - 95, _fy, 190, 40)
            ghov = gb.collidepoint(mx, my)
            self._shadow(gb, offset=3, radius=9)
            self._r((175, 65, 175) if ghov else PRESTIGE, gb, radius=9, border=2, bc=(100, 20, 100))
            self._tc(F_MD, f"Graduate!  +{g.diplomas_on_prestige} Diplomas", WHITE, gb)
            self._grad_btn = gb
            _fy += 48

        # 3. Quiz Me button
        if not g._quiz_active and not g._quiz_showing_reward:
            if g._quiz_cooldown > 0:
                qbtn_col = (100, 90, 70)
                qbtn_lbl = f"Quiz: {g._quiz_cooldown:.0f}s"
            else:
                qbtn_col = (55, 100, 160)
                qbtn_lbl = "Quiz Me!"
            qbtn = pygame.Rect(cx - 65, _fy, 130, 26)
            self._r(qbtn_col, qbtn, radius=6)
            self._tc(F_XS, qbtn_lbl, WHITE, qbtn)
            if g._quiz_cooldown <= 0:
                self._buy_items.append((qbtn, None, "quiz_start"))
            if qbtn.collidepoint(mx, my):
                self.tooltip = ((mx, my), [
                    "Quiz Me!",
                    "Answer 3 knowledge questions correctly to earn a reward.",
                    "Rewards: bonus KP, permanent +Diplomas/prestige, or a free prestige.",
                    "Wrong answer = no reward. Cooldown applies after each attempt.",
                ])
            _fy += 30
            if g._quiz_fail_msg:
                self._tc(F_XS, g._quiz_fail_msg, (220, 80, 80),
                         pygame.Rect(cx - 120, _fy, 240, 16))
                _fy += 20

        # 4. Focus Points bar + abilities
        fp_cap  = g._focus_cap()
        fp_frac = g.focus_points / max(1, fp_cap)
        self._t(F_XS, f"⚡ Focus  {int(g.focus_points)} / {int(fp_cap)}",
                (180, 210, 255), 12, _fy)
        bar_rect = pygame.Rect(12, _fy + 14, LEFT_W - 24, 8)
        pygame.draw.rect(self.screen, (50, 60, 90), bar_rect, border_radius=4)
        pygame.draw.rect(self.screen, (100, 170, 255),
                         (bar_rect.x, bar_rect.y, int(bar_rect.w * fp_frac), bar_rect.h),
                         border_radius=4)
        _fy += 24
        if g.focus_active:
            ab_name = next((a["name"] for a in FOCUS_ABILITIES if a["id"] == g.focus_active["id"]), "")
            rem = g.focus_active["timer"]
            self._t(F_XS, f"  {ab_name} {rem:.0f}s", (130, 200, 255), 12, _fy)
            _fy += 14
        _FOCUS_TIPS = {
            "surge":  ["Study Surge  (2 FP)", "Triples your click power for 20 seconds.",
                       "Great when you're about to click a lot."],
            "burst":  ["KPS Burst  (3 FP)", "Doubles your KP/s for 30 seconds.",
                       "Use before going idle for a short burst of passive income."],
            "lucky":  ["Lucky Hour  (5 FP)", "Forces a rare random event to trigger immediately.",
                       "Random events give bonus KP, boosts, or special effects."],
            "recall": ["Recall  (4 FP)", "Instantly earns 10 minutes of offline KP.",
                       "Use when you're short on KP and can't wait."],
        }
        ab_w, ab_g = 74, 4
        mx_f, my_f = pygame.mouse.get_pos()
        for i, ab in enumerate(FOCUS_ABILITIES):
            can = g.focus_points >= ab["cost"] and (g.focus_active is None or ab["duration"] == 0)
            abr = pygame.Rect(12 + i * (ab_w + ab_g), _fy, ab_w, 24)
            self._r((65, 124, 175) if can else (120, 120, 120), abr, radius=4)
            self._tc(F_XS, f"{ab['name']} {ab['cost']}⚡", WHITE, abr)
            self._buy_items.append((abr, ab["id"], "use_focus"))
            if abr.collidepoint(mx_f, my_f):
                self.tooltip = ((mx_f, my_f), _FOCUS_TIPS.get(ab["id"], [ab["name"]]))
        _fy += 28

        _fp_ui_bottom = _fy

        # Goals + Owned combined panel
        goals = self._get_goals()
        tip   = self._get_tutorial_tip()
        owned = [(b.name, g.building_counts[b.name])
                 for b in BUILDINGS if g.building_counts[b.name] > 0]
        n_own_rows = (len(owned) + 1) // 2
        G_LH, O_LH, T_LH = 17, 13, 14
        tip_lines = []
        if tip:
            words, cur = tip.split(), ""
            for w in words:
                test = (cur + " " + w).strip()
                if F_XS.size(test)[0] <= LEFT_W - 26:
                    cur = test
                else:
                    tip_lines.append(cur); cur = w
            if cur: tip_lines.append(cur)
        own_data_rows = n_own_rows if self._owned_expanded else 0
        panel_h = (14 + len(goals) * G_LH
                   + (6 + len(tip_lines) * T_LH if tip_lines else 0)
                   + (14 + own_data_rows * O_LH if owned else 0) + 10)
        y0 = max(_fp_ui_bottom + 4, H - TICKER_H - 8 - panel_h)
        panel_r = pygame.Rect(5, y0, LEFT_W - 10,
                              min(panel_h, H - TICKER_H - 4 - y0))
        self._r((215, 208, 194), panel_r, radius=6)
        self._clip(panel_r)

        cy = y0 + 6
        self._t(F_XS, "Goals:", (60, 60, 60), 12, cy)
        cy += 13
        for goal in goals:
            self._t(F_XS, f"• {goal}", DARK, 12, cy)
            cy += G_LH

        if tip_lines:
            cy += 3
            pygame.draw.line(self.screen, (185, 178, 165), (12, cy), (LEFT_W - 12, cy), 1)
            cy += 4
            self._t(F_XS, "💡", (160, 130, 50), 10, cy)
            for tl in tip_lines:
                self._t(F_XS, tl, (100, 80, 30), 24, cy)
                cy += T_LH

        if owned:
            cy += 3
            pygame.draw.line(self.screen, (185, 178, 165),
                             (12, cy), (LEFT_W - 12, cy), 1)
            cy += 5
            arrow = "▲" if self._owned_expanded else "▼"
            hdr_txt = f"Owned {arrow}  ({len(owned)} types)"
            hdr_r = pygame.Rect(5, cy - 2, LEFT_W - 10, 16)
            self._buy_items.append((hdr_r, None, "toggle_owned"))
            self._t(F_XS, hdr_txt, (88, 88, 88), 12, cy)
            cy += 13
            if self._owned_expanded:
                col_w = (LEFT_W - 10) // 2
                for i, (name, count) in enumerate(owned):
                    col_idx = i % 2
                    row_idx = i // 2
                    tx = 12 + col_idx * col_w
                    ty = cy + row_idx * O_LH
                    short = name if len(name) <= 13 else name[:12] + "…"
                    self._t(F_XS, f"{short}: {count}", DARK, tx, ty)

        self._unclip()

    def _draw_left_zone_info(self, zone_id: int):
        """Show zone stats in the left sidebar when the Worlds tab is active."""
        g   = self.game
        cx  = LEFT_W // 2
        y0  = TOP_H + 336
        x   = 10
        w   = LEFT_W - 20

        if zone_id == 1:
            # Zone 1 summary
            self._r(ACCENT, pygame.Rect(x, y0, w, 26), radius=5)
            self._tc(F_SM, "Zone 1: Modern School (Active)", WHITE, pygame.Rect(x, y0, w, 26))
            rows = [
                f"KP/s: {fmt(g.kps())}",
                f"KP: {fmt(g.kp)}",
                f"Prestige: ×{g.prestige_count}",
                f"Diplomas: {g.diplomas}",
                f"Alumni: {g.alumni_points}",
            ]
            for i, row in enumerate(rows):
                self._t(F_XS, row, DARK, x + 4, y0 + 32 + i * 17)
        else:
            zdef = next((z for z in ZONE_DEFS if z["id"] == zone_id), None)
            if zdef is None:
                return
            col_t = zdef["theme_color"]
            self._r(col_t, pygame.Rect(x, y0, w, 26), radius=5)
            icon  = zdef.get("icon", "")
            label = f"{icon} Zone {zone_id}: {zdef['name']}"
            self._tc(F_SM, label, WHITE, pygame.Rect(x, y0, w, 26))

            zg = self.world.zones.get(zone_id)
            if zg and self.world.is_unlocked(zone_id, g):
                rows = [
                    f"KP/s: {fmt(zg.kps())}",
                    f"KP: {fmt(zg.kp)}",
                    f"Prestige: ×{zg.prestige_count}",
                ]
                for i, row in enumerate(rows):
                    self._t(F_XS, row, DARK, x + 4, y0 + 32 + i * 17)
            else:
                req  = zdef["unlock"]
                src  = "Zone 1" if req["zone"] == 1 else f"Zone {req['zone']}"
                if req["type"] == "prestige":
                    msg = f"Prestige {src} {req['value']}× to unlock"
                else:
                    msg = f"Earn {req['value']} Alumni in {src} to unlock"
                self._t(F_XS, msg, (160, 80, 80), x + 4, y0 + 32)

    def _draw_school(self, cx: int, cy: int):
        s = self.screen
        pygame.draw.rect(s, (155, 140, 115), (cx-102, cy+33, 204, 7))
        pygame.draw.rect(s, (183, 175, 160), (cx-36, cy+24, 72, 10))
        pygame.draw.rect(s, (193, 186, 170), (cx-28, cy+15, 56, 10))
        pygame.draw.rect(s, (200, 186, 156), (cx-96, cy-54, 192, 90))
        for px in [-82, -60, 48, 70]:
            pygame.draw.rect(s, (183, 170, 140), (cx+px, cy-54, 8, 90))
        pygame.draw.polygon(s, (132, 93, 68),
                            [(cx-108, cy-54), (cx, cy-105), (cx+108, cy-54)])
        pygame.draw.rect(s, (112, 79, 55), (cx-108, cy-59, 216, 7))
        pygame.draw.rect(s, (78, 52, 30), (cx-16, cy+4, 32, 32))
        pygame.draw.circle(s, GOLD, (cx+12, cy+20), 3)
        pygame.draw.arc(s, (98, 75, 50), pygame.Rect(cx-16, cy-1, 32, 18), 0, 3.14159, 3)
        for wx in [-80, -42, 20, 58]:
            pygame.draw.rect(s, LBLUE,  (cx+wx, cy-42, 22, 22))
            pygame.draw.line(s, DARK,   (cx+wx+11, cy-42), (cx+wx+11, cy-20), 1)
            pygame.draw.line(s, DARK,   (cx+wx,    cy-31), (cx+wx+22, cy-31), 1)
            pygame.draw.rect(s, (85, 85, 85), (cx+wx, cy-42, 22, 22), 1)
        pygame.draw.line(s, (75, 75, 75), (cx, cy-105), (cx, cy-148), 2)
        pygame.draw.polygon(s, (208, 42, 42),
                            [(cx, cy-148), (cx+30, cy-136), (cx, cy-124)])

    # ── Goals panel ───────────────────────────────────────────────────────────

    def _get_tutorial_tip(self) -> str:
        g = self.game
        total_bld = sum(g.building_counts.values())
        if g.all_time_kp < 50:
            return "Hold STUDY to auto-click! Buildings generate KP/s passively."
        if total_bld == 0:
            return "Buy a Classroom in the Buildings tab to earn KP/s automatically!"
        if not g.upgrades_purchased and any(
                g.kp >= g.upgrade_cost(u.name) for u in UPGRADES):
            return "You can afford an Upgrade! They multiply building output permanently."
        if g.merit_points >= 3 and not g.skills_purchased:
            return "You have Merit Points — visit Curriculum to unlock permanent Skills!"
        if g.prestige_eligible and g.prestige_count == 0:
            return "You're ready to Graduate! Diplomas survive resets and give +2% KPS each."
        if g.prestige_count >= 1 and g.diplomas >= g.honor_rate and not g.honor_upgrades_purchased:
            return "Visit Legacy to convert Diplomas → Honors for powerful permanent bonuses."
        if g.honors >= 5 and g.endowments == 0:
            return "Convert Honors → Endowments in the Legacy tab for even bigger multipliers."
        if g.endowments >= g.alumni_rate and g.alumni_points == 0:
            return "You can earn an Alumni Point in Legacy! The most permanent boost in the game."
        return ""

    def _get_goals(self) -> list[str]:
        g     = self.game
        goals = []

        # Highest-priority conversions
        if len(goals) < 3 and g.endowments >= g.alumni_rate:
            goals.append(f"Alumni Point ready! ({g.endowments}/{g.alumni_rate} Endowments)")
        if len(goals) < 3 and g.diplomas >= g.honor_rate:
            goals.append(f"Honor Ceremony! ({g.diplomas}/{g.honor_rate} Diplomas)")
        if len(goals) < 3 and g.honors >= 5:
            goals.append(f"Endowment ready! ({g.honors}/5 Honors)")

        # Prestige
        if len(goals) < 3:
            if g.prestige_eligible:
                goals.append(f"Graduate! +{g.diplomas_on_prestige} Diplomas waiting")
            elif g.total_kp > 100_000:
                left = 1_000_000 - g.total_kp
                goals.append(f"{fmt(left)} KP to Graduate")

        # Next building to buy
        if len(goals) < 3:
            for b in BUILDINGS:
                if g.all_time_kp >= b.unlock_at or g.building_counts[b.name] > 0:
                    cost = g.building_cost(b.name)
                    if cost > g.kp:
                        goals.append(f"{fmt(cost - g.kp)} KP → {b.name}")
                        break

        # Next upgrade
        if len(goals) < 3:
            for u in UPGRADES:
                if u.name not in g.upgrades_purchased:
                    cost = g.upgrade_cost(u.name)
                    if cost > g.kp:
                        goals.append(f"{fmt(cost - g.kp)} KP → {u.name}")
                        break

        # Closest achievement (capped to not flood with unreachable ones)
        if len(goals) < 3:
            best, best_pct = None, -1.0
            for a in ACHIEVEMENTS:
                if a.id in g.achievements_unlocked:
                    continue
                if a.check == "kp_total":
                    pct = min(1.0, g.all_time_kp / max(1, a.check_value))
                elif a.check == "clicks":
                    pct = min(1.0, g.total_clicks / max(1, a.check_value))
                elif a.check == "building_count":
                    pct = min(1.0, g.building_counts.get(a.check_target, 0) / max(1, a.check_value))
                elif a.check == "combo":
                    pct = min(1.0, g.max_combo_reached / max(1, a.check_value))
                elif a.check == "honors":
                    pct = min(1.0, g.total_honors_earned / max(1, a.check_value))
                elif a.check == "endowments":
                    pct = min(1.0, g.total_endow_earned / max(1, a.check_value))
                elif a.check == "prestige":
                    pct = min(1.0, g.prestige_count / max(1, a.check_value))
                elif a.check == "total_buildings":
                    pct = min(1.0, sum(g.building_counts.values()) / max(1, a.check_value))
                elif a.check == "star_level":
                    pct = min(1.0, max(g.star_milestones_hit.values(), default=0) / max(1, a.check_value))
                elif a.check == "scholars":
                    pct = min(1.0, len(g.scholars_purchased) / max(1, a.check_value))
                elif a.check == "all_scholars":
                    pct = min(1.0, len(g.scholars_purchased) / max(1, len(SCHOLARS)))
                elif a.check == "faculty_count":
                    pct = min(1.0, g._total_faculty_hires / max(1, a.check_value))
                elif a.check == "daily_done":
                    pct = min(1.0, g._total_daily_done / max(1, a.check_value))
                elif a.check == "seasons_seen":
                    pct = min(1.0, len(g._seasons_seen) / max(1, a.check_value))
                elif a.check == "alumni_earned":
                    pct = min(1.0, g.total_alumni_earned / max(1, a.check_value))
                elif a.check == "research_legacy":
                    pct = min(1.0, g.alumni_research_count / max(1, a.check_value))
                else:
                    pct = 0.0
                if 0 < pct and pct > best_pct:
                    best_pct, best = pct, a
            if best and best_pct > 0:
                goals.append(f"Achiev: {best.name} {int(best_pct*100)}%")

        return goals[:3]

    # ── Right panel ───────────────────────────────────────────────────────────

    def _right_area(self):
        x   = LEFT_W + 5
        w   = W - LEFT_W - 10
        off = 72 if self.game.inspector else 0
        return x, CONTENT_Y + off, w, CONTENT_H - off

    def _draw_buildings_header(self, x, y0, w):
        # ── Buy mode (right side) ──────────────────────────────────────────────
        bw, gap = 68, 5
        bm_total = len(BUY_OPTS) * (bw + gap) - gap
        bm_x = x + w - bm_total - 8
        self._t(F_XS, "Buy:", (100, 100, 100), bm_x - 34, y0 + 10)
        for i, (opt, label) in enumerate(BUY_OPTS):
            br = pygame.Rect(bm_x + i * (bw + gap), y0 + 3, bw, 26)
            active = self.buy_mult == opt
            self._r(ACCENT if active else (185, 178, 165), br, radius=5)
            self._tc(F_SM, label, WHITE, br)
            self._buy_items.append((br, opt, "set_buy_mult"))

        # ── Filter (left side) ────────────────────────────────────────────────
        FILTERS = [("all", "All"), ("affordable", "Affordable"), ("owned", "Owned")]
        fw, fg = 86, 5
        self._t(F_XS, "Filter:", (100, 100, 100), x + 8, y0 + 10)
        for i, (fid, flabel) in enumerate(FILTERS):
            fr = pygame.Rect(x + 55 + i * (fw + fg), y0 + 3, fw, 26)
            active = self.b_filter == fid
            self._r(ACCENT if active else (185, 178, 165), fr, radius=5)
            self._tc(F_SM, flabel, WHITE, fr)
            self._buy_items.append((fr, fid, "set_b_filter"))

    def _draw_buildings(self):
        g = self.game
        x, y0, w, h = self._right_area()
        BROW = 36
        step = self.ITEM_H + self.ITEM_G

        # Fixed buy-mode selector row
        self._draw_buildings_header(x, y0, w)
        pygame.draw.line(self.screen, (190, 184, 172),
                         (x, y0 + BROW - 2), (x + w, y0 + BROW - 2))

        # Scrollable building list
        ly0, lh = y0 + BROW, h - BROW
        self._clip(pygame.Rect(x, ly0, w, lh))

        for i, b in enumerate(BUILDINGS):
            iy = ly0 + i * step - self.b_scroll
            if iy + self.ITEM_H < ly0 or iy > ly0 + lh:
                continue
            card = pygame.Rect(x, iy, w, self.ITEM_H)
            if not (g.all_time_kp >= b.unlock_at or g.building_counts[b.name] > 0):
                if not g.sandbox_mode:
                    self._shadow(card)
                    self._r(CARD_LOCK, card, radius=8)
                    self._t(F_MD, "??? (locked)", (152, 147, 137), x+14, iy+26)
                    continue

            cnt = g.building_counts[b.name]

            # Apply filter
            if self.b_filter == "owned" and cnt == 0:
                continue
            if self.b_filter == "affordable" and g.kp < g.building_cost(b.name):
                continue

            # Compute cost and affordability for selected buy mode
            mult = self.buy_mult
            sac = BUILDING_SACRIFICE.get(b.name)
            sac_have = g.building_counts.get(sac[0], 0) if sac else 0

            if mult == "max":
                n = g.building_max_buyable(b.name)
                n_buy = max(1, n)
                total_cost = g.building_cost_n(b.name, n_buy)
                ok = n > 0
                btn_label = f"×{n}  {fmt(total_cost)} KP" if n > 0 else f"Buy  {fmt(g.building_cost(b.name))} KP"
            else:
                n_buy = int(mult)
                total_cost = g.building_cost_n(b.name, n_buy)
                kp_ok = g.kp >= total_cost
                sac_ok = (not sac) or g.sandbox_mode or sac_have >= n_buy * sac[1]
                ok = kp_ok and sac_ok
                btn_label = f"×{n_buy}  {fmt(total_cost)} KP" if n_buy > 1 else f"Buy  {fmt(total_cost)} KP"

            self._shadow(card)
            self._r(CARD_OK if ok else CARD_DIM, card, radius=8, border=1, bc=(173,167,155))
            self._t(F_MD, f"{b.name}   ×{cnt}", DARK, x+14, iy+8)
            star_level = self.game.star_milestones_hit.get(b.name, 0)
            if star_level > 0:
                star_surf = F_SM.render("★" * star_level, True, GOLD)
                name_w    = F_MD.size(f"{b.name}   ×{cnt}")[0]
                self.screen.blit(star_surf, (x + 14 + name_w + 6, iy + 10))
            self._t(F_SM, b.desc, (95, 95, 95), x+14, iy+30)
            if cnt > 0:
                kps_val = g.building_kps(b.name)
                fac = g.faculty_bonuses.get(b.name, 0.0)
                fac_tag = f"  [+{fac*100:.0f}% faculty]" if fac > 0 else ""
                self._t(F_SM, f"Producing: {fmt(kps_val)} KP/s{fac_tag}", (48, 126, 55), x+14, iy+52)
            btn = pygame.Rect(x + w - 168, iy + (self.ITEM_H-36)//2, 160, 36)
            self._r(GREEN if ok else GRAY, btn, radius=6)
            self._tc(F_SM, btn_label, WHITE, btn)
            self._buy_items.append((btn, b.name, "building"))
            if not ok:
                pct = min(1.0, g.kp / max(1, total_cost))
                pygame.draw.rect(self.screen, (175,168,155), (x+14, iy+self.ITEM_H-6, 220, 4), border_radius=2)
                pygame.draw.rect(self.screen, (100,180,100), (x+14, iy+self.ITEM_H-6, int(220*pct), 4), border_radius=2)
            # Sacrifice requirement badge — drawn last so it sits on top
            if sac and not g.sandbox_mode:
                need = n_buy * sac[1]
                met = sac_have >= need
                badge_col = (38, 120, 45) if met else (165, 38, 38)
                badge_r = pygame.Rect(x+10, iy+56, 234, 16)
                pygame.draw.rect(self.screen, badge_col, badge_r, border_radius=3)
                self._t(F_XS, f"⚡ Needs {need} {sac[0]}  (have {sac_have})", WHITE, x+14, iy+58)
            if card.collidepoint(pygame.mouse.get_pos()) and cnt > 0:
                upg_names = [u.name for u in UPGRADES if u.target == b.name and u.name in g.upgrades_purchased]
                syn_parts = [
                    f"{src}: ×{g.building_counts.get(src,0)*pct_s:.2f}"
                    for src, pct_s in SYNERGIES.get(b.name, [])
                    if g.building_counts.get(src, 0) > 0
                ]
                lines = [
                    f"{b.name}  (owned: {cnt})",
                    f"Base KPS: {fmt(b.base_kps * cnt)}",
                    f"Multiplier: ×{g._building_mult(b.name):.2f}",
                    f"Total KPS: {fmt(g.building_kps(b.name))}",
                    f"Next cost: {fmt(g.building_cost(b.name))} KP",
                ]
                if sac and not g.sandbox_mode:
                    lines.append(f"Sacrifice: {sac[1]} {sac[0]} per purchase (have {sac_have})")
                if syn_parts:
                    lines.append("Synergy: " + "  ".join(syn_parts))
                if upg_names:
                    lines.append("Upgrades: " + ", ".join(upg_names))
                self.tooltip = (pygame.mouse.get_pos(), lines)
        self._unclip()

    def _draw_upgrades(self):
        g = self.game
        x, y0, w, h = self._right_area()
        step = self.ITEM_H + self.ITEM_G
        self._clip(pygame.Rect(x, y0, w, h))

        row = 0
        for u in UPGRADES:
            if u.name in g.upgrades_purchased:
                continue
            iy = y0 + row * step - self.u_scroll
            if iy + self.ITEM_H >= y0 and iy <= y0 + h:
                card = pygame.Rect(x, iy, w, self.ITEM_H)
                cost = g.upgrade_cost(u.name)
                ok   = g.kp >= cost
                bg   = (232, 248, 232) if ok else CARD_DIM
                self._shadow(card)
                self._r(bg, card, radius=8, border=1, bc=(173,167,155))
                self._t(F_MD, u.name, DARK, x+14, iy+8)
                self._t(F_SM, f"{u.desc}   →  {u.target}", (95,95,95), x+14, iy+30)
                btn = pygame.Rect(x + w - 158, iy + (self.ITEM_H-36)//2, 150, 36)
                self._r(GREEN if ok else GRAY, btn, radius=6)
                self._tc(F_SM, f"{fmt(cost)} KP", WHITE, btn)
                self._buy_items.append((btn, u.name, "upgrade"))
                if not ok:
                    pct = min(1.0, g.kp / max(1, cost))
                    pygame.draw.rect(self.screen, (175,168,155), (x+14, iy+self.ITEM_H-10, 220, 5), border_radius=2)
                    pygame.draw.rect(self.screen, (100,180,100), (x+14, iy+self.ITEM_H-10, int(220*pct), 5), border_radius=2)
            row += 1

        y_sep = y0 + row * step - self.u_scroll + 10
        if y_sep >= y0 and y_sep < y0 + h:
            pygame.draw.line(self.screen, (190,185,175), (x+10, y_sep), (x+w-10, y_sep))
            self._t(F_SM, "Purchased:", (130,130,130), x+14, y_sep+4)
        row2 = 0
        for u in UPGRADES:
            if u.name not in g.upgrades_purchased:
                continue
            iy = y_sep + 22 + row2 * 22 - self.u_scroll
            if y0 <= iy < y0 + h:
                self._t(F_SM, f"  ✓  {u.name}", (100,160,100), x+14, iy)
            row2 += 1
        self._unclip()

    def _draw_curriculum(self):
        g = self.game
        x, y0, w, h = self._right_area()
        self._clip(pygame.Rect(x, y0, w, h))
        self._t(F_LG, f"Curriculum  —  Merit Points: {g.merit_points} MP", MERIT, x+10, y0+4)

        from collections import defaultdict
        groups: dict[str, list] = defaultdict(list)
        for s in SKILLS:
            groups[s.path].append(s)

        step     = self.ITEM_H + self.ITEM_G
        hdr_h    = 26
        y_cur    = y0 + 34 - self.sk_scroll

        for path in PATH_ORDER:
            if path not in groups:
                continue
            # Path header band
            if y_cur + hdr_h >= y0 and y_cur <= y0 + h:
                hdr_r = pygame.Rect(x, y_cur, w, hdr_h)
                self._r(PATH_BG[path], hdr_r)
                self._t(F_SM, PATH_LABELS.get(path, path), PATH_FG[path], x+10, y_cur+6)
            y_cur += hdr_h + 3

            for s in groups[path]:
                iy = y_cur
                y_cur += step
                if iy + self.ITEM_H < y0 or iy > y0 + h:
                    continue
                card  = pygame.Rect(x, iy, w, self.ITEM_H)
                owned = s.id in g.skills_purchased
                req_ok = (not s.requires) or (s.requires in g.skills_purchased)
                affordable = g.merit_points >= s.cost
                if owned:
                    bg = (218, 240, 218)
                elif req_ok and affordable:
                    bg = (218, 238, 248)
                elif req_ok:
                    bg = CARD_DIM
                else:
                    bg = CARD_LOCK
                self._shadow(card)
                self._r(bg, card, radius=8, border=1, bc=(173,167,155))
                self._t(F_MD, s.name, DARK if not owned else (55,135,55), x+14, iy+8)
                self._t(F_SM, s.desc, (95,95,95), x+14, iy+30)
                if s.requires:
                    req_name = next((sk.name for sk in SKILLS if sk.id == s.requires), s.requires)
                    self._t(F_SM, f"Requires: {req_name}", (140,100,60), x+14, iy+52)
                if not owned and req_ok:
                    btn = pygame.Rect(x + w - 158, iy + (self.ITEM_H-36)//2, 150, 36)
                    self._r(MERIT if affordable else GRAY, btn, radius=6)
                    self._tc(F_SM, f"Learn  {s.cost} MP", WHITE, btn)
                    self._buy_items.append((btn, s.id, "skill"))
                elif owned:
                    self._t(F_MD, "✓", (55,155,55), x + w - 40, iy + 26)

        self._unclip()

    def _draw_reportcard(self):
        g = self.game
        x, y0, w, h = self._right_area()
        unlocked = len(g.achievements_unlocked)
        total    = len(ACHIEVEMENTS)
        self._t(F_LG, f"Report Card  —  {unlocked}/{total} unlocked", (95,60,148), x+10, y0+4)

        # ── Daily Challenges ──────────────────────────────────────────────────
        dm_y  = y0 + 30
        self._t(F_SM, "Daily Challenges:", (100, 72, 150), x+10, dm_y)
        dm_card_y = dm_y + 18
        dm_h, dm_gap = 46, 6
        dm_w = (w - dm_gap * 2 - 10) // 3
        for i, m in enumerate(g.daily_missions[:3]):
            mx   = x + 5 + i * (dm_w + dm_gap)
            done = m.get("completed", False)
            bg   = (218, 240, 218) if done else (228, 220, 245)
            self._r(bg, pygame.Rect(mx, dm_card_y, dm_w, dm_h), radius=6,
                    border=1, bc=(160, 140, 200))
            label = ("✓ " if done else "") + m["label"]
            col   = (55, 145, 55) if done else (85, 60, 130)
            self._t(F_XS, label, col, mx + 6, dm_card_y + 5)
            prog  = g._daily_progress(m["type"])
            ptxt  = f"{fmt(prog)} / {fmt(m['target'])}  +{m['reward']} MP"
            self._t(F_XS, ptxt, (100, 80, 140), mx + 6, dm_card_y + 19)
            pct   = min(1.0, prog / max(1, m["target"]))
            pygame.draw.rect(self.screen, (185, 178, 210),
                             (mx + 4, dm_card_y + dm_h - 9, dm_w - 8, 5), border_radius=2)
            if pct > 0:
                pygame.draw.rect(self.screen,
                                 (80, 200, 120) if done else (120, 100, 185),
                                 (mx + 4, dm_card_y + dm_h - 9, int((dm_w - 8) * pct), 5),
                                 border_radius=2)

        ach_y0 = dm_card_y + dm_h + 6   # achievements start below daily missions

        self._clip(pygame.Rect(x, ach_y0, w, h - (ach_y0 - y0)))
        cw, ch = (w - 12) // 2, 78
        gap    = 6
        for i, a in enumerate(ACHIEVEMENTS):
            col = i % 2
            row = i // 2
            cx2 = x + col * (cw + gap)
            iy  = ach_y0 + row * (ch + gap) - self.ac_scroll
            if iy + ch < y0 or iy > y0 + h:
                continue
            card  = pygame.Rect(cx2, iy, cw, ch)
            owned = a.id in g.achievements_unlocked
            gcol  = GRADE_COL.get(a.grade, GRAY)
            bg    = (232, 242, 232) if owned else CARD_DIM
            self._shadow(card, radius=7)
            self._r(bg, card, radius=7, border=1, bc=(172,165,153))
            badge = pygame.Rect(cx2 + cw - 48, iy + 8, 40, 32)
            self._r(gcol if owned else GRAY, badge, radius=5)
            self._tc(F_XS, a.grade, WHITE, badge)
            col2 = DARK if owned else (148, 143, 133)
            self._t(F_XS, a.name,              col2,        cx2+10, iy+8)
            self._t(F_XS, a.desc,              (105,105,105),cx2+10, iy+26)
            if owned:
                self._t(F_XS, "✓ UNLOCKED", (55,155,55), cx2+10, iy+50)
            else:
                self._t(F_XS, f"+{a.merit_reward} Merit", MERIT, cx2+10, iy+50)
        self._unclip()

    def _draw_prestige_shop(self):
        g = self.game
        x, y0, w, h = self._right_area()
        self._clip(pygame.Rect(x, y0, w, h))
        self._t(F_LG, f"Prestige  —  Diplomas: {g.diplomas}", PRESTIGE, x+10, y0+4)
        self._t(F_SM, "Spend Diplomas on permanent upgrades that survive every reset.",
                (100,100,100), x+10, y0+30)
        step = self.ITEM_H + self.ITEM_G
        for i, du in enumerate(DIPLOMA_UPGRADES):
            iy  = y0 + 54 + i * step - self.ps_scroll
            if iy + self.ITEM_H < y0 or iy > y0 + h:
                continue
            card  = pygame.Rect(x, iy, w, self.ITEM_H)
            owned = du["id"] in g.diploma_upgrades_purchased
            ok    = (not owned) and g.diplomas >= du["cost"]
            bg    = (218, 240, 218) if owned else ((235, 225, 248) if ok else CARD_DIM)
            self._shadow(card)
            self._r(bg, card, radius=8, border=1, bc=(173,167,155))
            self._t(F_MD, du["name"], DARK if not owned else (55,135,55), x+14, iy+8)
            self._t(F_SM, du["desc"], (95,95,95), x+14, iy+30)
            self._t(F_SM, f"Cost: {du['cost']} Diplomas", PRESTIGE, x+14, iy+52)
            if owned:
                self._t(F_MD, "✓ OWNED", (55,155,55), x + w - 120, iy+26)
            else:
                btn = pygame.Rect(x + w - 158, iy + (self.ITEM_H-36)//2, 150, 36)
                self._r(PRESTIGE if ok else GRAY, btn, radius=6)
                self._tc(F_SM, f"Buy  {du['cost']} Diplomas", WHITE, btn)
                self._buy_items.append((btn, du["id"], "diploma_upgrade"))
                if not ok and g.diplomas > 0:
                    pct = min(1.0, g.diplomas / du["cost"])
                    pygame.draw.rect(self.screen, (175,168,155), (x+14, iy+self.ITEM_H-10, 220, 5), border_radius=2)
                    pygame.draw.rect(self.screen, PRESTIGE, (x+14, iy+self.ITEM_H-10, int(220*pct), 5), border_radius=2)
        self._unclip()

    def _draw_legacy(self):
        g = self.game
        x, y0, w, h = self._right_area()

        # Header
        self._t(F_LG,
                f"Legacy  —  Honors: {g.honors}  •  Endowments: {g.endowments}  •  Alumni: {g.alumni_points}",
                GOLD, x+10, y0+4)

        # ── Row 1: Honor + Endowment conversion ──────────────────────────────
        panel_h = 76
        py      = y0 + 34
        rate    = g.honor_rate
        half_w  = w // 2 - 5

        honor_r = pygame.Rect(x, py, half_w, panel_h)
        can_h   = g.diplomas >= rate
        self._r((230, 226, 216), honor_r, radius=6, border=1, bc=(180,175,165))
        self._t(F_MD, "Honor Ceremony", DARK, honor_r.x+10, honor_r.y+6)
        self._t(F_SM, f"Spend {rate} Diplomas → 1 Honor", (80,80,80), honor_r.x+10, honor_r.y+26)
        pct_h = min(1.0, g.diplomas / max(1, rate))
        pygame.draw.rect(self.screen, (175,168,155), (honor_r.x+10, honor_r.y+48, 100, 4), border_radius=2)
        pygame.draw.rect(self.screen, GOLD, (honor_r.x+10, honor_r.y+48, int(100*pct_h), 4), border_radius=2)
        hbtn = pygame.Rect(honor_r.right - 132, honor_r.y + (panel_h-32)//2, 124, 32)
        self._r(GREEN if can_h else GRAY, hbtn, radius=6)
        self._tc(F_SM, f"Earn Honor ({rate})", WHITE, hbtn)
        self._buy_items.append((hbtn, None, "honor_convert"))

        endow_r = pygame.Rect(x + w // 2 + 5, py, half_w, panel_h)
        can_e   = g.honors >= 5
        self._r((220, 240, 236), endow_r, radius=6, border=1, bc=(160,190,180))
        self._t(F_MD, "Endowment", DARK, endow_r.x+10, endow_r.y+6)
        self._t(F_SM, "Spend 5 Honors → 1 Endowment", (80,80,80), endow_r.x+10, endow_r.y+26)
        pct_e = min(1.0, g.honors / 5)
        pygame.draw.rect(self.screen, (160,190,180), (endow_r.x+10, endow_r.y+48, 100, 4), border_radius=2)
        pygame.draw.rect(self.screen, ENDOW_COL, (endow_r.x+10, endow_r.y+48, int(100*pct_e), 4), border_radius=2)
        ebtn = pygame.Rect(endow_r.right - 132, endow_r.y + (panel_h-32)//2, 124, 32)
        self._r(ENDOW_COL if can_e else GRAY, ebtn, radius=6)
        self._tc(F_SM, "Earn Endow. (5)", WHITE, ebtn)
        self._buy_items.append((ebtn, None, "endow_convert"))

        # ── Row 2: Alumni conversion ──────────────────────────────────────────
        ar = g.alumni_rate
        alum_y  = py + panel_h + 5
        alum_r  = pygame.Rect(x, alum_y, w, 52)
        can_a   = g.endowments >= ar
        self._r((235, 228, 248), alum_r, radius=6, border=1, bc=(170,145,200))
        self._t(F_MD, "Alumni Network", ALUMNI_COL, alum_r.x+10, alum_r.y+6)
        self._t(F_SM, f"Spend {ar} Endowments → 1 Alumni Point  (boosts everything, never resets)",
                (90,80,110), alum_r.x+185, alum_r.y+10)
        pct_a = min(1.0, g.endowments / max(1, ar))
        pygame.draw.rect(self.screen, (180,165,200), (alum_r.x+10, alum_r.y+38, 160, 4), border_radius=2)
        pygame.draw.rect(self.screen, ALUMNI_COL, (alum_r.x+10, alum_r.y+38, int(160*pct_a), 4), border_radius=2)
        abtn = pygame.Rect(alum_r.right - 185, alum_r.y + 9, 176, 34)
        self._r(ALUMNI_COL if can_a else GRAY, abtn, radius=6)
        self._tc(F_MD, f"Earn Alumni Point ({ar} Endow.)", WHITE, abtn)
        self._buy_items.append((abtn, None, "alumni_convert"))

        # Bonus description row
        bonus_y = alum_y + 52 + 3
        path = "Diplomas  →  Honors  →  Endowments  →  Alumni Points"
        self._t(F_XS, path, (130, 100, 50), x+10, bonus_y)
        self._t(F_XS, "Honor +3% KPS  ·  Endow +10% KPS  ·  Alumni: up to ×315 KPS",
                (100,100,100), x+10, bonus_y + 13)

        # ── Sub-tab bar ────────────────────────────────────────────────────────
        div_y  = bonus_y + 30
        pygame.draw.line(self.screen, (190,185,175), (x+10, div_y), (x+w-10, div_y))
        stab_y = div_y + 5
        stab_w = (w - 20 - 24) // 4   # 4 tabs with 8px gaps
        subtabs_def = [
            ("Honors",     HONOR_UPGRADES,  g.honor_upgrades_purchased),
            ("Endowments", ENDOW_UPGRADES,  g.endow_upgrades_purchased),
            ("Scholars",   SCHOLARS,        g.scholars_purchased),
            ("Alumni",     ALUMNI_UPGRADES, g.alumni_upgrades_purchased),
        ]
        for i, (sname, slist, spurch) in enumerate(subtabs_def):
            sr     = pygame.Rect(x + 10 + i * (stab_w + 8), stab_y, stab_w, 28)
            active = self.lg_subtab == sname
            bought = sum(1 for du in slist if du["id"] in spurch)
            label  = f"{sname} ({bought}/{len(slist)})"
            self._r(CREAM if active else (195,188,175), sr, radius=6)
            self._tc(F_XS, label, DARK if active else (100,100,100), sr)
            self._buy_items.append((sr, sname, "legacy_subtab"))

        # ── Shop list ─────────────────────────────────────────────────────────
        shop_y = stab_y + 36
        if self.lg_subtab == "Honors":
            shop_items = HONOR_UPGRADES
            purchased  = g.honor_upgrades_purchased
            kind_str   = "honor_upgrade"
            currency   = g.honors
            curr_name  = "Honors"
            c_col      = GOLD
            scroll     = self.lg_scroll_h
        elif self.lg_subtab == "Scholars":
            shop_items = SCHOLARS
            purchased  = g.scholars_purchased
            kind_str   = "scholar"
            currency   = g.honors
            curr_name  = "Honors"
            c_col      = GOLD
            scroll     = self.lg_scroll_s
        elif self.lg_subtab == "Alumni":
            shop_items = ALUMNI_UPGRADES
            purchased  = g.alumni_upgrades_purchased
            kind_str   = "alumni_upgrade"
            currency   = g.alumni_points
            curr_name  = "Alumni Pts"
            c_col      = ALUMNI_COL
            scroll     = self.lg_scroll_a
        else:
            shop_items = ENDOW_UPGRADES
            purchased  = g.endow_upgrades_purchased
            kind_str   = "endow_upgrade"
            currency   = g.endowments
            curr_name  = "Endowments"
            c_col      = ENDOW_COL
            scroll     = self.lg_scroll_e

        clip_h = h - (shop_y - y0)
        self._clip(pygame.Rect(x, shop_y, w, clip_h))
        step = self.ITEM_H + self.ITEM_G
        for i, du in enumerate(shop_items):
            iy    = shop_y + i * step - scroll
            if iy + self.ITEM_H < shop_y or iy > shop_y + clip_h:
                continue
            card  = pygame.Rect(x, iy, w, self.ITEM_H)
            owned = du["id"] in purchased
            ok    = (not owned) and currency >= du["cost"]
            if owned:
                bg = (218, 240, 218)
            elif ok:
                bg = (245, 240, 252) if self.lg_subtab == "Alumni" else \
                     (235, 228, 250) if self.lg_subtab == "Honors" else (218, 245, 240)
            else:
                bg = CARD_DIM
            self._r(bg, card, radius=8, border=1, bc=(173,167,155))
            self._t(F_MD, du["name"], DARK if not owned else (55,135,55), x+14, iy+8)
            if "era" in du:
                self._t(F_XS, du["era"], (130, 105, 65), x+14, iy+27)
                self._t(F_SM, du["desc"], (95,95,95), x+14, iy+39)
                bonus_txt = f"{du.get('bonus','')}  ·  Cost: {du['cost']} {curr_name}"
                self._t(F_XS, bonus_txt, (80, 130, 80), x+14, iy+57)
            else:
                self._t(F_SM, du["desc"], (95,95,95), x+14, iy+30)
                self._t(F_SM, f"Cost: {du['cost']} {curr_name}", c_col, x+14, iy+52)
            if owned:
                self._t(F_MD, "✓ OWNED", (55,155,55), x + w - 120, iy+26)
            else:
                btn = pygame.Rect(x + w - 158, iy + (self.ITEM_H-36)//2, 150, 36)
                self._r(c_col if ok else GRAY, btn, radius=6)
                self._tc(F_SM, f"Buy  {du['cost']} {curr_name}", WHITE, btn)
                self._buy_items.append((btn, du["id"], kind_str))
                if not ok and currency > 0:
                    pct = min(1.0, currency / du["cost"])
                    pygame.draw.rect(self.screen, (175,168,155), (x+14, iy+self.ITEM_H-10, 220, 5), border_radius=2)
                    pygame.draw.rect(self.screen, c_col, (x+14, iy+self.ITEM_H-10, int(220*pct), 5), border_radius=2)

        # Research Legacy — endgame repeatable (Alumni tab only, all upgrades purchased)
        if self.lg_subtab == "Alumni" and g.alumni_all_purchased:
            rl_i  = len(ALUMNI_UPGRADES)
            rl_iy = shop_y + rl_i * step - self.lg_scroll_a
            if shop_y <= rl_iy <= shop_y + clip_h:
                rl_card = pygame.Rect(x, rl_iy, w, self.ITEM_H)
                rl_ok   = g.alumni_points >= 2
                rl_bg   = (245, 238, 255) if rl_ok else CARD_DIM
                self._r(rl_bg, rl_card, radius=8, border=2, bc=ALUMNI_COL if rl_ok else (150,140,160))
                rc = g.alumni_research_count
                self._t(F_MD, f"Research Legacy  (×{rc+1})", ALUMNI_COL, x+14, rl_iy+8)
                mult_now = f"×{1.10**rc:.2f}" if rc > 0 else "no bonus yet"
                self._t(F_SM, f"+10% global KPS permanently (repeatable)  —  current: {mult_now}", (80,60,110), x+14, rl_iy+30)
                self._t(F_SM, "Cost: 2 Alumni Pts", ALUMNI_COL, x+14, rl_iy+52)
                rl_btn = pygame.Rect(x + w - 158, rl_iy + (self.ITEM_H-36)//2, 150, 36)
                self._r(ALUMNI_COL if rl_ok else GRAY, rl_btn, radius=6)
                self._tc(F_SM, "Buy  2 Alumni Pts", WHITE, rl_btn)
                self._buy_items.append((rl_btn, None, "alumni_research"))
                if not rl_ok and g.alumni_points > 0:
                    pct = min(1.0, g.alumni_points / 2)
                    pygame.draw.rect(self.screen, (175,168,155), (x+14, rl_iy+self.ITEM_H-10, 220, 5), border_radius=2)
                    pygame.draw.rect(self.screen, ALUMNI_COL, (x+14, rl_iy+self.ITEM_H-10, int(220*pct), 5), border_radius=2)
        self._unclip()

    def _draw_campus_tab(self):
        x, y0, w, h = self._right_area()
        self.campus.draw(self.screen, pygame.Rect(x, y0, w, h),
                         self.game, tile_base=80, theme=self.game.cosmetic_theme)

    def _draw_settings(self):
        g = self.game
        x, y0, w, h = self._right_area()

        if g.sandbox_mode:
            # Sandbox mode UI
            self._r(SANDBOX_C, pygame.Rect(x, y0, w, 48), radius=8)
            self._t(F_LG, "SANDBOX MODE ACTIVE", WHITE, x+14, y0+6)
            self._t(F_SM, "Changes are NOT saved in sandbox mode.", (255,200,200), x+14, y0+30)
            exit_sb = pygame.Rect(x + 10, y0 + 60, 200, 42)
            self._r((55, 140, 75), exit_sb, radius=8)
            self._t(F_MD, "Exit Sandbox", WHITE, exit_sb.x+16, exit_sb.y+10)
            self._buy_items.append((exit_sb, None, "toggle_sandbox"))
            return

        self._t(F_LG, "Settings & Statistics", DARK, x+10, y0+4)

        # School name input
        self._t(F_SM, "School Name:", (80, 80, 80), x+20, y0+38)
        input_rect = pygame.Rect(x+135, y0+32, w-155, 28)
        self._name_input_rect = input_rect
        active = self._name_input_active
        display = self._name_input_text if active else self.game.school_name
        self._r(WHITE if active else (230, 226, 216), input_rect, radius=4,
                border=2, bc=ACCENT if active else (150, 145, 135))
        txt_surf = F_SM.render(display, True, DARK)
        self._clip(pygame.Rect(input_rect.x+4, input_rect.y, input_rect.w-8, input_rect.h))
        self.screen.blit(txt_surf, (input_rect.x+4,
                                    input_rect.centery - txt_surf.get_height()//2))
        self._unclip()
        if active and (pygame.time.get_ticks() // 500) % 2 == 0:
            cx = input_rect.x + 4 + txt_surf.get_width() + 1
            pygame.draw.line(self.screen, DARK, (cx, input_rect.y+4), (cx, input_rect.bottom-4), 1)

        stats = [
            ("KP this run",     fmt(g.total_kp)),
            ("All-time KP",     fmt(g.all_time_kp)),
            ("Best run KP",     fmt(g.best_run_kp)),
            ("Best KP/s",       fmt(g.best_kps)),
            ("Total clicks",    str(g.total_clicks)),
            ("Max combo",       str(g.max_combo_reached)),
            ("Prestige count",  str(g.prestige_count)),
            ("Diplomas",        str(g.diplomas)),
            ("Honors",          str(g.honors)),
            ("Endowments",      str(g.endowments)),
            ("Alumni Pts",      str(g.alumni_points)),
            ("Merit points",    str(g.merit_points)),
            ("Achievements",    f"{len(g.achievements_unlocked)}/{len(ACHIEVEMENTS)}"),
            ("Skills",          f"{len(g.skills_purchased)}/{len(SKILLS)}"),
            ("Session time",    fmt_time(g.session_seconds)),
        ]
        # Two-column layout: rows × 2 cols
        col_w  = (w - 20) // 2
        row_h  = 30
        ys     = y0 + 72
        n_rows = (len(stats) + 1) // 2
        for i, (label, val) in enumerate(stats):
            col    = i % 2
            row    = i // 2
            rx     = x + 10 + col * col_w
            ry2    = ys + row * row_h
            self._r((238, 233, 222), pygame.Rect(rx, ry2, col_w - 4, 26), radius=5)
            self._t(F_XS, label, (80, 80, 80), rx + 8, ry2 + 7)
            self._t(F_XS, val,   DARK,          rx + 130, ry2 + 7)

        # ── Campus Theme picker ──────────────────────────────────────────────────
        theme_y = ys + n_rows * row_h + 16  # below stats grid
        self._t(F_SM, "Campus Theme", (80, 80, 80), x + 10, theme_y)
        theme_y += 22

        btn_w = (w - 24) // len(COSMETIC_THEMES)
        for ti, th in enumerate(COSMETIC_THEMES):
            tx = x + 10 + ti * (btn_w + 4)
            is_active = g.cosmetic_theme == th["id"]
            always_ok = th.get("always_unlocked", False)
            cw_req    = th.get("cw_req")
            unlocked  = always_ok or (cw_req and self.world.cosmetic_unlocked(th["id"]))

            if is_active:
                tbg = ACCENT
                tc2 = WHITE
            elif unlocked:
                tbg = (200, 195, 185)
                tc2 = DARK
            else:
                tbg = (160, 155, 148)
                tc2 = (100, 95, 90)

            tbtn = pygame.Rect(tx, theme_y, btn_w - 2, 36)
            self._r(tbg, tbtn, radius=6)
            self._tc(F_XS, th["name"], tc2, tbtn)
            if not unlocked and cw_req:
                cw_cost = next((it["cost"] for it in CW_SHOP if it["id"] == cw_req), "?")
                self._t(F_XS, f"🔒 {cw_cost}CW", (120, 115, 108),
                        tx + 2, theme_y + 36)
            if unlocked:
                self._buy_items.append((tbtn, th["id"], "set_theme"))

        since = time.time() - g.last_save_time
        ys_end = ys + n_rows * row_h + 4
        self._t(F_SM, f"Auto-saved {int(since)}s ago", (120,120,120), x+10, ys_end + 76)

        # KPS history sparkline
        sp_y = ys_end + 20
        sp_h = 52
        sp_w = w - 20
        self._r((230, 226, 216), pygame.Rect(x+10, sp_y, sp_w, sp_h), radius=5)
        self._t(F_XS, "KP/s history (last 2 hrs)", (100,100,100), x+16, sp_y+4)
        samples = g._kps_samples
        if len(samples) >= 2:
            import math as _m
            max_v = max(s[1] for s in samples) or 1.0
            gx0, gx1 = x+16, x+10+sp_w-6
            gy0, gy1 = sp_y+sp_h-6, sp_y+16
            pts = []
            for i, (_, kv) in enumerate(samples):
                px = int(gx0 + (gx1-gx0) * i / max(1, len(samples)-1))
                py2 = int(gy1 + (gy0-gy1) * (1.0 - kv/max_v))
                pts.append((px, py2))
            if len(pts) >= 2:
                pygame.draw.lines(self.screen, ACCENT, False, pts, 2)
            self._t(F_XS, fmt(max_v)+"/s", ACCENT, gx1-36, sp_y+6)
        else:
            self._tc(F_XS, "Collecting data...", (150,150,150),
                     pygame.Rect(x+10, sp_y, sp_w, sp_h))

        ry = sp_y + sp_h + 8
        # Reset button
        if self._reset_confirm:
            self._r((200, 60, 60), pygame.Rect(x+10, ry, 220, 42), radius=8)
            self._t(F_MD, "Click again to RESET", WHITE, x+18, ry+10)
            self._buy_items.append((pygame.Rect(x+10, ry, 220, 42), None, "reset_confirm"))
        else:
            self._r((180, 70, 70), pygame.Rect(x+10, ry, 200, 42), radius=8)
            self._t(F_MD, "Reset Save", WHITE, x+22, ry+10)
            self._buy_items.append((pygame.Rect(x+10, ry, 200, 42), None, "reset_ask"))

        # Mute toggle
        muted   = audio.is_muted()
        mu_rect = pygame.Rect(x + 10, ry + 54, 180, 38)
        self._r((140, 55, 55) if muted else (55, 140, 75), mu_rect, radius=8)
        self._t(F_MD, "Unmute Audio" if muted else "Mute Audio", WHITE, mu_rect.x+14, mu_rect.y+9)
        self._buy_items.append((mu_rect, None, "toggle_mute"))

        # Headmaster tips toggle
        hm_on   = g.show_headmaster
        hm_rect = pygame.Rect(x + 10, ry + 104, 260, 38)
        self._r(ACCENT if hm_on else (140, 135, 125), hm_rect, radius=8)
        self._t(F_MD, f"Principal Tips:  {'ON' if hm_on else 'OFF'}", WHITE,
                hm_rect.x+14, hm_rect.y+9)
        self._buy_items.append((hm_rect, None, "toggle_headmaster"))

        # Sandbox toggle
        sb_rect = pygame.Rect(x + 10, ry + 154, 260, 38)
        self._r((100, 80, 60), sb_rect, radius=8)
        self._t(F_MD, "Enter Sandbox Mode (explore)", WHITE, sb_rect.x+12, sb_rect.y+9)
        self._buy_items.append((sb_rect, None, "toggle_sandbox"))
        self._t(F_XS, "Costs ÷1000 · all buildings visible · no saves", (150,140,130), x+10, ry+198)

        # Fullscreen toggle
        fs_rect = pygame.Rect(x + 10, ry + 204, 260, 38)
        fs_label = "Exit Fullscreen" if self._fullscreen else "Enter Fullscreen"
        fs_col   = (38, 100, 160) if self._fullscreen else (50, 120, 80)
        self._r(fs_col, fs_rect, radius=8)
        self._t(F_MD, fs_label, WHITE, fs_rect.x+12, fs_rect.y+9)
        self._buy_items.append((fs_rect, None, "toggle_fullscreen"))

    # ── Worlds tab ───────────────────────────────────────────────────────────

    def _draw_worlds(self):
        g  = self.game
        w_world = self.world
        x, y0, w, h = self._right_area()
        CARD_W  = 284
        CARD_H  = 56      # compact to fit all 10 zones + CW bar in view
        CARD_G  = 3
        det_x   = x + CARD_W + 8
        det_w   = w - CARD_W - 8

        # ── Left: zone list ────────────────────────────────────────────────────
        self._clip(pygame.Rect(x, y0, CARD_W, h))
        # Zone 1 card (always active baseline)
        card_y = y0 + 2
        z1_card = pygame.Rect(x, card_y, CARD_W, CARD_H)
        sel1 = self.worlds_sel_zone == 1
        self._r((210, 220, 235) if sel1 else CARD_DIM, z1_card, radius=6,
                border=2 if sel1 else 1, bc=ACCENT if sel1 else (170, 165, 155))
        self._t(F_SM, "🏫  Zone 1: Modern School", DARK, x+8, card_y+5)
        self._t(F_XS, f"KPS: {fmt(g.kps())}   KP: {fmt(g.kp)}", (60,100,60), x+8, card_y+22)
        self._t(F_XS, f"Prestige: {g.prestige_count}  ·  Alumni: {g.total_alumni_earned}", (80,80,80), x+8, card_y+37)
        self._t(F_XS, "Active zone (main game)", (100,130,180), x+8, card_y+44)
        self._buy_items.append((z1_card, 1, "zone_select"))
        card_y += CARD_H + CARD_G

        for zdef in ZONE_DEFS:
            zid = zdef["id"]
            zg  = w_world.zones[zid]
            locked = not w_world.is_unlocked(zid, g)
            sel    = self.worlds_sel_zone == zid
            col_t  = zdef["theme_color"]

            card  = pygame.Rect(x, card_y, CARD_W, CARD_H)
            if locked:
                bg = (195, 188, 178)
            elif sel:
                bg = tuple(min(255, c + 60) for c in col_t)
            else:
                bg = tuple(min(255, c + 20) for c in col_t)
            self._r(bg, card, radius=6, border=2 if sel else 1,
                    bc=col_t if sel else (150, 144, 135))
            icon = zdef.get("icon", "?")
            lbl  = f"{icon}  Zone {zid}: {zdef['name']}"
            self._t(F_SM, lbl, DARK if not locked else (130,125,115), x+8, card_y+6)
            if locked:
                req = zdef["unlock"]
                if req["type"] == "prestige":
                    src = f"Zone {req['zone']} prestige ×{req['value']}"
                else:
                    src = f"Zone {req['zone']} Alumni ×{req['value']}"
                self._t(F_XS, f"🔒  Unlock: {src}", (110,105,100), x+8, card_y+22)
            else:
                self._t(F_XS, f"KPS: {fmt(zg.kps())}   KP: {fmt(zg.kp)}", (60,100,60), x+8, card_y+22)
                self._t(F_XS, f"Prestige: {zg.prestige_count}  ·  {zg.l1_name[:8]}: {zg.l1}", (60,60,60), x+8, card_y+38)
                self._t(F_XS, f"Click to manage", (80,80,100), x+8, card_y+44)
            self._buy_items.append((card, zid, "zone_select"))
            card_y += CARD_H + CARD_G
        self._unclip()

        # Multiverse Shop button (below zone list, above CW bar)
        mv_btn = pygame.Rect(x, y0 + h - 44, CARD_W, 20)
        mv_sel = self.worlds_sel_zone == 0
        self._r((55, 35, 80) if mv_sel else (45, 28, 65), mv_btn, radius=4)
        self._tc(F_XS, "✦  MULTIVERSE SHOP", (220, 190, 255), mv_btn)
        self._buy_items.append((mv_btn, 0, "zone_select"))

        # Cosmic Wisdom display
        cw_y = y0 + h - 22
        self._r((35, 30, 55), pygame.Rect(x, cw_y, CARD_W, 20), radius=4)
        self._t(F_XS, f"✦ Cosmic Wisdom: {w_world.cosmic_wisdom}", (200, 180, 255), x+6, cw_y+3)

        # ── Right: zone detail ────────────────────────────────────────────────
        pygame.draw.line(self.screen, (185, 178, 165), (det_x - 4, y0), (det_x - 4, y0 + h), 1)

        # Multiverse Shop selected
        if self.worlds_sel_zone == 0:
            self._draw_cw_shop(det_x, y0, det_w, h)
            return

        # Zone 1 selected — show summary
        if self.worlds_sel_zone == 1:
            self._t(F_LG, "Zone 1: Modern School (Active)", ACCENT, det_x + 8, y0 + 6)
            self._t(F_SM, "This is your main zone — use the other tabs to manage it.",
                    (80,80,80), det_x + 8, y0 + 34)
            stats = [
                f"KP/s: {fmt(g.kps())}   KP: {fmt(g.kp)}",
                f"All-time KP: {fmt(g.all_time_kp)}",
                f"Prestige ×{g.prestige_count}   Diplomas: {g.diplomas}",
                f"Honors: {g.honors}   Endowments: {g.endowments}   Alumni: {g.alumni_points}",
                f"Merit: {g.merit_points} MP",
                f"Cosmic Wisdom earned: {w_world.cosmic_wisdom} CW",
            ]
            for i, s in enumerate(stats):
                self._t(F_SM, s, DARK, det_x + 8, y0 + 60 + i * 22)
            # Other zones total KPS
            ext_kps = w_world.total_kps(g)
            if ext_kps > 0:
                self._t(F_MD, f"All other zones: {fmt(ext_kps)} KP/s combined", GOLD,
                        det_x + 8, y0 + 60 + len(stats) * 22 + 10)
            return

        zid = self.worlds_sel_zone
        if zid not in w_world.zones:
            return
        zg     = w_world.zones[zid]
        zdef   = next(z for z in ZONE_DEFS if z["id"] == zid)
        locked = not w_world.is_unlocked(zid, g)
        col_t  = zdef["theme_color"]

        # Theme header bar
        hdr_h = 46
        self._r(col_t, pygame.Rect(det_x, y0, det_w, hdr_h), radius=6)
        icon = zdef.get("icon", "")
        self._t(F_LG, f"{icon}  Zone {zid}: {zdef['name']}", WHITE, det_x + 10, y0 + 6)
        self._t(F_XS, zdef["desc"], (255, 255, 200), det_x + 10, y0 + 28)

        if locked:
            req = zdef["unlock"]
            if req["type"] == "prestige":
                src_name = "Zone 1" if req["zone"] == 1 else f"Zone {req['zone']}"
                msg = f"Unlock by prestiging {src_name} {req['value']} time(s)."
            else:
                src_name = "Zone 1" if req["zone"] == 1 else f"Zone {req['zone']}"
                msg = f"Unlock by earning {req['value']} Alumni Point(s) in {src_name}."
            self._r(CARD_LOCK, pygame.Rect(det_x, y0+hdr_h+4, det_w, 60), radius=6)
            self._t(F_MD, "🔒  Zone Locked", DARK, det_x+12, y0+hdr_h+12)
            self._t(F_SM, msg, (80,80,80), det_x+12, y0+hdr_h+34)
            return

        # Sub-tab bar
        stab_y = y0 + hdr_h + 5
        stabs  = ["Overview", "Buildings", "Upgrades", "Prestige"]
        stab_w = (det_w - 12) // len(stabs)
        for i, stn in enumerate(stabs):
            sr = pygame.Rect(det_x + 6 + i * (stab_w + 2), stab_y, stab_w, 26)
            active = self.worlds_subtab == stn
            self._r(CREAM if active else (185, 178, 165), sr, radius=5)
            self._tc(F_XS, stn, DARK if active else WHITE, sr)
            self._buy_items.append((sr, stn, "worlds_subtab"))

        cont_y = stab_y + 32
        cont_h = h - (cont_y - y0) - 2

        if self.worlds_subtab == "Overview":
            self._draw_zone_overview(zid, zg, zdef, det_x, cont_y, det_w, cont_h)
        elif self.worlds_subtab == "Buildings":
            self._draw_zone_buildings(zid, zg, det_x, cont_y, det_w, cont_h)
        elif self.worlds_subtab == "Upgrades":
            self._draw_zone_upgrades(zid, zg, det_x, cont_y, det_w, cont_h)
        elif self.worlds_subtab == "Prestige":
            self._draw_zone_prestige(zid, zg, zdef, det_x, cont_y, det_w, cont_h)

    def _draw_cw_shop(self, x: int, y: int, w: int, h: int):
        """Multiverse Shop — purchase upgrades with Cosmic Wisdom."""
        g = self.game
        ww = self.world

        self._t(F_LG, "✦  Multiverse Shop", (180, 140, 255), x + 10, y + 6)
        cw_str = f"Cosmic Wisdom: {ww.cosmic_wisdom} CW"
        self._t(F_MD, cw_str, (200, 180, 255), x + 10, y + 32)
        self._t(F_XS, "Earn CW by prestiging and converting in any zone.",
                (130, 120, 160), x + 10, y + 52)

        ITEM_W = (w - 24) // 2
        ITEM_H = 88
        ITEM_G = 6
        col0   = x + 6
        col1   = x + 6 + ITEM_W + ITEM_G
        iy     = y + 72

        for i, item in enumerate(CW_SHOP):
            cx = col0 if i % 2 == 0 else col1
            if i % 2 == 0 and i > 0:
                iy += ITEM_H + ITEM_G

            owned    = item["id"] in ww.cw_purchased
            req_ok   = item.get("req") is None or item["req"] in ww.cw_purchased
            can_buy  = not owned and req_ok and ww.cosmic_wisdom >= item["cost"]

            if owned:
                bg = (50, 70, 50)
                bc = (80, 160, 80)
            elif can_buy:
                bg = (40, 35, 65)
                bc = (150, 120, 220)
            else:
                bg = (35, 30, 50)
                bc = (80, 70, 100)

            card = pygame.Rect(cx, iy, ITEM_W, ITEM_H)
            self._r(bg, card, radius=6, border=1, bc=bc)

            name_col = (220, 200, 255) if not owned else (140, 200, 140)
            self._t(F_SM, item["name"], name_col, cx + 8, iy + 6)

            if owned:
                self._t(F_XS, "✓ Purchased", (100, 200, 100), cx + 8, iy + 26)
            elif not req_ok:
                req_name = next((it["name"] for it in CW_SHOP if it["id"] == item["req"]), "?")
                self._t(F_XS, f"Requires: {req_name}", (180, 140, 100), cx + 8, iy + 26)
            else:
                cost_col = (255, 210, 80) if can_buy else (160, 140, 100)
                self._t(F_XS, f"Cost: {item['cost']} CW", cost_col, cx + 8, iy + 26)

            # Wrap description to 2 lines
            desc = item["desc"]
            if len(desc) > 38:
                desc = desc[:38] + "…"
            self._t(F_XS, desc, (180, 170, 200), cx + 8, iy + 42)

            if not owned and req_ok:
                btn_col = (100, 70, 180) if can_buy else (60, 50, 80)
                btn = pygame.Rect(cx + ITEM_W - 58, iy + ITEM_H - 26, 52, 20)
                self._r(btn_col, btn, radius=4)
                self._tc(F_XS, "Buy" if can_buy else "—", WHITE, btn)
                if can_buy:
                    self._buy_items.append((btn, item["id"], "cw_buy"))

        # Handle bottom of last row (if odd number of items, move iy forward)
        if len(CW_SHOP) % 2 == 1:
            iy += ITEM_H + ITEM_G

    def _draw_zone_overview(self, zid, zg, zdef, x, y0, w, h):
        m  = zdef["mechanic"]
        ct = zdef["theme_color"]

        # Stats row
        stats = [
            ("KP",      fmt(zg.kp)),
            ("KP/s",    fmt(zg.kps())),
            ("All-time",fmt(zg.all_time_kp)),
            ("Prestige",str(zg.prestige_count)),
            (zg.l1_name[:9], str(zg.l1)),
            (zg.l2_name[:9], str(zg.l2)),
        ]
        col_w = w // len(stats)
        for i, (label, val) in enumerate(stats):
            cx = x + i * col_w + 6
            self._r((228, 222, 210), pygame.Rect(x + i * col_w + 2, y0, col_w - 4, 42), radius=5)
            self._t(F_XS, label, (80,80,80), cx, y0 + 4)
            self._t(F_MD, val, DARK, cx, y0 + 18)

        # Mechanic section
        mec_y = y0 + 50
        self._r((228, 222, 210), pygame.Rect(x, mec_y, w, 82), radius=6)
        self._t(F_MD, f"⚙  {m['passive_name']}", ct, x+10, mec_y+6)
        self._t(F_XS, m["passive_desc"], (80,80,80), x+10, mec_y+26)
        # Progress bar
        bar_w = w - 20
        bar_r = pygame.Rect(x + 10, mec_y + 44, bar_w, 10)
        pygame.draw.rect(self.screen, (170,165,155), bar_r, border_radius=4)
        fill_c = (220,80,60) if m["inverted"] else ct
        pct_val = zg.mechanic_value
        pygame.draw.rect(self.screen, fill_c,
                         pygame.Rect(x+10, mec_y+44, int(bar_w*pct_val), 10), border_radius=4)
        pct_lbl = f"{pct_val*100:.0f}%"
        if m["inverted"]:
            eff = f"  KPS ×{1.0-pct_val*m['max_effect']:.2f}"
        else:
            eff = f"  KPS ×{1.0+pct_val*m['max_effect']:.2f}"
        self._t(F_XS, pct_lbl + eff, (80,80,80), x+10, mec_y+58)

        # Active mechanic
        act_y = mec_y + 90
        can   = zg.can_active()
        self._r((222, 215, 200), pygame.Rect(x, act_y, w, 60), radius=6)
        self._t(F_MD, f"⚡  {m['active_name']}", ct, x+10, act_y+6)
        self._t(F_XS, m["active_desc"], (80,80,80), x+10, act_y+24)
        cd_lbl = "Ready!" if zg.mechanic_active_cd <= 0 else f"Cooldown: {zg.mechanic_active_cd:.0f}s"
        if m["active_cost_layer"] == 1 and m["active_cost"] > 0:
            cd_lbl += f"  (Cost: {m['active_cost']} {zg.l1_name})"
        act_btn = pygame.Rect(x + w - 148, act_y + 12, 140, 36)
        self._r(ct if can else GRAY, act_btn, radius=6)
        self._tc(F_SM, "Activate!" if can else cd_lbl, WHITE, act_btn)
        self._buy_items.append((act_btn, zid, "zone_active"))

        # Pending event
        if zg.pending_event:
            ev    = zg.pending_event
            ev_y  = act_y + 68
            ev_r  = pygame.Rect(x, ev_y, w, 42)
            self._r((38, 140, 68), ev_r, radius=6)
            self._t(F_MD, f"EVENT: {ev['name']}", GOLD, x+10, ev_y+4)
            self._t(F_XS, ev.get("desc",""), (200,255,200), x+10, ev_y+24)
            collect_btn = pygame.Rect(x + w - 128, ev_y + 5, 120, 32)
            self._r(GREEN, collect_btn, radius=5)
            self._tc(F_SM, "Collect!", WHITE, collect_btn)
            self._buy_items.append((collect_btn, zid, "zone_event"))

        # ── Hero Creation / Hero Display (Zone 10 only) ──────────────────────
        if zid == 10:
            from data import HERO_CREATION_COST, HERO_PATH_STATS
            hero_y = act_y + 68 + (42 if zg.pending_event else 0) + 8
            g = self.game
            if g.hero is None:
                # Creation panel
                can_h = g.diplomas >= HERO_CREATION_COST
                hpanel = pygame.Rect(x, hero_y, w, 110)
                self._r((48, 36, 80) if can_h else (60, 55, 70), hpanel, radius=8)
                self._t(F_LG, "⚔  Create Your Hero", (220, 180, 255), x+10, hero_y+6)
                self._t(F_SM,
                        "Your curriculum choices shape the hero's stats.",
                        (180, 160, 220), x+10, hero_y+30)
                self._t(F_SM,
                        f"Cost: {HERO_CREATION_COST} Diplomas (you have {g.diplomas})",
                        (220, 200, 100) if can_h else (160, 140, 140),
                        x+10, hero_y+50)
                self._t(F_XS,
                        "The hero will open the first Hero Academy in Zone 10.",
                        (150, 140, 180), x+10, hero_y+70)
                hbtn = pygame.Rect(x + w - 178, hero_y + 36, 170, 38)
                self._r((100, 60, 180) if can_h else GRAY, hbtn, radius=6)
                self._tc(F_MD, "Create Hero!", WHITE, hbtn)
                if can_h:
                    self._buy_items.append((hbtn, None, "create_hero"))
            else:
                # Hero display panel
                hero = g.hero
                hpanel = pygame.Rect(x, hero_y, w, 178)
                self._r((30, 25, 58), hpanel, radius=8)
                dom = hero.get("dominant_path", "Foundation")
                dom_col = PATH_FG.get(dom, (200, 180, 255))
                self._t(F_LG, f"⚔  {hero['name']}", (220, 200, 255), x+10, hero_y+6)
                self._t(F_XS, f"Dominant Path: {dom}", dom_col, x+10, hero_y+26)
                stats = hero.get("stats", {})
                stat_labels = [(v[1], stats.get(v[0], 0))
                               for v in HERO_PATH_STATS.values()]
                col_w2 = w // 3
                for si, (label, score) in enumerate(stat_labels):
                    sx = x + (si % 3) * col_w2 + 6
                    sy = hero_y + 42 + (si // 3) * 28
                    self._t(F_XS, label, (160, 150, 200), sx, sy)
                    bar_r = pygame.Rect(sx, sy + 14, col_w2 - 12, 6)
                    pygame.draw.rect(self.screen, (60, 50, 80), bar_r, border_radius=3)
                    pygame.draw.rect(self.screen, dom_col,
                                     pygame.Rect(sx, sy+14, int((col_w2-12)*score/50), 6),
                                     border_radius=3)
                    self._t(F_XS, str(score), (200, 190, 255), sx + col_w2 - 22, sy)
                # Passive bonus summary
                ints  = stats.get("intelligence", 0)
                agi   = stats.get("agility", 0)
                res   = stats.get("resilience", 0)
                tech  = stats.get("tech_power", 0)
                rep   = stats.get("reputation", 0)
                trans = stats.get("transcendence", 0)
                pygame.draw.line(self.screen, (60, 50, 90),
                                 (x+10, hero_y+100), (x+w-10, hero_y+100))
                self._t(F_XS, "Passive bonuses:", (130, 115, 170), x+10, hero_y+104)
                self._t(F_XS,
                        f"+{ints*0.5:.1f}% KPS (Int)  "
                        f"+{agi*0.5:.1f}% click (Agi)  "
                        f"-{res*0.2:.1f}% costs (Res)",
                        (180, 170, 220), x+10, hero_y+118)
                self._t(F_XS,
                        f"+{tech*0.5:.1f}% bldgs (Tech)  "
                        f"+{rep*0.5:.1f} dip/prestige (Rep)  "
                        f"+{trans*0.4:.1f}% KPS (Trans)",
                        (180, 170, 220), x+10, hero_y+134)

        # Study Zone button
        study_y = h + y0 - 52
        study_r = pygame.Rect(x + 4, study_y, w - 8, 44)
        self._r(ct, study_r, radius=8, border=2, bc=tuple(max(0, c-40) for c in ct))
        self._tc(F_MD, f"Study  +{fmt(zg.click_power)} KP", WHITE, study_r)
        self._buy_items.append((study_r, zid, "zone_study"))

    def _draw_zone_buildings(self, zid, zg, x, y0, w, h):
        ITEM_H = 80
        ITEM_G = 4
        step   = ITEM_H + ITEM_G
        self._clip(pygame.Rect(x, y0, w, h))
        for i, b in enumerate(zg.buildings):
            iy  = y0 + i * step - self.worlds_b_scroll
            if iy + ITEM_H < y0 or iy > y0 + h:
                continue
            cnt = zg.building_counts[b["name"]]
            if zg.all_time_kp < b["unlock_at"] and cnt == 0:
                card = pygame.Rect(x, iy, w, ITEM_H)
                self._r(CARD_LOCK, card, radius=7)
                self._t(F_MD, "???  (locked)", (152,147,137), x+14, iy+28)
                continue

            mult = self.buy_mult
            if mult == "max":
                n_buy = max(1, zg.building_max_buyable(b["name"]))
                cost  = zg.building_cost_n(b["name"], n_buy)
                ok    = zg.building_max_buyable(b["name"]) > 0
                lbl   = f"×{zg.building_max_buyable(b['name'])}  {fmt(cost)} KP" if ok else f"Buy  {fmt(zg.building_cost(b['name']))} KP"
            else:
                n_buy = int(mult)
                cost  = zg.building_cost_n(b["name"], n_buy)
                ok    = zg.kp >= cost
                lbl   = f"×{n_buy}  {fmt(cost)} KP" if n_buy > 1 else f"Buy  {fmt(cost)} KP"

            card = pygame.Rect(x, iy, w, ITEM_H)
            self._r(CARD_OK if ok else CARD_DIM, card, radius=7, border=1, bc=(173,167,155))
            self._t(F_MD, f"{b['name']}  ×{cnt}", DARK, x+14, iy+8)
            star = zg.star_milestones_hit.get(b["name"], 0)
            if star:
                self.screen.blit(F_SM.render("★"*star, True, GOLD),
                                 (x+14+F_MD.size(f"{b['name']}  ×{cnt}")[0]+6, iy+10))
            self._t(F_SM, b["desc"], (95,95,95), x+14, iy+30)
            if cnt > 0:
                self._t(F_SM, f"Producing: {fmt(zg.building_kps(b['name']))} KP/s", (48,126,55), x+14, iy+52)
            btn = pygame.Rect(x + w - 168, iy + (ITEM_H-36)//2, 160, 36)
            self._r(GREEN if ok else GRAY, btn, radius=6)
            self._tc(F_SM, lbl, WHITE, btn)
            self._buy_items.append((btn, (zid, b["name"]), "zone_buy_bld"))
            if not ok:
                pct = min(1.0, zg.kp / max(1, cost))
                pygame.draw.rect(self.screen, (175,168,155), (x+14, iy+ITEM_H-10, 220, 5), border_radius=2)
                pygame.draw.rect(self.screen, (100,180,100), (x+14, iy+ITEM_H-10, int(220*pct), 5), border_radius=2)
        self._unclip()

    def _draw_zone_upgrades(self, zid, zg, x, y0, w, h):
        ITEM_H = 80
        ITEM_G = 4
        step   = ITEM_H + ITEM_G
        self._clip(pygame.Rect(x, y0, w, h))
        row = 0
        for u in zg.upgrades:
            if u["id"] in zg.upgrades_purchased:
                continue
            iy = y0 + row * step - self.worlds_u_scroll
            if iy + ITEM_H >= y0 and iy <= y0 + h:
                cost = zg.upgrade_cost(u["id"])
                ok   = zg.kp >= cost
                card = pygame.Rect(x, iy, w, ITEM_H)
                self._r((232, 248, 232) if ok else CARD_DIM, card, radius=7, border=1, bc=(173,167,155))
                self._t(F_MD, u["name"], DARK, x+14, iy+8)
                self._t(F_SM, f"{u['desc']}   →  {u['target']}", (95,95,95), x+14, iy+30)
                btn = pygame.Rect(x + w - 158, iy + (ITEM_H-36)//2, 150, 36)
                self._r(GREEN if ok else GRAY, btn, radius=6)
                self._tc(F_SM, f"{fmt(cost)} KP", WHITE, btn)
                self._buy_items.append((btn, (zid, u["id"]), "zone_buy_upg"))
                if not ok:
                    pct = min(1.0, zg.kp / max(1, cost))
                    pygame.draw.rect(self.screen, (175,168,155), (x+14, iy+ITEM_H-10, 220, 5), border_radius=2)
                    pygame.draw.rect(self.screen, (100,180,100), (x+14, iy+ITEM_H-10, int(220*pct), 5), border_radius=2)
            row += 1

        y_sep = y0 + row * step - self.worlds_u_scroll + 10
        if y0 <= y_sep < y0 + h:
            pygame.draw.line(self.screen, (190,185,175), (x+10, y_sep), (x+w-10, y_sep))
            self._t(F_SM, "Purchased:", (130,130,130), x+14, y_sep+4)
        row2 = 0
        for u in zg.upgrades:
            if u["id"] not in zg.upgrades_purchased:
                continue
            iy = y_sep + 22 + row2 * 22 - self.worlds_u_scroll
            if y0 <= iy < y0 + h:
                self._t(F_SM, f"  ✓  {u['name']}", (100,160,100), x+14, iy)
            row2 += 1
        self._unclip()

    def _draw_zone_prestige(self, zid, zg, zdef, x, y0, w, h):
        pl = zdef["prestige_layers"]

        # ── L1: Zone prestige ─────────────────────────────────────────────────
        panel_h = 70
        py = y0 + 4
        l1  = pl[0]
        can_p = zg.prestige_eligible

        # Zone 4: pending School of Thought choice replaces the prestige button
        if zid == 4 and getattr(zg, '_pending_thought_choice', False):
            schools = [
                ("platonic",     "Platonic",     "+12% zone KPS per choice",   (88, 44, 152)),
                ("aristotelian", "Aristotelian", "+25% Scrolls per prestige",  (38, 110, 58)),
                ("stoic",        "Stoic",         "-5% building costs per choice (cap 50%)", (50, 80, 148)),
            ]
            choice_h = 52 + len(schools) * 44
            pane_r = pygame.Rect(x, py, w, choice_h)
            self._r((245, 238, 200), pane_r, radius=6, border=2, bc=(160, 130, 50))
            self._t(F_MD, "Choose Your School of Thought", (110, 70, 10), x+10, py+8)
            self._t(F_XS, "Your choice shapes this prestige permanently.", (120, 90, 30), x+10, py+28)
            for si, (key, name, desc, col) in enumerate(schools):
                by = py + 48 + si * 44
                count = zg._thought_school_counts.get(key, 0)
                btn_r = pygame.Rect(x + 6, by, w - 12, 38)
                self._r(col, btn_r, radius=6)
                self._t(F_MD, f"{name}  (chosen ×{count})", WHITE, x + 16, by + 5)
                self._t(F_XS, desc, (210, 200, 255) if col[0] < 80 else (200, 240, 200),
                        x + 16, by + 22)
                self._buy_items.append((btn_r, (zid, key), "zone_thought"))
            py += choice_h + 5
        else:
            pane_r = pygame.Rect(x, py, w, panel_h)
            self._r((230, 225, 215), pane_r, radius=6, border=1, bc=(180,175,165))
            self._t(F_MD, f"Zone Prestige  →  {l1['name']}", PRESTIGE, x+10, py+6)
            self._t(F_SM, f"Reset zone (2M KP) → earn {l1['name']}. {l1['desc']}",
                    (80,80,80), x+10, py+26)
            if can_p:
                earn = zg.l1_on_prestige
                self._t(F_XS, f"Ready! You'll earn {earn} {l1['name']}.", (50,140,50), x+10, py+48)
            else:
                req = l1.get("prestige_kp", 2_000_000)
                pct = min(1.0, zg.total_kp / max(1, req))
                pygame.draw.rect(self.screen, (175,168,155), (x+10, py+50, 200, 5), border_radius=2)
                pygame.draw.rect(self.screen, PRESTIGE, (x+10, py+50, int(200*pct), 5), border_radius=2)
            pbtn = pygame.Rect(x + w - 150, py + (panel_h-34)//2, 142, 34)
            self._r(PRESTIGE if can_p else GRAY, pbtn, radius=6)
            self._tc(F_SM, f"Prestige  ({zg.l1} {l1['abbr']})", WHITE, pbtn)
            self._buy_items.append((pbtn, zid, "zone_prestige"))
            py += panel_h + 5

        # Zone 9: Dark Legacy info — show sin-at-prestige consequence
        if zid == 9:
            sin_pct  = zg.mechanic_value * 100
            earn_now = zg.l1_on_prestige
            legacy   = zg.mechanic_value * 40
            sin_h    = 48
            sin_r    = pygame.Rect(x, py, w, sin_h)
            self._r((55, 18, 28), sin_r, radius=6)
            self._t(F_MD, "Dark Legacy", (255, 90, 90), x + 10, py + 6)
            self._t(F_XS,
                    f"Sin {sin_pct:.0f}% → earn {earn_now} Soul Marks · "
                    f"{legacy:.0f}% sin carries into next run",
                    (200, 140, 140), x + 10, py + 26)
            py += sin_h + 5

        # Zone 4: current School bonuses summary
        if zid == 4 and not getattr(zg, '_pending_thought_choice', False):
            tc = zg._thought_school_counts
            if any(tc.values()):
                sum_h = 36
                sum_r = pygame.Rect(x, py, w, sum_h)
                self._r((240, 230, 200), sum_r, radius=6)
                p_txt = f"Platonic ×{tc['platonic']} (+{tc['platonic']*12}% KPS)"
                a_txt = f"Aristotelian ×{tc['aristotelian']} (+{tc['aristotelian']*25}% Scrolls)"
                s_txt = f"Stoic ×{tc['stoic']} (-{min(50, tc['stoic']*5)}% costs)"
                self._t(F_XS, f"{p_txt}  ·  {a_txt}  ·  {s_txt}", (90, 60, 10), x + 8, py + 12)
                py += sum_h + 5

        # ── L2/L3/L4 conversions ──────────────────────────────────────────────
        conv_data = [
            (pl[1], zg.l1, zg.l2, "zone_conv_l2", zg.l2_rate, "l1"),
            (pl[2], zg.l2, zg.l3, "zone_conv_l3", zg.l3_rate, "l2"),
            (pl[3], zg.l3, zg.l4, "zone_conv_l4", zg.l4_rate, "l3"),
        ]
        for layer, from_val, to_val, kind, rate, from_lbl in conv_data:
            ph = 58
            col = layer["color"]
            can = from_val >= rate
            pr = pygame.Rect(x, py, w, ph)
            self._r((220, 240, 235) if can else (215, 210, 200), pr, radius=6,
                    border=1, bc=col)
            self._t(F_MD, layer["name"], col, x+10, py+6)
            self._t(F_SM, f"Spend {rate} {from_lbl.upper()} → 1 {layer['name']}  ·  {layer['desc']}",
                    (80,80,80), x+140, py+10)
            pct = min(1.0, from_val / max(1, rate))
            pygame.draw.rect(self.screen, (175,168,155), (x+10, py+40, 160, 5), border_radius=2)
            pygame.draw.rect(self.screen, col, (x+10, py+40, int(160*pct), 5), border_radius=2)
            self._t(F_XS, f"Have: {from_val}  Owned: {to_val}", (60,60,60), x+10, py+24)
            cbtn = pygame.Rect(x + w - 150, py + (ph-30)//2, 142, 30)
            self._r(col if can else GRAY, cbtn, radius=5)
            self._tc(F_XS, f"Convert ({rate})", WHITE, cbtn)
            self._buy_items.append((cbtn, zid, kind))
            py += ph + 5

    # ── Inspection overlay ────────────────────────────────────────────────────

    def _draw_inspection_overlay(self):
        import math as _m
        g = self.game
        if not g._inspection_active:
            return

        x, y0, w, h = self._right_area()
        # Semi-transparent dark overlay
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((10, 10, 30, 210))
        self.screen.blit(overlay, (x, y0))

        cx = x + w // 2
        cy = y0 + h // 2

        # Pulsing title
        pulse = int(200 + 55 * abs(_m.sin(pygame.time.get_ticks() / 300)))
        title_col = (pulse, int(pulse * 0.4), 40)
        title_surf = F_LG.render("SCHOOL INSPECTION!", True, title_col)
        self.screen.blit(title_surf, (cx - title_surf.get_width() // 2, cy - 110))

        sub_surf = F_SM.render("Click the button as fast as you can!", True, (220, 210, 180))
        self.screen.blit(sub_surf, (cx - sub_surf.get_width() // 2, cy - 78))

        # Progress bar
        prog = g._inspection_clicks / max(1, g._inspection_target)
        bar_w = 240
        bar_h = 18
        pygame.draw.rect(self.screen, (60, 55, 80),
                         (cx - bar_w // 2, cy - 52, bar_w, bar_h), border_radius=4)
        fill_w = int(bar_w * min(1.0, prog))
        if fill_w > 0:
            pygame.draw.rect(self.screen, (80, 200, 100),
                             (cx - bar_w // 2, cy - 52, fill_w, bar_h), border_radius=4)
        prog_txt = f"{g._inspection_clicks} / {g._inspection_target} clicks"
        pt = F_SM.render(prog_txt, True, WHITE)
        self.screen.blit(pt, (cx - pt.get_width() // 2, cy - 30))

        # Timer
        t_col = (255, 120, 60) if g._inspection_timer < 5 else (220, 210, 180)
        t_surf = F_MD.render(f"{g._inspection_timer:.1f}s remaining", True, t_col)
        self.screen.blit(t_surf, (cx - t_surf.get_width() // 2, cy - 4))

        # Big CLICK button
        click_btn = pygame.Rect(cx - 70, cy + 24, 140, 52)
        btn_pulse  = int(160 + 80 * abs(_m.sin(pygame.time.get_ticks() / 200)))
        self._r((btn_pulse, 50, 50), click_btn, radius=10)
        self._tc(F_LG, "CLICK!", WHITE, click_btn)
        self._buy_items.append((click_btn, None, "inspection_click"))

    # ── Quiz overlay ──────────────────────────────────────────────────────────

    def _draw_quiz_overlay(self):
        import math as _m
        g = self.game
        if not g._quiz_active and not g._quiz_showing_reward:
            return

        x, y0, w, h = self._right_area()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((10, 20, 50, 220))
        self.screen.blit(overlay, (x, y0))
        cx2 = x + w // 2

        if g._quiz_showing_reward:
            # ── Reward selection screen ─────────────────────────────
            title = F_LG.render("Choose Your Reward!", True, (255, 230, 80))
            self.screen.blit(title, (cx2 - title.get_width() // 2, y0 + 20))

            opt_w, opt_h, opt_g = 180, 120, 20
            n = len(g._quiz_reward_options)
            total_w = n * opt_w + (n - 1) * opt_g
            ox0 = cx2 - total_w // 2

            for i, tier in enumerate(g._quiz_reward_options):
                rw  = QUIZ_REWARDS[tier]
                ox  = ox0 + i * (opt_w + opt_g)
                oy  = y0 + 80
                col = rw["color"]
                self._r(col, pygame.Rect(ox, oy, opt_w, opt_h), radius=10,
                        border=2, bc=tuple(min(255, c + 60) for c in col))
                name_s = F_MD.render(rw["name"], True, WHITE)
                self.screen.blit(name_s, (ox + opt_w // 2 - name_s.get_width() // 2, oy + 10))
                # Wrap description
                desc = rw["desc"]
                lines = []
                while len(desc) > 22:
                    cut = desc[:22].rfind(' ')
                    if cut < 0: cut = 22
                    lines.append(desc[:cut])
                    desc = desc[cut:].strip()
                lines.append(desc)
                for li, ln in enumerate(lines):
                    ds = F_XS.render(ln, True, (240, 240, 240))
                    self.screen.blit(ds, (ox + opt_w // 2 - ds.get_width() // 2, oy + 44 + li * 16))
                btn = pygame.Rect(ox + 20, oy + opt_h - 30, opt_w - 40, 24)
                self._r((255, 255, 255, 60), btn, radius=6)
                self._tc(F_XS, "CLAIM", WHITE, btn)
                self._buy_items.append((btn, tier, "quiz_reward"))

        else:
            # ── Question screen ──────────────────────────────────────
            qi = g._quiz_idx
            q  = g._quiz_questions[qi]
            type_labels = {"math": "Math", "spelling": "Spelling", "history": "History"}
            type_col    = {"math": (80, 180, 255), "spelling": (80, 220, 120), "history": (255, 180, 60)}

            prog_str = f"Question {qi + 1} of {len(g._quiz_questions)}"
            ps = F_SM.render(prog_str, True, (180, 180, 200))
            self.screen.blit(ps, (cx2 - ps.get_width() // 2, y0 + 16))

            type_s = F_SM.render(f"[ {type_labels.get(q['type'], q['type'])} ]",
                                 True, type_col.get(q["type"], WHITE))
            self.screen.blit(type_s, (cx2 - type_s.get_width() // 2, y0 + 38))

            # Word-wrap question text
            qtext = q["q"]
            q_lines = []
            while len(qtext) > 36:
                cut = qtext[:36].rfind(' ')
                if cut < 0: cut = 36
                q_lines.append(qtext[:cut])
                qtext = qtext[cut:].strip()
            q_lines.append(qtext)
            for li, ln in enumerate(q_lines):
                qs = F_MD.render(ln, True, (255, 255, 200))
                self.screen.blit(qs, (cx2 - qs.get_width() // 2, y0 + 70 + li * 28))

            # Answer buttons (2×2 grid)
            choices = q["choices"]
            btn_w, btn_h, btn_g = 200, 40, 10
            cols_x = [cx2 - btn_w - btn_g // 2, cx2 + btn_g // 2]
            rows_y = [y0 + 160, y0 + 220]
            ans_colors = [(60, 80, 160), (60, 130, 60), (140, 60, 60), (100, 80, 20)]
            for i, choice in enumerate(choices[:4]):
                bx2 = cols_x[i % 2]
                by2 = rows_y[i // 2]
                bcol = ans_colors[i]
                btn  = pygame.Rect(bx2, by2, btn_w, btn_h)
                self._r(bcol, btn, radius=8)
                cs   = F_SM.render(choice, True, WHITE)
                self.screen.blit(cs, (bx2 + btn_w // 2 - cs.get_width() // 2,
                                      by2 + btn_h // 2 - cs.get_height() // 2))
                self._buy_items.append((btn, choice, "quiz_answer"))

    # ── Milestone flash ───────────────────────────────────────────────────────

    def _draw_milestone_flash(self, dt: float):
        import math as _m
        mf = self.milestone_flash
        if not mf:
            return
        alpha = int(255 * (mf["timer"] / 2.5))
        scale = 1.0 + 0.1 * _m.sin(mf["timer"] * 6)
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, max(0, min(120, alpha // 2))))
        self.screen.blit(dim, (0, 0))
        size  = int(48 * scale)
        font  = pygame.font.SysFont("DejaVu Sans", size, bold=True)
        surf1 = font.render(mf["text"], True, GOLD)
        surf1.set_alpha(alpha)
        surf2 = font.render(mf["text"], True, WHITE)
        surf2.set_alpha(alpha // 3)
        cx2   = W // 2 - surf1.get_width() // 2
        cy2   = H // 2 - surf1.get_height() // 2
        self.screen.blit(surf2, (cx2 + 2, cy2 + 2))
        self.screen.blit(surf1, (cx2, cy2))
        mf["timer"] -= dt
        if mf["timer"] <= 0:
            self.milestone_flash = None

    def _draw_event_banner(self):
        import math as _m
        ev = self.game.pending_event
        if not ev:
            self._event_btn = None
            return
        pulse = int(215 + 40 * _m.sin(pygame.time.get_ticks() / 250))
        bw = W - LEFT_W - 10
        bh = 52
        bx = LEFT_W + 5
        by = CONTENT_Y + 4
        # Rare events get a different color
        is_rare = ev.get("rarity") == "rare"
        surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        if is_rare:
            surf.fill((140, 40, 140, pulse))
        else:
            surf.fill((38, 140, 68, pulse))
        self.screen.blit(surf, (bx, by))
        border_col = (255, 180, 60) if is_rare else GOLD
        pygame.draw.rect(self.screen, border_col, (bx, by, bw, bh), 2, border_radius=6)
        prefix = "RARE EVENT: " if is_rare else "EVENT: "
        self._t(F_LG, f"{prefix}{ev['name']}", border_col, bx+12, by+6)
        self._t(F_SM, f"{ev['desc']}   (click to collect!)", WHITE, bx+12, by+30)
        self._event_btn = pygame.Rect(bx, by, bw, bh)

    def _draw_story_popup(self) -> list[tuple]:
        g = self.game
        if not g.story_queue:
            return []
        cid = g.story_queue[0]
        ch  = next((c for c in STORY if c["id"] == cid), None)
        if not ch:
            g.story_queue.pop(0)
            return []
        pw, ph = 560, 310
        px = (W - pw) // 2
        py = (H - ph) // 2
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 160))
        self.screen.blit(dim, (0, 0))
        self._r((248, 244, 232), pygame.Rect(px, py, pw, ph), radius=10, border=2, bc=(100,90,70))
        self._r((60, 50, 35), pygame.Rect(px, py, pw, 44), radius=10)
        self._t(F_LG, ch["title"], GOLD, px+16, py+10)
        lines = ch["text"].split("\n")
        ty = py + 56
        for line in lines:
            self._t(F_MD if line else F_SM, line, DARK, px+16, ty)
            ty += 22 if line else 10
        ok = pygame.Rect(px + pw//2 - 70, py + ph - 52, 140, 38)
        self._r(ACCENT, ok, radius=7)
        self._tc(F_MD, "Continue", WHITE, ok)
        return [(ok, "story_ok")]

    def _draw_ticker(self, dt: float):
        ty = H - TICKER_H
        self._r(TICKER_BG, pygame.Rect(0, ty, W, TICKER_H))
        lab = F_SM.render("NEWS:", True, GOLD)
        self.screen.blit(lab, (8, ty + (TICKER_H - lab.get_height())//2))

        if self._ticker_dynamic:
            msg   = self._ticker_dynamic
            color = GOLD
        else:
            msg   = NEWS[self.tick_idx]
            color = (210, 225, 245)

        surf = F_SM.render(msg, True, color)
        pygame.draw.rect(self.screen, TICKER_BG, pygame.Rect(70, ty, W-70, TICKER_H))
        self._clip(pygame.Rect(70, ty, W-70, TICKER_H))
        self.screen.blit(surf, (int(self.tick_x), ty + (TICKER_H - surf.get_height())//2))
        self._unclip()
        self.tick_x -= self.tick_spd * dt
        if self.tick_x < -(surf.get_width() + 20):
            self._ticker_dynamic = None
            if self.game.dynamic_news_queue:
                self._ticker_dynamic = self.game.dynamic_news_queue.pop(0)
            else:
                self.tick_idx = (self.tick_idx + 1) % len(NEWS)
            self.tick_x = float(W)

    def _draw_toast(self):
        g = self.game
        if g.ach_toast_timer <= 0 or not g.new_achievements:
            return
        aid = g.new_achievements[-1]
        a   = next((x for x in ACHIEVEMENTS if x.id == aid), None)
        if not a:
            return
        alpha = min(255, int(g.ach_toast_timer * 128))
        tw, th = 400, 58
        tx = W - tw - 12
        tt = H - TICKER_H - th - 12
        toast = pygame.Surface((tw, th), pygame.SRCALPHA)
        toast.fill((30, 30, 30, 200))
        pygame.draw.rect(toast, GRADE_COL.get(a.grade, GRAY), (0, 0, tw, th), 3, border_radius=8)
        f1 = F_MD.render(f"Achievement! {a.name}  [{a.grade}]", True, WHITE)
        f2 = F_SM.render(a.desc, True, (200,200,200))
        toast.blit(f1, (10, 8))
        toast.blit(f2, (10, 32))
        toast.set_alpha(alpha)
        self.screen.blit(toast, (tx, tt))

    def _draw_inspector_banner(self):
        insp = self.game.inspector
        if not insp:
            return
        x  = LEFT_W + 5
        w  = W - LEFT_W - 10
        y0 = CONTENT_Y
        bh = 72
        result = insp.get("result")
        if result == "success":
            bg = (38, 140, 60); border = (20, 200, 80); msg = "✓ PASSED!  Merit Points awarded!"
        elif result == "fail":
            bg = (140, 38, 38); border = (220, 60, 60); msg = "✗ FAILED  −10% KPS for 2 minutes"
        else:
            bg = (28, 52, 102); border = (80, 130, 220); msg = ""

        banner = pygame.Surface((w, bh), pygame.SRCALPHA)
        banner.fill((*bg, 235))
        pygame.draw.rect(banner, border, (0, 0, w, bh), 2, border_radius=6)
        self.screen.blit(banner, (x, y0))

        if result:
            ts = F_LG.render(msg, True, WHITE)
            self.screen.blit(ts, (x + w//2 - ts.get_width()//2, y0 + bh//2 - ts.get_height()//2))
        else:
            self._t(F_MD, "📋 School Inspector!", WHITE, x + 10, y0 + 6)
            self._t(F_SM, f"Generate {fmt(insp['target_kp'])} KP in {int(insp['timer'])}s",
                    (200, 220, 255), x + 10, y0 + 30)
            pct = min(1.0, insp["earned"] / max(1, insp["target_kp"]))
            pygame.draw.rect(self.screen, (40, 60, 110), (x + 10, y0 + 52, w - 120, 12), border_radius=5)
            pygame.draw.rect(self.screen, (80, 200, 120), (x + 10, y0 + 52, int((w-120)*pct), 12), border_radius=5)
            pct_txt = F_SM.render(f"{pct*100:.0f}%", True, WHITE)
            self.screen.blit(pct_txt, (x + w - 108, y0 + 50))
            # Timer arc / colour
            t_col = (255, 80, 80) if insp["timer"] < 15 else (255, 200, 80) if insp["timer"] < 30 else WHITE
            self._t(F_LG, f"{int(insp['timer'])}s", t_col, x + w - 68, y0 + 16)

    def _instructor_zone(self) -> int:
        if self.tab == "Worlds" and self.worlds_sel_zone != 1:
            return self.worlds_sel_zone
        return 1

    def _draw_instructor(self, cx: int, cy: int, zone_id: int):
        s  = self.screen
        PI = 3.14159
        SKIN = (232, 198, 162)

        _zones: dict = {
            1: {"body": (38,  52,  95),  "leg": (28,  38,  68),  "hair": (80,  55,  30),  "eye": (40,  25,  10)},
            2: {"body": (130, 105, 60),  "leg": (100, 80,  45),  "hair": (80,  55,  30),  "eye": (40,  25,  10)},
            3: {"body": (160, 175, 190), "leg": (130, 145, 160), "hair": None,             "eye": (80,  180, 240)},
            4: {"body": (230, 220, 200), "leg": (200, 190, 170), "hair": (185, 165, 125),  "eye": (40,  25,  10)},
            5: {"body": (235, 238, 245), "leg": (215, 218, 225), "hair": None,             "eye": (50,  120, 200)},
            6: {"body": (100, 30,  160), "leg": (70,  20,  120), "hair": (220, 210, 185),  "eye": (180, 50,  220)},
            7: {"body": (130, 90,  50),  "leg": (100, 68,  38),  "hair": (60,  40,  20),   "eye": (50,  30,  10)},
            8: {"body": (240, 245, 255), "leg": (220, 228, 245), "hair": (255, 240, 160),  "eye": (100, 160, 255)},
            9: {"body": (55,  10,  10),  "leg": (35,  5,   5),   "hair": (25,  20,  20),   "eye": (255, 40,  40)},
           10: {"body": (40,  80, 200),  "leg": (30,  60, 160),  "hair": (50,  40,  30),   "eye": (50,  200, 255)},
        }
        c        = _zones.get(zone_id, _zones[1])
        body_col = c["body"]
        leg_col  = c["leg"]
        hair_col = c["hair"]
        eye_col  = c["eye"]

        # body/gown
        pygame.draw.rect(s, body_col, (cx - 14, cy - 22, 28, 40), border_radius=4)

        # collar (zone-specific)
        if zone_id == 1:
            pygame.draw.polygon(s, (210, 200, 185),
                                [(cx, cy - 20), (cx - 6, cy - 12), (cx + 6, cy - 12)])
        elif zone_id == 4:   # toga drape
            pygame.draw.polygon(s, (220, 210, 195),
                                [(cx, cy - 22), (cx - 10, cy - 8), (cx + 10, cy - 8)])
        elif zone_id == 6:   # purple robe V-neck
            pygame.draw.polygon(s, (160, 100, 200),
                                [(cx, cy - 20), (cx - 7, cy - 10), (cx + 7, cy - 10)])
        elif zone_id == 7:   # fur collar
            pygame.draw.polygon(s, (160, 115, 65),
                                [(cx, cy - 20), (cx - 6, cy - 12), (cx + 6, cy - 12)])
        elif zone_id == 8:   # white robe V-neck
            pygame.draw.polygon(s, (210, 215, 240),
                                [(cx, cy - 20), (cx - 7, cy - 10), (cx + 7, cy - 10)])
        elif zone_id == 10:  # hero emblem (gold "H" on chest)
            gold = (255, 215, 40)
            pygame.draw.line(s, gold, (cx - 5, cy - 16), (cx - 5, cy - 6), 2)
            pygame.draw.line(s, gold, (cx + 5, cy - 16), (cx + 5, cy - 6), 2)
            pygame.draw.line(s, gold, (cx - 5, cy - 11), (cx + 5, cy - 11), 2)

        # zone 8: wing nubs (draw before arms so arms render on top)
        if zone_id == 8:
            pygame.draw.arc(s, (200, 210, 240), (cx - 28, cy - 18, 18, 22), PI * 0.15, PI * 0.85, 4)
            pygame.draw.arc(s, (200, 210, 240), (cx + 10, cy - 18, 18, 22), PI * 0.15, PI * 0.85, 4)

        # zone 10: billowing cape (draw behind arms)
        if zone_id == 10:
            cape_pts = [(cx - 14, cy - 20), (cx + 14, cy - 20),
                        (cx + 22, cy + 30), (cx,       cy + 42), (cx - 22, cy + 30)]
            pygame.draw.polygon(s, (200, 30, 30), cape_pts)

        # arms
        pygame.draw.line(s, body_col, (cx - 14, cy - 12), (cx - 24, cy + 10), 5)
        pygame.draw.line(s, body_col, (cx + 14, cy - 12), (cx + 24, cy + 10), 5)

        # zone 4: scroll held in right hand
        if zone_id == 4:
            pygame.draw.rect(s, (235, 225, 195), (cx + 20, cy - 8, 8, 14), border_radius=1)
            pygame.draw.rect(s, (180, 160, 120), (cx + 20, cy - 8,  8, 3))
            pygame.draw.rect(s, (180, 160, 120), (cx + 20, cy + 3,  8, 3))

        # legs
        pygame.draw.rect(s, leg_col, (cx - 11, cy + 18, 9, 24))
        pygame.draw.rect(s, leg_col, (cx + 2,  cy + 18, 9, 24))

        # shoes
        if zone_id == 5:
            shoe = (200, 205, 215)   # white moon boots
        elif zone_id == 7:
            shoe = (160, 120, 70)    # bare leather
        elif zone_id == 8:
            shoe = (220, 225, 240)   # angelic sandals
        elif zone_id == 10:
            shoe = (180, 20,  20)    # red hero boots
        else:
            shoe = (15, 15, 15)
        pygame.draw.ellipse(s, shoe, (cx - 14, cy + 40, 13, 6))
        pygame.draw.ellipse(s, shoe, (cx + 1,  cy + 40, 13, 6))

        # head
        head_col = SKIN
        if zone_id == 3:
            head_col = (210, 230, 250)   # inside futuristic helmet
        elif zone_id == 5:
            head_col = (225, 205, 178)   # inside spacesuit bubble
        pygame.draw.circle(s, head_col, (cx, cy - 40), 15)

        # hair
        if hair_col:
            if zone_id == 7:   # messy prehistoric
                pygame.draw.arc(s, hair_col, (cx - 17, cy - 58, 34, 25), 0, PI, 6)
                pygame.draw.line(s, hair_col, (cx - 15, cy - 53), (cx - 20, cy - 44), 3)
                pygame.draw.line(s, hair_col, (cx + 15, cy - 53), (cx + 20, cy - 44), 3)
            else:
                pygame.draw.arc(s, hair_col, (cx - 15, cy - 56, 30, 22), 0, PI, 5)

        # eyes / face features
        if zone_id == 1:   # glasses
            pygame.draw.circle(s, (65, 45, 20), (cx - 6, cy - 41), 5, 1)
            pygame.draw.circle(s, (65, 45, 20), (cx + 6, cy - 41), 5, 1)
            pygame.draw.line(s,   (65, 45, 20), (cx - 1,  cy - 41), (cx + 1,  cy - 41), 1)
            pygame.draw.line(s,   (65, 45, 20), (cx - 11, cy - 41), (cx - 14, cy - 39), 1)
            pygame.draw.line(s,   (65, 45, 20), (cx + 11, cy - 41), (cx + 14, cy - 39), 1)
            pygame.draw.circle(s, eye_col, (cx - 6, cy - 41), 2)
            pygame.draw.circle(s, eye_col, (cx + 6, cy - 41), 2)
        elif zone_id == 3:   # sci-fi visor bar
            pygame.draw.line(s, (80, 200, 240), (cx - 10, cy - 41), (cx + 10, cy - 41), 3)
            pygame.draw.circle(s, eye_col, (cx - 5, cy - 41), 2)
            pygame.draw.circle(s, eye_col, (cx + 5, cy - 41), 2)
        elif zone_id == 9:   # glowing red eyes
            pygame.draw.circle(s, (180, 0,   0), (cx - 6, cy - 41), 4)
            pygame.draw.circle(s, (180, 0,   0), (cx + 6, cy - 41), 4)
            pygame.draw.circle(s, eye_col,       (cx - 6, cy - 41), 2)
            pygame.draw.circle(s, eye_col,       (cx + 6, cy - 41), 2)
        elif zone_id == 10:  # hero domino mask + glowing eyes
            pygame.draw.ellipse(s, (20, 20, 20), (cx - 12, cy - 44, 10, 7))
            pygame.draw.ellipse(s, (20, 20, 20), (cx + 2,  cy - 44, 10, 7))
            pygame.draw.circle(s, eye_col, (cx - 7, cy - 41), 2)
            pygame.draw.circle(s, eye_col, (cx + 7, cy - 41), 2)
        else:
            pygame.draw.circle(s, eye_col, (cx - 6, cy - 41), 2)
            pygame.draw.circle(s, eye_col, (cx + 6, cy - 41), 2)

        # smile
        pygame.draw.arc(s, (155, 75, 55), (cx - 5, cy - 33, 10, 7), PI, 0, 2)

        # head accessories
        if zone_id == 1:   # graduation cap
            pygame.draw.rect(s,   (18, 18, 28),   (cx - 18, cy - 60, 36, 5))
            pygame.draw.rect(s,   (18, 18, 28),   (cx - 13, cy - 72, 26, 14))
            pygame.draw.line(s,   (205, 165, 30), (cx + 9,  cy - 60), (cx + 16, cy - 46), 2)
            pygame.draw.circle(s, (205, 165, 30), (cx + 16, cy - 46), 3)

        elif zone_id == 2:   # orange hard hat
            pygame.draw.ellipse(s, (220, 130, 30), (cx - 16, cy - 63, 32, 24))
            pygame.draw.rect(s,   (220, 130, 30), (cx - 19, cy - 52, 38, 6), border_radius=2)

        elif zone_id == 3:   # sci-fi dome helmet outline
            pygame.draw.circle(s, (100, 185, 235), (cx, cy - 40), 21, 2)
            pygame.draw.arc(s,   (200, 240, 255),  (cx - 11, cy - 56, 12, 12), 0.5, 1.8, 2)

        elif zone_id == 4:   # laurel wreath
            pygame.draw.arc(s,   (60, 145, 60), (cx - 17, cy - 58, 20, 18), 0.4, PI, 3)
            pygame.draw.arc(s,   (60, 145, 60), (cx - 3,  cy - 58, 20, 18), 0.0, 2.7, 3)
            pygame.draw.circle(s, (175, 45, 45), (cx,     cy - 57), 3)
            pygame.draw.circle(s, (175, 45, 45), (cx - 7, cy - 55), 2)
            pygame.draw.circle(s, (175, 45, 45), (cx + 7, cy - 55), 2)

        elif zone_id == 5:   # bubble helmet
            pygame.draw.circle(s, (190, 210, 225), (cx, cy - 40), 22, 3)
            pygame.draw.arc(s,   (225, 245, 255),  (cx - 14, cy - 56, 14, 14), 0.6, 1.9, 2)
            pygame.draw.arc(s,   (170, 180, 195),  (cx - 5,  cy - 28, 18, 18), PI, PI * 1.5, 3)

        elif zone_id == 6:   # tall wizard hat + sparkles
            pygame.draw.polygon(s, (75, 15, 125),
                                [(cx, cy - 90), (cx - 13, cy - 57), (cx + 13, cy - 57)])
            pygame.draw.rect(s,   (85, 20, 140), (cx - 17, cy - 60, 34, 5), border_radius=2)
            pygame.draw.circle(s, (255, 215, 40), (cx,      cy - 78), 3)
            pygame.draw.circle(s, (210, 170, 255), (cx - 23, cy - 32), 2)
            pygame.draw.circle(s, (190, 145, 250), (cx + 23, cy - 26), 2)

        elif zone_id == 7:   # bone hair-pin + tooth necklace
            pygame.draw.rect(s,   (230, 220, 195), (cx - 6,  cy - 62, 12, 4), border_radius=2)
            pygame.draw.circle(s, (230, 220, 195), (cx - 6,  cy - 60), 3)
            pygame.draw.circle(s, (230, 220, 195), (cx + 6,  cy - 60), 3)
            pygame.draw.arc(s,   (200, 178, 135),  (cx - 10, cy - 26, 20, 12), PI, 0, 2)

        elif zone_id == 8:   # golden halo
            pygame.draw.ellipse(s, (255, 215, 35), (cx - 13, cy - 64, 26, 9), 3)

        elif zone_id == 9:   # small horns + dark flame wisps
            pygame.draw.polygon(s, (140, 15, 15),
                                [(cx - 8, cy - 54), (cx - 5, cy - 67), (cx - 2, cy - 54)])
            pygame.draw.polygon(s, (140, 15, 15),
                                [(cx + 2, cy - 54), (cx + 5, cy - 67), (cx + 8, cy - 54)])
            pygame.draw.arc(s,   (90,  10, 160),  (cx - 19, cy + 12, 12, 18), PI, 0, 2)
            pygame.draw.arc(s,   (110, 15, 180),  (cx + 5,  cy + 16, 12, 14), PI, 0, 2)

        elif zone_id == 10:  # hero fin-cowl + star on forehead
            # Fin on top of head
            pygame.draw.polygon(s, (30, 60, 160),
                                [(cx, cy - 70), (cx - 6, cy - 54), (cx + 6, cy - 54)])
            # Gold star on forehead
            pygame.draw.circle(s, (255, 215, 40), (cx, cy - 48), 3)

    def _draw_headmaster(self, dt: float):
        if not self.game.show_headmaster:
            self._hm_x = float(W + 10)
            self._hm_show_tab = self.tab
            return
        # Trigger: slide in on tab switch, out after 5 s
        if self.tab != self._hm_show_tab:
            self._hm_show_tab = self.tab
            self._hm_x        = float(W + 10)
            self._hm_timer    = 0.0
        self._hm_timer += dt

        target_x = float(W - 72) if self._hm_timer < 5.5 else float(W + 10)
        self._hm_x += (target_x - self._hm_x) * min(1.0, dt * 8)
        if self._hm_x > W - 4:
            return

        cx = int(self._hm_x) + 34
        cy = H - TICKER_H - 128

        # ── Speech bubble ──────────────────────────────────────────────────────
        hint  = TAB_HINTS.get(self._hm_show_tab, "")
        raw   = hint.split("\n") if hint else []
        # word-wrap each paragraph to fit bubble interior
        def _ww(text, max_w):
            words, lines, cur = text.split(), [], ""
            for w in words:
                test = (cur + " " + w).strip()
                if F_SM.size(test)[0] <= max_w:
                    cur = test
                else:
                    if cur: lines.append(cur)
                    cur = w
            if cur: lines.append(cur)
            return lines
        bw    = 255
        lines = []
        for para in raw:
            lines.extend(_ww(para, bw - 22))
        lh    = 17
        bh    = len(lines) * lh + 20
        bx    = cx - 26 - bw
        by    = cy - bh // 2 - 10

        fade = min(1.0, (W - 4 - self._hm_x) / 40.0)
        alpha = int(fade * 220)

        if lines and alpha > 0:
            bsurf = pygame.Surface((bw, bh), pygame.SRCALPHA)
            bsurf.fill((252, 248, 236, alpha))
            pygame.draw.rect(bsurf, (160, 140, 100, alpha), (0, 0, bw, bh), 2, border_radius=10)
            for i, line in enumerate(lines):
                col = (50, 35, 15)
                ts  = F_SM.render(line, True, col)
                ts.set_alpha(int(fade * 255))
                bsurf.blit(ts, (10, 8 + i * lh))
            self.screen.blit(bsurf, (bx, by))
            # pointer triangle toward character
            px = bx + bw
            py_tip = by + bh // 2
            pts = [(px, py_tip - 7), (px, py_tip + 7), (px + 12, py_tip)]
            pygame.draw.polygon(self.screen, (252, 248, 236), pts)
            pygame.draw.lines(self.screen, (160, 140, 100), False,
                              [(px, py_tip - 7), (px + 12, py_tip), (px, py_tip + 7)], 2)

        # ── Character ──────────────────────────────────────────────────────────
        self._draw_instructor(cx, cy, self._instructor_zone())

    def _draw_tooltip(self):
        if not self.tooltip:
            return
        pos, lines = self.tooltip
        pad = 8
        lh  = 18
        tw  = max(F_SM.size(l)[0] for l in lines) + pad*2
        th  = len(lines) * lh + pad*2
        tx  = min(pos[0] + 14, W - tw - 4)
        ty  = min(pos[1] + 14, H - TICKER_H - th - 4)
        bg  = pygame.Surface((tw, th), pygame.SRCALPHA)
        bg.fill((28, 28, 28, 215))
        self.screen.blit(bg, (tx, ty))
        pygame.draw.rect(self.screen, (120,120,120), (tx, ty, tw, th), 1, border_radius=4)
        for i, line in enumerate(lines):
            self._t(F_SM, line, WHITE, tx+pad, ty+pad+i*lh)

    def _draw_popup(self) -> list[tuple]:
        if not self.popup:
            return []
        pw, ph = 480, 240
        px = (W - pw) // 2
        py = (H - ph) // 2
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 140))
        self.screen.blit(dim, (0, 0))
        self._r((245, 242, 235), pygame.Rect(px, py, pw, ph), radius=12, border=2, bc=(100,95,85))
        popup_btns = []
        ptype = self.popup["type"]
        if ptype == "offline":
            g = self.game
            self._t(F_LG, "Welcome back!", DARK, px+20, py+18)
            self._t(F_MD, f"You were away for {g.offline_hours:.1f} hours.", (80,80,80), px+20, py+56)
            self._t(F_LG, f"+{fmt(g.offline_kp_gained)} KP earned offline.", GREEN, px+20, py+92)
            self._t(F_SM, "(50%+ efficiency while away)", (120,120,120), px+20, py+126)
            ok_btn = pygame.Rect(px + pw//2 - 80, py + ph - 56, 160, 40)
            self._r(ACCENT, ok_btn, radius=8)
            self._tc(F_MD, "Collect!", WHITE, ok_btn)
            popup_btns.append((ok_btn, "close_popup"))
        elif ptype == "prestige_confirm":
            g = self.game
            d = g.diplomas_on_prestige
            self._t(F_LG, "Graduate?", PRESTIGE, px+20, py+18)
            self._t(F_MD, f"You will earn  {d} Diploma{'s' if d!=1 else ''}.", GOLD, px+20, py+56)
            self._t(F_SM, "Each diploma grants +2% global KPS (stacks).", (80,80,80), px+20, py+88)
            self._t(F_SM, "Requires 2 Million KP. Resets: KP, buildings, upgrades.", (160,80,80), px+20, py+116)
            self._t(F_SM, "Keeps: diplomas, honors, skills, achievements.", (60,140,60), px+20, py+140)
            yes = pygame.Rect(px + 40, py + ph - 58, 160, 42)
            no  = pygame.Rect(px + pw - 200, py + ph - 58, 160, 42)
            self._r(PRESTIGE, yes, radius=8)
            self._tc(F_LG, "Graduate!", WHITE, yes)
            self._r((140,140,140), no, radius=8)
            self._tc(F_MD, "Cancel", WHITE, no)
            popup_btns.append((yes, "prestige_confirm"))
            popup_btns.append((no,  "close_popup"))
        return popup_btns

    # ── Main draw ─────────────────────────────────────────────────────────────

    def _draw(self, dt: float):
        self.tooltip    = None
        self._buy_items = []
        self.screen.fill(BG)

        self._draw_topbar()
        self._draw_tabs()
        self._draw_left()
        self.sprites.draw_left(self.screen)

        self._r(CREAM, pygame.Rect(LEFT_W, CONTENT_Y, W - LEFT_W, H - CONTENT_Y - TICKER_H))

        match self.tab:
            case "Buildings":   self._draw_buildings()
            case "Upgrades":    self._draw_upgrades()
            case "Curriculum":  self._draw_curriculum()
            case "Report Card": self._draw_reportcard()
            case "Campus":      self._draw_campus_tab()
            case "Prestige":    self._draw_prestige_shop()
            case "Legacy":      self._draw_legacy()
            case "Worlds":      self._draw_worlds()
            case "Settings":    self._draw_settings()

        self.sprites.draw_right(self.screen, self.tab)
        self._draw_inspector_banner()
        self._draw_event_banner()
        self._draw_inspection_overlay()
        self._draw_quiz_overlay()
        self._draw_toast()
        self._draw_ticker(dt)
        popup_btns  = self._draw_popup()
        story_btns  = self._draw_story_popup()
        self._draw_tooltip()

        if self.game.milestone_queue and not self.milestone_flash:
            self.milestone_flash = {"text": self.game.milestone_queue.pop(0), "timer": 2.5}
            audio.play("milestone")

        self._draw_milestone_flash(dt)
        self._draw_headmaster(dt)

        pygame.display.flip()
        return popup_btns, story_btns

    # ── Scrolling ─────────────────────────────────────────────────────────────

    def _scroll(self, direction: int):
        delta = -45 if direction < 0 else 45
        match self.tab:
            case "Buildings":   self.b_scroll   = max(0, self.b_scroll   + delta)
            case "Upgrades":    self.u_scroll   = max(0, self.u_scroll   + delta)
            case "Curriculum":  self.sk_scroll  = max(0, self.sk_scroll  + delta)
            case "Report Card": self.ac_scroll  = max(0, self.ac_scroll  + delta)
            case "Legacy":
                if self.lg_subtab == "Honors":
                    self.lg_scroll_h = max(0, self.lg_scroll_h + delta)
                elif self.lg_subtab == "Scholars":
                    self.lg_scroll_s = max(0, self.lg_scroll_s + delta)
                elif self.lg_subtab == "Alumni":
                    self.lg_scroll_a = max(0, self.lg_scroll_a + delta)
                else:
                    self.lg_scroll_e = max(0, self.lg_scroll_e + delta)
            case "Prestige":    self.ps_scroll      = max(0, self.ps_scroll      + delta)
            case "Worlds":
                if self.worlds_subtab == "Buildings":
                    self.worlds_b_scroll = max(0, self.worlds_b_scroll + delta)
                elif self.worlds_subtab == "Upgrades":
                    self.worlds_u_scroll = max(0, self.worlds_u_scroll + delta)

    # ── Events ────────────────────────────────────────────────────────────────

    def _handle_events(self, popup_btns: list, story_btns: list):
        g  = self.game
        mx, my = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                g.save()
                self.world.save()
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN:
                if self._name_input_active:
                    if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        name = self._name_input_text.strip()
                        g.school_name = name if name else "Edu Empire Academy"
                        self._name_input_active = False
                    elif ev.key == pygame.K_ESCAPE:
                        self._name_input_active = False
                    elif ev.key == pygame.K_BACKSPACE:
                        self._name_input_text = self._name_input_text[:-1]
                    elif ev.unicode and len(self._name_input_text) < 40:
                        self._name_input_text += ev.unicode
                    continue
                if ev.key == pygame.K_SPACE and not self._name_input_active:
                    gained = g.click()
                    audio.play("click")
                    mx2, my2 = pygame.mouse.get_pos()
                    self.floats.append(Float(mx2 - 30, my2 - 25, f"+{fmt(gained)} KP"))
                if ev.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                              pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8):
                    idx = ev.key - pygame.K_1
                    if 0 <= idx < len(TABS):
                        self.tab = TABS[idx]
                        self._reset_confirm = False
                if ev.key == pygame.K_ESCAPE:
                    if self.popup:
                        self.popup = None
                    elif g.story_queue:
                        g.story_queue.pop(0)
                    else:
                        g.save()
                        self.world.save()
                        pygame.quit()
                        sys.exit()

            if ev.type == pygame.MOUSEBUTTONUP:
                if ev.button == 1:
                    self._mouse_held = False
                    self._hold_acc   = 0.0

            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 4: self._scroll(-1)
                if ev.button == 5: self._scroll(+1)

                if ev.button == 1:
                    if self._study_btn and self._study_btn.collidepoint(mx, my):
                        self._mouse_held = True

                if ev.button == 1:
                    if self._exit_btn and self._exit_btn.collidepoint(mx, my):
                        g.save()
                        self.world.save()
                        pygame.quit()
                        sys.exit()

                    # School name input — activate on click, confirm on click outside
                    if (self._name_input_rect and self.tab == "Settings"
                            and self._name_input_rect.collidepoint(mx, my)):
                        if not self._name_input_active:
                            self._name_input_active = True
                            self._name_input_text   = g.school_name
                    elif self._name_input_active:
                        name = self._name_input_text.strip()
                        g.school_name = name if name else "Edu Empire Academy"
                        self._name_input_active = False

                    if g.story_queue:
                        for btn, action in story_btns:
                            if btn.collidepoint(mx, my) and action == "story_ok":
                                g.story_queue.pop(0)
                        continue

                    if self.popup:
                        for btn, action in popup_btns:
                            if btn.collidepoint(mx, my):
                                if action == "close_popup":
                                    self.popup = None
                                elif action == "prestige_confirm":
                                    g.do_prestige()
                                    audio.play("prestige")
                                    self.popup = None
                        continue

                    for r, name in self._tab_rects:
                        if r.collidepoint(mx, my):
                            self.tab = name
                            self._reset_confirm = False

                    if self._study_btn and self._study_btn.collidepoint(mx, my):
                        gained = g.click()
                        audio.play("click")
                        self.floats.append(Float(mx - 30, my - 25, f"+{fmt(gained)} KP"))

                    if self._grad_btn and self._grad_btn.collidepoint(mx, my):
                        self.popup = {"type": "prestige_confirm"}

                    if self._event_btn and self._event_btn.collidepoint(mx, my):
                        g.collect_event()
                        audio.play("collect")

                    for btn, obj, kind in self._buy_items:
                        if not btn.collidepoint(mx, my):
                            continue
                        if kind == "set_buy_mult":
                            self.buy_mult = obj
                        elif kind == "set_b_filter":
                            self.b_filter = obj
                        elif kind == "building":
                            mult = self.buy_mult
                            if mult == "max":
                                n = g.building_max_buyable(obj)
                            else:
                                n = int(mult)
                            if n > 0 and g.buy_building_n(obj, n):
                                audio.play("buy")
                            else:
                                audio.play("error")
                        elif kind == "upgrade":
                            cost = g.upgrade_cost(obj)
                            if g.kp >= cost and obj not in g.upgrades_purchased:
                                g.buy_upgrade(obj)
                                audio.play("upgrade")
                            else:
                                audio.play("error")
                        elif kind == "skill":
                            sk = next((s for s in SKILLS if s.id == obj), None)
                            if sk and g.merit_points >= sk.cost and obj not in g.skills_purchased:
                                g.buy_skill(obj)
                                audio.play("skill")
                            else:
                                audio.play("error")
                        elif kind == "diploma_upgrade":
                            du = next((d for d in DIPLOMA_UPGRADES if d["id"] == obj), None)
                            if du and g.diplomas >= du["cost"] and obj not in g.diploma_upgrades_purchased:
                                g.buy_diploma_upgrade(obj)
                                audio.play("diploma")
                            else:
                                audio.play("error")
                        elif kind == "honor_convert":
                            if g.convert_to_honors():
                                audio.play("honor")
                            else:
                                audio.play("error")
                        elif kind == "endow_convert":
                            if g.convert_to_endowments():
                                audio.play("endow")
                            else:
                                audio.play("error")
                        elif kind == "alumni_convert":
                            if g.endowments >= g.alumni_rate:
                                g.do_alumni()
                                audio.play("alumni")
                            else:
                                audio.play("error")
                        elif kind == "alumni_upgrade":
                            if g.buy_alumni_upgrade(obj):
                                audio.play("alumni")
                            else:
                                audio.play("error")
                        elif kind == "alumni_research":
                            if g.buy_alumni_research():
                                audio.play("milestone")
                            else:
                                audio.play("error")
                        elif kind == "honor_upgrade":
                            du = next((d for d in HONOR_UPGRADES if d["id"] == obj), None)
                            if du and g.honors >= du["cost"] and obj not in g.honor_upgrades_purchased:
                                g.buy_honor_upgrade(obj)
                                audio.play("diploma")
                            else:
                                audio.play("error")
                        elif kind == "endow_upgrade":
                            du = next((d for d in ENDOW_UPGRADES if d["id"] == obj), None)
                            if du and g.endowments >= du["cost"] and obj not in g.endow_upgrades_purchased:
                                g.buy_endow_upgrade(obj)
                                audio.play("prestige")
                            else:
                                audio.play("error")
                        elif kind == "use_focus":
                            if g.use_focus_ability(obj):
                                audio.play("skill")
                            else:
                                audio.play("error")
                        elif kind == "legacy_subtab":
                            self.lg_subtab = obj
                        elif kind == "reset_ask":
                            self._reset_confirm = True
                        elif kind == "reset_confirm":
                            g.reset()
                            self._reset_confirm = False
                        elif kind == "scholar":
                            sc = next((s for s in SCHOLARS if s["id"] == obj), None)
                            if sc and g.honors >= sc["cost"] and obj not in g.scholars_purchased:
                                g.buy_scholar(obj)
                                audio.play("scholar")
                            else:
                                audio.play("error")
                        elif kind == "toggle_headmaster":
                            g.show_headmaster = not g.show_headmaster
                        elif kind == "toggle_owned":
                            self._owned_expanded = not self._owned_expanded
                        elif kind == "toggle_mute":
                            audio.toggle_mute()
                        elif kind == "zone_select":
                            zid = obj
                            if zid != self.worlds_sel_zone:
                                self.worlds_sel_zone = zid
                                self.worlds_subtab   = "Overview"
                                self.worlds_b_scroll = 0
                                self.worlds_u_scroll = 0
                        elif kind == "worlds_subtab":
                            self.worlds_subtab   = obj
                            self.worlds_b_scroll = 0
                            self.worlds_u_scroll = 0
                        elif kind == "zone_study":
                            zid = obj
                            if zid in self.world.zones and self.world.is_unlocked(zid, g):
                                zg = self.world.zones[zid]
                                gained = zg.click()
                                audio.play("click")
                                self.floats.append(Float(mx - 30, my - 25,
                                                         f"+{fmt(gained)} KP", (200, 240, 180)))
                        elif kind == "zone_buy_bld":
                            zid, bname = obj
                            if zid in self.world.zones and self.world.is_unlocked(zid, g):
                                zg = self.world.zones[zid]
                                mult = self.buy_mult
                                n    = zg.building_max_buyable(bname) if mult == "max" else int(mult)
                                if n > 0 and zg.buy_building_n(bname, n):
                                    audio.play("buy")
                                else:
                                    audio.play("error")
                        elif kind == "zone_buy_upg":
                            zid, uid = obj
                            if zid in self.world.zones and self.world.is_unlocked(zid, g):
                                zg = self.world.zones[zid]
                                if zg.buy_upgrade(uid):
                                    audio.play("upgrade")
                                else:
                                    audio.play("error")
                        elif kind == "zone_prestige":
                            zid = obj
                            if zid in self.world.zones and self.world.is_unlocked(zid, g):
                                zg = self.world.zones[zid]
                                if zg.prestige_eligible:
                                    zg.do_prestige()
                                    audio.play("prestige")
                                else:
                                    audio.play("error")
                        elif kind == "zone_thought":
                            zid, school = obj
                            if zid in self.world.zones:
                                if self.world.zones[zid].do_prestige_with_thought(school):
                                    self.world.save()
                                    audio.play("prestige")
                                else:
                                    audio.play("error")
                        elif kind == "zone_conv_l2":
                            zid = obj
                            if zid in self.world.zones:
                                if self.world.zones[zid].convert_to_l2():
                                    audio.play("honor")
                                else:
                                    audio.play("error")
                        elif kind == "zone_conv_l3":
                            zid = obj
                            if zid in self.world.zones:
                                if self.world.zones[zid].convert_to_l3():
                                    audio.play("endow")
                                else:
                                    audio.play("error")
                        elif kind == "zone_conv_l4":
                            zid = obj
                            if zid in self.world.zones:
                                if self.world.zones[zid].convert_to_l4():
                                    audio.play("alumni")
                                else:
                                    audio.play("error")
                        elif kind == "zone_active":
                            zid = obj
                            if zid in self.world.zones and self.world.is_unlocked(zid, g):
                                if self.world.zones[zid].do_active_mechanic():
                                    audio.play("skill")
                                else:
                                    audio.play("error")
                        elif kind == "zone_event":
                            zid = obj
                            if zid in self.world.zones:
                                self.world.zones[zid].collect_event()
                                audio.play("collect")
                        elif kind == "resolve_strike":
                            g.resolve_strike()
                        elif kind == "cw_buy":
                            if self.world.buy_cw_upgrade(obj):
                                self.world.save()
                        elif kind == "set_theme":
                            self.game.cosmetic_theme = obj
                            self.game.save()
                        elif kind == "inspection_click":
                            self.game.click_inspection()
                        elif kind == "quiz_start":
                            g.start_quiz()
                        elif kind == "quiz_answer":
                            g.answer_quiz(obj)
                        elif kind == "quiz_reward":
                            g.claim_quiz_reward(obj)
                        elif kind == "create_hero":
                            if self.game.create_hero(world_manager=self.world):
                                audio.play("skill")
                            else:
                                audio.play("error")
                        elif kind == "toggle_fullscreen":
                            self._fullscreen = not self._fullscreen
                            flags = pygame.SCALED
                            if self._fullscreen:
                                flags |= pygame.FULLSCREEN
                            else:
                                flags |= pygame.RESIZABLE
                            try:
                                self.screen = pygame.display.set_mode((W, H), flags)
                            except pygame.error:
                                self._fullscreen = not self._fullscreen
                        elif kind == "toggle_sandbox":
                            if not g.sandbox_mode:
                                g.save()
                                self._normal_game = self.game
                                sandbox = Game()
                                sandbox.sandbox_mode = True
                                sandbox.kp           = 10_000_000.0
                                sandbox.total_kp     = 0.0
                                sandbox.all_time_kp  = 1_000_000_000_000.0
                                sandbox.merit_points = 200
                                sandbox.diplomas     = 100
                                sandbox.honors       = 20
                                sandbox.endowments   = 10
                                sandbox.alumni_points         = 20
                                sandbox.alumni_upgrades_purchased = {d["id"] for d in ALUMNI_UPGRADES}
                                self._prev_ach_count = 0
                                self._prev_story_len = 0
                                self._prev_event     = None
                                self.game = sandbox
                                self.sprites = spr.SpriteManager()
                                self.campus  = CampusView()
                            else:
                                if self._normal_game is not None:
                                    self.game = self._normal_game
                                    self._normal_game = None
                                else:
                                    self.game.sandbox_mode = False
                                self._prev_ach_count = len(self.game.achievements_unlocked)
                                self._prev_story_len = len(self.game.story_queue)
                                self._prev_event     = self.game.pending_event
                                self.sprites = spr.SpriteManager()
                                self.campus  = CampusView()

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run(self):
        last = pygame.time.get_ticks()
        while True:
            now = pygame.time.get_ticks()
            dt  = min((now - last) / 1000.0, 0.1)
            last = now

            popup_btns, story_btns = self._draw(dt)
            self._handle_events(popup_btns, story_btns)

            # Hold-to-study: auto-clicks at 5/sec, 2× base click power, no combo
            g = self.game
            if (self._mouse_held and self._study_btn
                    and not g.story_queue and not self.popup
                    and not g.sandbox_mode):
                mx2, my2 = pygame.mouse.get_pos()
                if self._study_btn.collidepoint(mx2, my2):
                    self._hold_acc         += dt
                    self._hold_float_timer += dt
                    last_gained = 0.0
                    while self._hold_acc >= 0.2:
                        self._hold_acc -= 0.2
                        last_gained = g.hold_click()
                    if last_gained > 0 and self._hold_float_timer >= 0.5:
                        self._hold_float_timer = 0.0
                        audio.play("click")
                        self.floats.append(Float(mx2 - 30, my2 - 25,
                                                 f"+{fmt(last_gained)} KP", (180, 255, 140)))
                else:
                    self._mouse_held = False
                    self._hold_acc   = 0.0

            for f in self.floats:
                f.tick(dt)
                f.draw(self.screen)
            self.floats = [f for f in self.floats if f.alive]
            pygame.display.flip()

            # Apply cross-zone CW bonuses to Zone 1 each frame
            self.game.zone_bonus_mult   = self.world.cross_zone_mult()
            self.game._cw_click_mult    = self.world.zone1_click_mult()
            self.game._cw_diploma_bonus = self.world.zone1_diploma_bonus()
            self.game.update(dt)
            self.world.update(dt, self.game)
            self.game._zone_building_counts = self.world.all_zone_building_counts()
            _spr_zone = self.worlds_sel_zone if self.tab == "Worlds" else 1
            self.sprites.update(dt, self.game.kps(), self.tab, zone_id=_spr_zone)
            self.campus.update(dt)
            self.campus._time = self.game.game_time  # keep campus calendar in sync

            # Auto-click gain floats — drain queue and spawn near study button
            if self.game._auto_click_gains and self._study_btn:
                import random as _rnd
                bx = self._study_btn.centerx
                by = self._study_btn.top
                for _gain in self.game._auto_click_gains:
                    self.floats.append(Float(
                        bx + _rnd.randint(-40, 40),
                        by + _rnd.randint(-30, 0),
                        f"+{fmt(_gain)} KP",
                        color=(150, 230, 150)  # green tint for auto-clicks
                    ))
                self.game._auto_click_gains.clear()

            # Star milestone notifications → milestone flash
            while self.game.star_queue:
                bname, level = self.game.star_queue.pop(0)
                self.game.milestone_queue.append(f"{bname}  {'★' * level}")

            # Sound events
            ach_n = len(self.game.achievements_unlocked)
            if ach_n > self._prev_ach_count:
                audio.play("achievement")
            self._prev_ach_count = ach_n

            daily_done = self.game._total_daily_done
            if daily_done > self._prev_daily_done:
                audio.play("achievement")
            self._prev_daily_done = daily_done

            slen = len(self.game.story_queue)
            if slen > self._prev_story_len:
                audio.play("story")
            self._prev_story_len = slen

            if self.game.pending_event is not None and self._prev_event is None:
                ev_rar = self.game.pending_event.get("rarity", "common")
                audio.play("rare_event" if ev_rar == "rare" else "event")
            self._prev_event = self.game.pending_event

            if not self.game.sandbox_mode:
                if time.time() - self._last_save > AUTO_SAVE_INTERVAL:
                    self.game.save()
                    self._last_save = time.time()
                if time.time() - self._prev_world_save > AUTO_SAVE_INTERVAL:
                    self.world.save()
                    self._prev_world_save = time.time()

            self.clock.tick(FPS)


if __name__ == "__main__":
    import os, traceback
    try:
        App().run()
    except Exception:
        crash_path = os.path.join(os.path.dirname(__file__), "crash.log")
        with open(crash_path, "w") as _cf:
            traceback.print_exc(file=_cf)
        traceback.print_exc()
        raise
