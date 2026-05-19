import datetime
import json
import math
import os
import random
import time
from typing import Dict, Optional, Set

from data import (BUILDINGS, UPGRADES, SKILLS, ACHIEVEMENTS, EVENTS, STORY,
                  SYNERGIES, DIPLOMA_UPGRADES, HONOR_UPGRADES, ENDOW_UPGRADES,
                  ALUMNI_UPGRADES, SCHOLARS, EVENT_RARITY_WEIGHTS,
                  DYNAMIC_NEWS_BUILDING, DYNAMIC_NEWS_ACHIEVEMENT,
                  DYNAMIC_NEWS_PRESTIGE, DYNAMIC_NEWS_MILESTONE,
                  BUILDING_SACRIFICE, QUIZ_QUESTIONS, QUIZ_REWARDS,
                  HERO_CREATION_COST, HERO_PATH_STATS)

SAVE_FILE    = os.path.join(os.path.dirname(__file__), "save.json")
COMBO_MAX    = 10
COMBO_WINDOW = 2.0

FOCUS_ABILITIES = [
    {"id": "surge",  "name": "Study Surge", "cost": 2, "desc": "×3 click power  20s",   "duration": 20.0, "type": "click_boost"},
    {"id": "burst",  "name": "KPS Burst",   "cost": 3, "desc": "×2 KPS  30s",            "duration": 30.0, "type": "kps_boost"},
    {"id": "lucky",  "name": "Lucky Hour",  "cost": 5, "desc": "Force a rare event now", "duration":  0.0, "type": "event"},
    {"id": "recall", "name": "Recall",      "cost": 4, "desc": "Earn 10 min offline KP", "duration":  0.0, "type": "offline"},
]

_INSPECTOR_TRIGGERS  = [1_000_000, 100_000_000, 10_000_000_000, 1_000_000_000_000]
_STAR_THRESHOLDS     = [1_000, 10_000, 100_000, 1_000_000]
_STAR_LEVEL_MULTS    = [1.25, 1.50, 2.00, 3.00]   # applied multiplicatively per star level

_SEASON_MONTHS = {1:'Winter',2:'Winter',3:'Spring',4:'Spring',5:'Spring',
                  6:'Summer',7:'Summer',8:'Summer',9:'Autumn',
                  10:'Autumn',11:'Autumn',12:'Winter'}

MILESTONES = [
    1e2, 5e2, 1e3, 5e3, 1e4, 5e4, 1e5, 5e5,
    1e6, 5e6, 1e7, 5e7, 1e8, 5e8, 1e9, 5e9,
    1e10, 1e11, 1e12, 1e15, 1e18, 1e21, 1e24, 1e27, 1e30,
]


_SUFFIXES = [
    (1e48, "Qd"), (1e45, "Td"), (1e42, "Dd"), (1e39, "Ud"),
    (1e36, "De"), (1e33, "No"), (1e30, "Oc"), (1e27, "Sp"),
    (1e24, "Sx"), (1e21, "Qt"), (1e18, "Qi"), (1e15, "Qa"),
    (1e12, "T"),  (1e9,  "B"),  (1e6,  "M"),  (1e3,  "K"),
]

def fmt(n: float) -> str:
    if not math.isfinite(n):
        return "MAX" if n > 0 else "?"
    if n < 0:
        return f"-{fmt(-n)}"
    for threshold, suffix in _SUFFIXES:
        if n >= threshold:
            val = n / threshold
            if val >= 100:
                return f"{val:.1f}{suffix}"
            elif val >= 10:
                return f"{val:.2f}{suffix}"
            return f"{val:.3f}{suffix}"
    if n >= 1e51:
        exp = int(math.log10(n))
        return f"{n/10**exp:.2f}e{exp}"
    return f"{n:.1f}"


def _safe_pow(base: float, exp: float) -> float:
    """Exponentiation capped to prevent float overflow."""
    return math.exp(min(exp * math.log(base), 700.0))


class Game:
    def __init__(self):
        self.building_counts: Dict[str, int] = {b.name: 0 for b in BUILDINGS}
        self._zone_building_counts: Dict[str, int] = {}   # populated by App from WorldManager
        self.upgrades_purchased: Set[str]    = set()
        self.skills_purchased:   Set[str]    = set()
        self.achievements_unlocked: Set[str] = set()

        self.kp           = 0.0
        self.total_kp     = 0.0   # resets on prestige
        self.all_time_kp  = 0.0   # never resets
        self.total_clicks = 0
        self.click_base   = 1.0

        # Prestige layer 1
        self.diplomas       = 0
        self.merit_points   = 0
        self.prestige_count = 0
        self.diploma_upgrades_purchased: Set[str] = set()

        # Prestige layer 2 — Honors
        self.honors                  = 0
        self.total_honors_earned     = 0
        self.honor_upgrades_purchased: Set[str] = set()

        # Prestige layer 3 — Endowments
        self.endowments              = 0
        self.total_endow_earned      = 0
        self.endow_upgrades_purchased: Set[str] = set()

        # Prestige layer 4 — Alumni Network
        self.alumni_points             = 0
        self.total_alumni_earned       = 0
        self.alumni_upgrades_purchased: Set[str] = set()
        self.alumni_research_count     = 0   # endgame: repeatable +10% KPS each

        # Achievement notifications
        self.new_achievements: list[str] = []
        self.ach_toast_timer = 0.0

        # Offline popup
        self.offline_kp_gained  = 0.0
        self.offline_hours      = 0.0
        self.offline_cap_hours  = 8.0
        self.show_offline_popup = False

        # Random events
        self.event_timer: float        = random.uniform(90, 150)
        self.pending_event: Optional[dict] = None
        self.active_boost:  Optional[dict] = None

        # Staff strike (negative timed debuff)
        self._staff_strike_active = False
        self._staff_strike_timer  = 0.0
        self._strike_notify       = False   # show the notification once when it starts

        # Auto-clicker (from diploma upgrades)
        self._auto_click_acc   = 0.0
        self._auto_click_gains: list[float] = []   # drained by main.py for Float display

        # School Inspection minigame
        self._inspection_active  = False
        self._inspection_timer   = 0.0
        self._inspection_clicks  = 0
        self._inspection_target  = 30

        # Campus cosmetic theme
        self.cosmetic_theme = "classic"

        # Cross-zone bonuses (set from main.py each frame based on CW purchases)
        self.zone_bonus_mult   = 1.0   # from WorldManager.cross_zone_mult()
        self._cw_click_mult    = 1.0   # from WorldManager.zone1_click_mult()
        self._cw_diploma_bonus = 0     # from WorldManager.zone1_diploma_bonus() (int)

        # Quiz system
        self._quiz_active         = False
        self._quiz_questions: list[dict] = []
        self._quiz_idx            = 0
        self._quiz_correct        = 0
        self._quiz_cooldown       = 0.0   # seconds until next quiz available
        self._quiz_fail_msg       = ""    # shown briefly on wrong answer
        self._quiz_fail_timer     = 0.0
        self._quiz_showing_reward = False
        self._quiz_reward_options: list[str] = []   # 3 tier keys to display
        self.quiz_tiers_earned:    Set[str]  = set()
        self.quiz_perm_kps_bonus   = 0.0   # additive fraction (0.10 = +10%)
        self.quiz_perm_diploma_bonus = 0   # extra diplomas per prestige
        self.one_in_million        = False  # True = earned achievement

        # Story
        self.story_shown:  Set[str]  = set()
        self.story_queue:  list[str] = []

        # Combo
        self.combo       = 0
        self.combo_timer = 0.0
        self.max_combo_reached = 0

        # Milestones
        self.milestones_hit:  Set[float] = set()
        self.milestone_queue: list[str]  = []

        # Focus Points
        self.focus_points     = 0.0
        self.focus_active: Optional[dict] = None   # {"id": str, "timer": float}
        self._fp_click_acc    = 0.0
        self.focus_debuff_timer = 0.0              # inspector fail debuff timer

        # Inspector
        self.inspector: Optional[dict] = None
        self._inspectors_done: Set[float] = set()

        # Scholars
        self.scholars_purchased: Set[str] = set()

        # Building star milestones (bname → star level 0-4)
        self.star_milestones_hit: Dict[str, int] = {}
        self.star_queue: list[tuple] = []   # (bname, level) notification queue

        # Faculty hires (bname → cumulative % KPS bonus)
        self.faculty_bonuses: Dict[str, float] = {}

        # Daily missions
        self.daily_missions: list[dict] = []
        self._daily_date:    str  = ""
        self._kp_today:      float = 0.0
        self._clicks_today:  int   = 0
        self._buys_today:    int   = 0

        # Game clock (real elapsed seconds; drives season / campus sync)
        self.game_time = 0.0

        # KPS history (sampled every 60 real seconds, up to 120 entries)
        self._kps_samples:   list  = []
        self._last_sample_t: float = time.time()

        # Achievement tracking counters
        self._total_faculty_hires     = 0
        self._total_daily_done        = 0
        self._seasons_seen: Set[str]  = set()
        self.best_kps                 = 0.0
        self.best_run_kp              = 0.0
        self._total_events_collected  = 0
        self._total_focus_uses        = 0

        # School identity
        self.school_name    = "Edu Empire Academy"
        self.show_headmaster = True

        # Hero (Zone 10)
        self.hero: Optional[dict] = None   # None until created

        # Dynamic news (session-only; not persisted)
        self.dynamic_news_queue:   list[str] = []
        self._first_buy_news_shown: set[str] = set()

        # Sandbox (never persisted — session flag only)
        self.sandbox_mode = False

        self.last_save_time = time.time()
        self.session_start  = time.time()

    # ── Skill / upgrade helpers ───────────────────────────────────────────────

    def _skill_sum(self, effect_type: str, target: str = "") -> float:
        return sum(
            s.effect_value
            for s in SKILLS
            if s.id in self.skills_purchased
            and s.effect_type == effect_type
            and (not target or s.effect_target == target)
        )

    def _skill_prod(self, effect_type: str) -> float:
        p = 1.0
        for s in SKILLS:
            if s.id in self.skills_purchased and s.effect_type == effect_type:
                p *= s.effect_value
        return p

    def _dipl_sum(self, effect: str) -> float:
        return sum(du["value"] for du in DIPLOMA_UPGRADES
                   if du["id"] in self.diploma_upgrades_purchased
                   and du["effect"] == effect)

    def _dipl_prod(self, effect: str) -> float:
        p = 1.0
        for du in DIPLOMA_UPGRADES:
            if du["id"] in self.diploma_upgrades_purchased and du["effect"] == effect:
                p *= du["value"]
        return p

    def _honor_sum(self, effect: str) -> float:
        return sum(du["value"] for du in HONOR_UPGRADES
                   if du["id"] in self.honor_upgrades_purchased
                   and du["effect"] == effect)

    def _honor_prod(self, effect: str) -> float:
        p = 1.0
        for du in HONOR_UPGRADES:
            if du["id"] in self.honor_upgrades_purchased and du["effect"] == effect:
                p *= du["value"]
        return p

    def _endow_sum(self, effect: str) -> float:
        return sum(du["value"] for du in ENDOW_UPGRADES
                   if du["id"] in self.endow_upgrades_purchased
                   and du["effect"] == effect)

    def _endow_prod(self, effect: str) -> float:
        p = 1.0
        for du in ENDOW_UPGRADES:
            if du["id"] in self.endow_upgrades_purchased and du["effect"] == effect:
                p *= du["value"]
        return p

    def _alumni_sum(self, effect: str) -> float:
        return sum(du["value"] for du in ALUMNI_UPGRADES
                   if du["id"] in self.alumni_upgrades_purchased
                   and du["effect"] == effect)

    def _alumni_prod(self, effect: str) -> float:
        p = 1.0
        for du in ALUMNI_UPGRADES:
            if du["id"] in self.alumni_upgrades_purchased and du["effect"] == effect:
                p *= du["value"]
        return p

    @property
    def alumni_rate(self) -> int:
        return 3

    def do_alumni(self):
        if self.endowments < self.alumni_rate:
            return
        self.endowments   -= self.alumni_rate
        self.alumni_points += 1
        self.total_alumni_earned += 1
        self._check_achievements()
        self.save()

    def buy_alumni_upgrade(self, uid: str) -> bool:
        du = next((d for d in ALUMNI_UPGRADES if d["id"] == uid), None)
        if not du or uid in self.alumni_upgrades_purchased:
            return False
        if self.alumni_points < du["cost"]:
            return False
        self.alumni_points -= du["cost"]
        self.alumni_upgrades_purchased.add(uid)
        self.save()
        return True

    @property
    def alumni_all_purchased(self) -> bool:
        return all(d["id"] in self.alumni_upgrades_purchased for d in ALUMNI_UPGRADES)

    def buy_alumni_research(self) -> bool:
        if not self.alumni_all_purchased or self.alumni_points < 2:
            return False
        self.alumni_points        -= 2
        self.alumni_research_count += 1
        self._check_achievements()
        self.save()
        return True

    def _scholar_sum(self, effect: str, target: str = "") -> float:
        return sum(
            sc["value"]
            for sc in SCHOLARS
            if sc["id"] in self.scholars_purchased
            and sc["effect"] == effect
            and (not target or sc.get("target", "") == target)
        )

    def _hero_stat(self, key: str) -> int:
        if self.hero is None:
            return 0
        return self.hero["stats"].get(key, 0)

    @staticmethod
    def _hero_xp_needed(level: int) -> int:
        return round(200 * (1.7 ** (level - 1)))

    # ── Season ───────────────────────────────────────────────────────────────

    @property
    def season(self) -> str:
        DAY_CYCLE = 60.0
        total_days = int(self.game_time / DAY_CYCLE)
        doy  = total_days % 365
        month = 12
        for m, days in enumerate([31,28,31,30,31,30,31,31,30,31,30,31], 1):
            if doy < days:
                month = m
                break
            doy -= days
        return _SEASON_MONTHS.get(month, 'Spring')

    def _season_kps_mult(self) -> float:
        return {'Spring': 1.08, 'Summer': 1.0, 'Autumn': 1.05, 'Winter': 1.0}.get(self.season, 1.0)

    def _season_click_mult(self) -> float:
        return {'Spring': 1.0, 'Summer': 1.12, 'Autumn': 1.0, 'Winter': 1.0}.get(self.season, 1.0)

    def _season_diploma_mult(self) -> float:
        return 1.15 if self.season == 'Autumn' else 1.0

    def _season_offline_mult(self) -> float:
        return 1.25 if self.season == 'Winter' else 1.0

    # ── Star milestones ───────────────────────────────────────────────────────

    def _building_star_mult(self, bname: str) -> float:
        level = self.star_milestones_hit.get(bname, 0)
        result = 1.0
        for i in range(level):
            result *= _STAR_LEVEL_MULTS[i]
        return result

    def _check_star_milestones(self):
        for b in BUILDINGS:
            cnt = self.building_counts[b.name]
            current = self.star_milestones_hit.get(b.name, 0)
            for level, threshold in enumerate(_STAR_THRESHOLDS, 1):
                if cnt >= threshold and current < level:
                    self.star_milestones_hit[b.name] = level
                    self.star_queue.append((b.name, level))

    # ── Daily missions ────────────────────────────────────────────────────────

    def _mission_click_target(self) -> int:
        return max(50, min(5_000, self.total_clicks // 20 + 50))

    def _mission_kp_target(self) -> float:
        return max(1_000.0, self.kps() * 300.0 + self.click_power * 100.0)

    def _mission_buy_target(self) -> int:
        return max(5, min(200, sum(self.building_counts.values()) // 10 + 5))

    def _refresh_daily_missions(self):
        today = datetime.date.today().isoformat()
        if self._daily_date == today and self.daily_missions:
            return
        self._daily_date    = today
        self._kp_today      = 0.0
        self._clicks_today  = 0
        self._buys_today    = 0
        self.daily_missions = [
            {"type": "clicks_today", "label": "Dedicated Student",
             "desc": f"Click {self._mission_click_target()} times",
             "target": self._mission_click_target(), "reward": 3, "completed": False},
            {"type": "kp_today",     "label": "Knowledge Seeker",
             "desc": f"Earn {fmt(self._mission_kp_target())} KP",
             "target": self._mission_kp_target(),   "reward": 4, "completed": False},
            {"type": "buys_today",   "label": "Campus Builder",
             "desc": f"Buy {self._mission_buy_target()} buildings",
             "target": self._mission_buy_target(),  "reward": 3, "completed": False},
        ]

    def _check_daily_missions(self):
        self._refresh_daily_missions()
        newly_done = 0
        for m in self.daily_missions:
            if m["completed"]:
                continue
            prog = self._daily_progress(m["type"])
            if prog >= m["target"]:
                m["completed"] = True
                self.merit_points += m["reward"]
                newly_done += 1
        if newly_done and all(m["completed"] for m in self.daily_missions):
            self._total_daily_done += 1
            self._check_achievements()

    def _daily_progress(self, mission_type: str) -> float:
        if mission_type == "clicks_today": return float(self._clicks_today)
        if mission_type == "kp_today":     return self._kp_today
        if mission_type == "buys_today":   return float(self._buys_today)
        return 0.0

    # ── Combo ─────────────────────────────────────────────────────────────────

    @property
    def _effective_combo_max(self) -> int:
        return COMBO_MAX + int(self._skill_sum("combo_cap_bonus"))

    @property
    def combo_mult(self) -> float:
        return 1.0 + self.combo * 0.25

    # ── Honor conversion rate ─────────────────────────────────────────────────

    @property
    def honor_rate(self) -> int:
        for s in SKILLS:
            if s.id in self.skills_purchased and s.effect_type == "honor_rate":
                return int(s.effect_value)
        return 15

    # ── KPS / click ───────────────────────────────────────────────────────────

    @property
    def click_power(self) -> float:
        base      = self.click_base + self._skill_sum("click_base") + self._dipl_sum("click_base") + self._honor_sum("click_base")
        upg_mult  = 1.0
        for u in UPGRADES:
            if u.target == "click" and u.name in self.upgrades_purchased:
                upg_mult *= u.mult
        skill_mult = self._skill_prod("click_mult")
        dipl_mult  = self._dipl_prod("click_mult")
        honor_mult = self._honor_prod("click_mult")
        endow_mult = self._endow_prod("click_mult")
        alumni_mult = self._alumni_prod("click_mult")
        hero_agility_mult = 1.0 + self._hero_stat("agility") * 0.005
        total_click = base * upg_mult * skill_mult * dipl_mult * honor_mult * endow_mult * alumni_mult * self._event_click_mult() * self.combo_mult * self._focus_click_mult() * self._season_click_mult() * hero_agility_mult
        return total_click * self._cw_click_mult

    def _building_mult(self, bname: str) -> float:
        upg_mult    = 1.0
        for u in UPGRADES:
            if u.target == bname and u.name in self.upgrades_purchased:
                upg_mult *= u.mult
        skill_bonus   = self._skill_sum("building_bonus", bname)
        syn_amp       = self._skill_sum("synergy_amp") + self._honor_sum("synergy_amp")
        syn_bonus     = sum(
            self.building_counts.get(src, 0) * pct
            for src, pct in SYNERGIES.get(bname, [])
        ) * (1.0 + syn_amp)
        scholar_bonus = self._scholar_sum("building_bonus", bname)
        faculty_bonus = self.faculty_bonuses.get(bname, 0.0)
        star_mult     = self._building_star_mult(bname)
        hero_tech_bonus = self._hero_stat("tech_power") * 0.005
        return upg_mult * (1.0 + skill_bonus + syn_bonus + scholar_bonus + faculty_bonus + hero_tech_bonus) * star_mult

    def _global_mult(self) -> float:
        diploma_mult        = 1.0 + math.log1p(self.diplomas) * 1.5
        honor_mult          = _safe_pow(1.03, self.honors)
        endow_mult          = _safe_pow(1.10, self.endowments)
        # Each alumni point provides a direct +15% KPS — visible regardless of upgrades
        alumni_direct_mult  = 1.0 + self.alumni_points * 0.15
        pct_bonus           = self._skill_sum("global_kps")
        honor_kps_bonus     = self._skill_sum("honor_kps")  * self.honors
        endow_kps_bonus     = self._skill_sum("endow_kps")  * self.endowments
        scholar_bonus       = self._scholar_sum("global_kps")
        skill_mult          = self._skill_prod("global_kps_mult")
        dipl_mult           = self._dipl_prod("global_mult")
        honor_upg_mult      = self._honor_prod("global_mult")
        endow_upg_mult      = self._endow_prod("global_mult")
        alumni_upg_mult     = self._alumni_prod("global_mult")
        research_grant_mult = _safe_pow(1.10, self.alumni_research_count)
        # Strike debuff
        strike_mult = 0.25 if self._staff_strike_active else 1.0
        quiz_perm_mult  = 1.0 + self.quiz_perm_kps_bonus
        million_mult    = 1.15 if self.one_in_million else 1.0
        # Hero passive: Intelligence → global KPS, Transcendence → all-zone wisdom
        hero_int_mult   = 1.0 + self._hero_stat("intelligence") * 0.005
        hero_trans_mult = 1.0 + self._hero_stat("transcendence") * 0.004
        return (diploma_mult * honor_mult * endow_mult * alumni_direct_mult
                * (1.0 + pct_bonus + honor_kps_bonus + endow_kps_bonus + scholar_bonus)
                * skill_mult * dipl_mult * honor_upg_mult * endow_upg_mult
                * alumni_upg_mult * research_grant_mult * strike_mult * self.zone_bonus_mult
                * quiz_perm_mult * million_mult * hero_int_mult * hero_trans_mult)

    def _event_kps_mult(self) -> float:
        if self.active_boost and self.active_boost["type"] == "kps_boost":
            return self.active_boost["value"]
        return 1.0

    def _event_click_mult(self) -> float:
        if self.active_boost and self.active_boost["type"] == "click_boost":
            return self.active_boost["value"]
        return 1.0

    def building_kps(self, bname: str) -> float:
        bd = next(b for b in BUILDINGS if b.name == bname)
        return bd.base_kps * self.building_counts[bname] * self._building_mult(bname)

    def kps(self) -> float:
        raw = sum(self.building_kps(b.name) for b in BUILDINGS)
        mult = self._global_mult() * self._event_kps_mult() * self._focus_kps_mult() * self._season_kps_mult()
        if self.focus_debuff_timer > 0:
            mult *= 0.90
        return raw * mult

    def building_cost(self, bname: str) -> float:
        return self._building_cost_at(bname, self.building_counts[bname])

    def _building_cost_at(self, bname: str, n: int) -> float:
        bd       = next(b for b in BUILDINGS if b.name == bname)
        discount = min(0.90, self._dipl_sum("cost_discount")
                            + self._honor_sum("cost_discount")
                            + self._endow_sum("cost_discount")
                            + self._alumni_sum("cost_discount")
                            + self._hero_stat("resilience") * 0.002)
        cost = bd.base_cost * (1.15 ** n) * (1.0 - discount)
        if self.sandbox_mode:
            cost /= 1000.0
        return max(1.0, cost)

    def building_cost_n(self, bname: str, n: int) -> float:
        current = self.building_counts[bname]
        return sum(self._building_cost_at(bname, current + i) for i in range(n))

    def building_max_buyable(self, bname: str) -> int:
        n, total, current = 0, 0.0, self.building_counts[bname]
        sac = BUILDING_SACRIFICE.get(bname)
        sac_avail = (self.building_counts.get(sac[0], 0) if sac and not self.sandbox_mode else 10_000_000)
        while True:
            c = self._building_cost_at(bname, current + n)
            if total + c > self.kp or n >= 10_000:
                break
            if sac and (n + 1) * sac[1] > sac_avail:
                break
            total += c
            n += 1
        return n

    def buy_building_n(self, bname: str, n: int) -> bool:
        if n <= 0:
            return False
        cost = self.building_cost_n(bname, n)
        if self.kp < cost:
            return False
        sac = BUILDING_SACRIFICE.get(bname)
        if sac and not self.sandbox_mode:
            sac_name, sac_count = sac
            total_sac = n * sac_count
            if self.building_counts.get(sac_name, 0) < total_sac:
                return False
            self.building_counts[sac_name] -= total_sac
        first = self.building_counts[bname] == 0
        self.kp -= cost
        self.building_counts[bname] += n
        self._buys_today += n
        self._check_achievements()
        if first and bname not in self._first_buy_news_shown and not self.sandbox_mode:
            self._first_buy_news_shown.add(bname)
            templates = DYNAMIC_NEWS_BUILDING.get(bname, [])
            if templates:
                self._queue_news(random.choice(templates))
        return True

    # ── Focus helpers ─────────────────────────────────────────────────────────

    def _focus_cap(self) -> float:
        return 10.0 + self._skill_sum("focus_cap")

    def _focus_click_mult(self) -> float:
        if self.focus_active and self.focus_active["id"] == "surge":
            return 3.0
        return 1.0

    def _focus_kps_mult(self) -> float:
        if self.focus_active and self.focus_active["id"] == "burst":
            return 2.0
        return 1.0

    def use_focus_ability(self, ability_id: str) -> bool:
        ab = next((a for a in FOCUS_ABILITIES if a["id"] == ability_id), None)
        if not ab or self.focus_points < ab["cost"]:
            return False
        self.focus_points -= ab["cost"]
        self._total_focus_uses += 1
        if ab["duration"] > 0:
            self.focus_active = {"id": ability_id, "timer": ab["duration"]}
        elif ab["type"] == "event":
            if not self.pending_event:
                rare = [e for e in EVENTS if e.get("rarity") == "rare"]
                if rare:
                    ev = random.choice(rare).copy()
                    if ev["type"] == "kp_bonus":
                        ev["kp_amount"] = self.kps() * ev["value_mult"]
                    self.pending_event = ev
        elif ab["type"] == "offline":
            gained = self.kps() * 600 * 0.5   # 10 min at 50% efficiency
            self.kp += gained; self.total_kp += gained; self.all_time_kp += gained
        return True

    # ── Inspector ─────────────────────────────────────────────────────────────

    def _tick_inspector(self, dt: float):
        # Trigger check
        if not self.inspector and not self.sandbox_mode and self.kps() > 0:
            for t in _INSPECTOR_TRIGGERS:
                if t not in self._inspectors_done and self.all_time_kp >= t:
                    self._inspectors_done.add(t)
                    self.inspector = {
                        "timer":     60.0,
                        "target_kp": self.kps() * 60.0 * 1.5,
                        "earned":    0.0,
                        "result":    None,
                        "result_timer": 3.5,
                    }
                    break

        if not self.inspector:
            return
        insp = self.inspector
        if insp["result"] is None:
            insp["timer"] -= dt
            # passive KP tick counted separately from click in click()
            insp["earned"] += self.kps() * dt
            if insp["earned"] >= insp["target_kp"]:
                insp["result"] = "success"
                bonus = max(2, self.prestige_count + 2)
                self.merit_points += bonus
            elif insp["timer"] <= 0:
                insp["result"] = "fail"
                self.focus_debuff_timer = 120.0
        else:
            insp["result_timer"] -= dt
            if insp["result_timer"] <= 0:
                self.inspector = None

    def upgrade_cost(self, uname: str) -> float:
        u = next((x for x in UPGRADES if x.name == uname), None)
        if not u:
            return float("inf")
        cost = float(u.cost)
        if self.sandbox_mode:
            cost /= 1000.0
        return max(1.0, cost)

    # ── Actions ───────────────────────────────────────────────────────────────

    def hold_click(self) -> float:
        """Auto-click from holding mouse: 2× base click power, no combo interaction."""
        gained = (self.click_power / self.combo_mult) * 2.0
        self.kp            += gained
        self.total_kp      += gained
        self.all_time_kp   += gained
        self.total_clicks  += 1
        self._clicks_today += 1
        self._fp_click_acc += 1
        if self._fp_click_acc >= 50:
            self._fp_click_acc -= 50
            self.focus_points = min(self._focus_cap(), self.focus_points + 1.0)
        if self.inspector and self.inspector.get("result") is None:
            self.inspector["earned"] += gained
        return gained

    def click(self) -> float:
        eff_max = self._effective_combo_max
        if self.combo_timer > 0:
            self.combo = min(self.combo + 1, eff_max)
        else:
            self.combo = 1
        self.combo_timer = COMBO_WINDOW
        self.max_combo_reached = max(self.max_combo_reached, self.combo)

        gained = self.click_power
        self.kp          += gained
        self.total_kp    += gained
        self.all_time_kp += gained
        self.total_clicks  += 1
        self._clicks_today += 1
        self._check_achievements()
        self._fp_click_acc += 1
        if self._fp_click_acc >= 50:
            self._fp_click_acc -= 50
            self.focus_points = min(self._focus_cap(), self.focus_points + 1.0)
        if self.inspector and self.inspector.get("result") is None:
            self.inspector["earned"] += gained
        return gained

    def update(self, dt: float):
        gained = self.kps() * dt
        self.kp          += gained
        self.total_kp    += gained
        self.all_time_kp += gained
        self._kp_today   += gained
        self.game_time   += dt
        self._seasons_seen.add(self.season)
        now_t = time.time()
        if now_t - self._last_sample_t >= 60.0:
            self._kps_samples.append((self.game_time, self.kps()))
            if len(self._kps_samples) > 120:
                self._kps_samples = self._kps_samples[-120:]
            self._last_sample_t = now_t
        current_kps = self.kps()
        if current_kps > self.best_kps:
            self.best_kps = current_kps
        if self.total_kp > self.best_run_kp:
            self.best_run_kp = self.total_kp
        self._check_achievements()
        self._check_story()
        self._check_milestones()
        self._check_star_milestones()
        self._check_daily_missions()

        if self.ach_toast_timer > 0:
            self.ach_toast_timer -= dt

        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0

        if self.pending_event is None and self.active_boost is None:
            self.event_timer -= dt
            if self.event_timer <= 0:
                self._spawn_event()

        if self.active_boost:
            self.active_boost["remaining"] -= dt
            if self.active_boost["remaining"] <= 0:
                self.active_boost = None
                self.event_timer  = random.uniform(90, 150)

        # Focus regen
        regen_rate = (1.0 / 30.0) * (1.0 + self._skill_sum("focus_regen"))
        self.focus_points = min(self._focus_cap(), self.focus_points + regen_rate * dt)
        if self.focus_active:
            self.focus_active["timer"] -= dt
            if self.focus_active["timer"] <= 0:
                self.focus_active = None
        if self.focus_debuff_timer > 0:
            self.focus_debuff_timer -= dt
        # Inspector
        self._tick_inspector(dt)

        # Staff strike tick
        if self._staff_strike_active:
            self._staff_strike_timer -= dt
            if self._staff_strike_timer <= 0:
                self._staff_strike_active = False
                self._strike_notify       = False

        # Auto-clicker (from diploma upgrades)
        auto_rate = self._dipl_sum("auto_click_rate")
        if auto_rate > 0:
            self._auto_click_acc += dt
            interval = 1.0 / auto_rate
            while self._auto_click_acc >= interval:
                self._auto_click_acc -= interval
                # Auto-clicks grant full click_power but do NOT build combo
                gain = self.click_power
                self.kp          += gain
                self.total_kp    += gain
                self.all_time_kp += gain
                self._auto_click_gains.append(gain)

        # School Inspection countdown
        if self._inspection_active:
            self._inspection_timer -= dt
            if self._inspection_timer <= 0:
                self._end_inspection(False)

        # Quiz cooldown
        if self._quiz_cooldown > 0:
            self._quiz_cooldown = max(0.0, self._quiz_cooldown - dt)
        if self._quiz_fail_timer > 0:
            self._quiz_fail_timer = max(0.0, self._quiz_fail_timer - dt)
            if self._quiz_fail_timer <= 0:
                self._quiz_fail_msg = ""

        self.update_hero(dt)

    def resolve_strike(self) -> bool:
        """Pay 5 merit to end the strike early."""
        if not self._staff_strike_active or self.merit_points < 5:
            return False
        self.merit_points       -= 5
        self._staff_strike_active = False
        self._staff_strike_timer  = 0.0
        self._strike_notify       = False
        return True

    def start_inspection(self) -> None:
        self._inspection_active = True
        self._inspection_timer  = 20.0
        self._inspection_clicks = 0
        self._inspection_target = 30

    def click_inspection(self) -> None:
        if not self._inspection_active:
            return
        self._inspection_clicks += 1
        if self._inspection_clicks >= self._inspection_target:
            self._end_inspection(True)

    def _end_inspection(self, success: bool) -> None:
        self._inspection_active = False
        self._inspection_timer  = 0.0
        if success:
            # Award a temporary KPS boost as active_boost
            self.active_boost = {"type": "kps_boost", "value": 2.0, "remaining": 60.0,
                                 "duration": 60.0, "name": "Inspection: Outstanding!"}
            self.milestone_queue.append("Inspection passed! KP/s ×2 for 60 seconds!")

    # ── Quiz ──────────────────────────────────────────────────────────────────

    def start_quiz(self) -> None:
        if self._quiz_active or self._quiz_cooldown > 0:
            return
        per_type = {"math": [], "spelling": [], "history": []}
        for q in QUIZ_QUESTIONS:
            per_type[q["type"]].append(q)
        import random as _r
        selected = []
        for t in ("math", "spelling", "history"):
            pool = per_type[t]
            if pool:
                selected.append(_r.choice(pool))
        _r.shuffle(selected)
        self._quiz_questions      = selected
        self._quiz_idx            = 0
        self._quiz_correct        = 0
        self._quiz_active         = True
        self._quiz_showing_reward = False
        self._quiz_reward_options = []
        self._quiz_fail_msg       = ""
        self._quiz_fail_timer     = 0.0

    def answer_quiz(self, answer: str) -> bool:
        if not self._quiz_active or self._quiz_showing_reward:
            return False
        q = self._quiz_questions[self._quiz_idx]
        correct = (answer == q["a"])
        if correct:
            self._quiz_correct += 1
            self._quiz_idx += 1
            if self._quiz_idx >= len(self._quiz_questions):
                self._complete_quiz()
        else:
            self._quiz_fail_msg   = f"Wrong! The answer was: {q['a']}"
            self._quiz_fail_timer = 3.0
            self._quiz_active     = False
            self._quiz_cooldown   = 120.0   # 2 minute cooldown on wrong answer
        return correct

    def _complete_quiz(self) -> None:
        import random as _r
        # Roll 1-in-a-million for the special achievement
        if not self.one_in_million and _r.randint(1, 1_000_000) == 1:
            self.one_in_million = True
            self.milestone_queue.append("ONE IN A MILLION! All stats permanently +15%!")

        # Generate 3 unique reward tier options (weighted sampling without replacement)
        tiers  = list(QUIZ_REWARDS.keys())
        weights= [QUIZ_REWARDS[t]["weight"] for t in tiers]
        chosen = []
        remaining_tiers   = list(tiers)
        remaining_weights = list(weights)
        for _ in range(min(3, len(remaining_tiers))):
            total = sum(remaining_weights)
            r     = _r.uniform(0, total)
            cumul = 0.0
            for i, w in enumerate(remaining_weights):
                cumul += w
                if r <= cumul:
                    chosen.append(remaining_tiers[i])
                    remaining_tiers.pop(i)
                    remaining_weights.pop(i)
                    break
        self._quiz_reward_options = chosen
        self._quiz_showing_reward = True

    def claim_quiz_reward(self, tier: str) -> None:
        if not self._quiz_showing_reward or tier not in QUIZ_REWARDS:
            return
        reward = QUIZ_REWARDS[tier]
        rtype  = reward["type"]
        if rtype in ("kps_boost", "click_boost"):
            self.active_boost = {"type": rtype, "value": reward["value"],
                                 "remaining": reward["duration"], "duration": reward["duration"],
                                 "name": f"Quiz: {reward['name']}!"}
        elif rtype == "perm_kps":
            self.quiz_perm_kps_bonus += reward["value"]
        elif rtype == "perm_diploma":
            self.quiz_perm_diploma_bonus += int(reward["value"])
        elif rtype == "free_prestige":
            self._free_prestige()

        self.quiz_tiers_earned.add(tier)
        self._quiz_active         = False
        self._quiz_showing_reward = False
        self._quiz_reward_options = []
        self._quiz_cooldown       = 180.0   # 3 minute cooldown after completing
        self._check_achievements()
        self.save()

    def _free_prestige(self) -> None:
        """Prestige without losing any buildings, KP, or upgrades."""
        n = self.diplomas_on_prestige
        self.diplomas              += n
        self.total_diplomas_earned  = getattr(self, "total_diplomas_earned", 0) + n
        self.prestige_count        += 1
        self.milestone_queue.append(f"Mythic Quiz Reward! +{n} Diplomas — no progress lost!")

    # ── Purchases ─────────────────────────────────────────────────────────────

    def buy_building(self, bname: str) -> bool:
        cost = self.building_cost(bname)
        if self.kp < cost:
            return False
        sac = BUILDING_SACRIFICE.get(bname)
        if sac and not self.sandbox_mode:
            sac_name, sac_count = sac
            if self.building_counts.get(sac_name, 0) < sac_count:
                return False
            self.building_counts[sac_name] -= sac_count
        first = self.building_counts[bname] == 0
        self.kp -= cost
        self.building_counts[bname] += 1
        self._buys_today += 1
        self._check_achievements()
        if first and bname not in self._first_buy_news_shown and not self.sandbox_mode:
            self._first_buy_news_shown.add(bname)
            templates = DYNAMIC_NEWS_BUILDING.get(bname, [])
            if templates:
                self._queue_news(random.choice(templates))
        return True

    def buy_upgrade(self, uname: str) -> bool:
        u    = next((x for x in UPGRADES if x.name == uname), None)
        cost = self.upgrade_cost(uname)
        if u and uname not in self.upgrades_purchased and self.kp >= cost:
            self.kp -= cost
            self.upgrades_purchased.add(uname)
            return True
        return False

    def buy_skill(self, sid: str) -> bool:
        s = next((x for x in SKILLS if x.id == sid), None)
        if not s or sid in self.skills_purchased:
            return False
        if s.requires and s.requires not in self.skills_purchased:
            return False
        if self.merit_points < s.cost:
            return False
        self.merit_points -= s.cost
        self.skills_purchased.add(sid)
        return True

    def buy_diploma_upgrade(self, uid: str) -> bool:
        du = next((d for d in DIPLOMA_UPGRADES if d["id"] == uid), None)
        if not du or uid in self.diploma_upgrades_purchased:
            return False
        if self.diplomas < du["cost"]:
            return False
        self.diplomas -= du["cost"]
        self.diploma_upgrades_purchased.add(uid)
        return True

    def convert_to_honors(self) -> bool:
        rate = self.honor_rate
        if self.diplomas < rate:
            return False
        self.diplomas -= rate
        self.honors   += 1
        self.total_honors_earned += 1
        self._check_achievements()
        self._check_story()
        return True

    def convert_to_endowments(self) -> bool:
        if self.honors < 5:
            return False
        self.honors    -= 5
        self.endowments += 1
        self.total_endow_earned += 1
        self._check_achievements()
        self._check_story()
        return True

    def buy_honor_upgrade(self, uid: str) -> bool:
        du = next((d for d in HONOR_UPGRADES if d["id"] == uid), None)
        if not du or uid in self.honor_upgrades_purchased:
            return False
        if self.honors < du["cost"]:
            return False
        self.honors -= du["cost"]
        self.honor_upgrades_purchased.add(uid)
        return True

    def buy_scholar(self, sid: str) -> bool:
        sc = next((s for s in SCHOLARS if s["id"] == sid), None)
        if not sc or sid in self.scholars_purchased:
            return False
        if self.honors < sc["cost"]:
            return False
        self.honors -= sc["cost"]
        self.scholars_purchased.add(sid)
        return True

    def buy_endow_upgrade(self, uid: str) -> bool:
        du = next((d for d in ENDOW_UPGRADES if d["id"] == uid), None)
        if not du or uid in self.endow_upgrades_purchased:
            return False
        if self.endowments < du["cost"]:
            return False
        self.endowments -= du["cost"]
        self.endow_upgrades_purchased.add(uid)
        return True

    def _queue_news(self, template: str, name: str = ""):
        msg = template.replace("{school}", self.school_name).replace("{name}", name)
        self.dynamic_news_queue.append(msg)

    # ── Events ────────────────────────────────────────────────────────────────

    def _spawn_event(self):
        weights = [EVENT_RARITY_WEIGHTS.get(e.get("rarity", "common"), 60) for e in EVENTS]
        ev = random.choices(EVENTS, weights=weights, k=1)[0].copy()
        if ev["type"] == "kp_bonus":
            ev["kp_amount"] = self.kps() * ev["value_mult"]
        elif ev["type"] == "faculty":
            owned = [b.name for b in BUILDINGS if self.building_counts[b.name] > 0]
            if not owned:
                self.event_timer = random.uniform(90, 150)
                return
            target = random.choice(owned)
            ev["target"] = target
            ev["name"]   = "Faculty Hire!"
            ev["desc"]   = f"A renowned educator joins {target}! +2% KPS permanently."
        elif ev["type"] == "strike":
            # Strike fires immediately — no "collect" needed
            self._staff_strike_active = True
            self._staff_strike_timer  = float(ev.get("duration", 60))
            self._strike_notify       = True
            self.event_timer = random.uniform(240, 480)   # strikes less frequent
            return   # don't queue as pending_event
        elif ev["type"] == "inspection_challenge":
            if not self._inspection_active:
                self.start_inspection()
            return
        self.pending_event = ev
        self.event_timer   = random.uniform(90, 150)

    def collect_event(self):
        ev = self.pending_event
        if not ev:
            return
        self._total_events_collected += 1
        self.pending_event = None
        t = ev["type"]
        if t == "kp_bonus":
            amount = ev.get("kp_amount", 0)
            self.kp          += amount
            self.total_kp    += amount
            self.all_time_kp += amount
        elif t == "merit_bonus":
            amt = int(ev["value"])
            self.merit_points += amt
        elif t == "faculty":
            bname = ev.get("target")
            if bname:
                self.faculty_bonuses[bname] = self.faculty_bonuses.get(bname, 0.0) + float(ev.get("value", 0.02))
                self._total_faculty_hires += 1
                self._check_achievements()
        elif t in ("kps_boost", "click_boost"):
            self.active_boost = {
                "type":      t,
                "value":     ev["value"],
                "remaining": ev["duration"],
                "duration":  ev["duration"],
                "name":      ev["name"],
                "rarity":    ev.get("rarity", "common"),
            }

    # ── Story ─────────────────────────────────────────────────────────────────

    def _check_story(self):
        for ch in STORY:
            if ch["id"] in self.story_shown:
                continue
            c = ch.get("check", "")
            if c == "start":
                hit = True
            elif c == "building":
                hit = self.building_counts.get(ch["target"], 0) >= ch["value"]
            elif c == "kp_total":
                hit = self.all_time_kp >= ch["value"]
            elif c == "prestige":
                hit = self.prestige_count >= ch["value"]
            elif c == "honors":
                hit = self.total_honors_earned >= ch.get("value", 1)
            elif c == "endowments":
                hit = self.total_endow_earned  >= ch.get("value", 1)
            elif c == "alumni":
                hit = self.total_alumni_earned >= ch.get("value", 1)
            elif c == "scholars_count":
                hit = len(self.scholars_purchased) >= ch.get("value", 1)
            elif c == "full_year":
                DAY_CYCLE = 60.0
                hit = self.game_time >= 365 * DAY_CYCLE
            elif c == "star_hit":
                hit = any(v >= ch.get("value", 1) for v in self.star_milestones_hit.values())
            else:
                hit = False
            if hit:
                self.story_shown.add(ch["id"])
                self.story_queue.append(ch["id"])

    # ── Milestones ────────────────────────────────────────────────────────────

    def _check_milestones(self):
        for m in MILESTONES:
            if m not in self.milestones_hit and self.all_time_kp >= m:
                self.milestones_hit.add(m)
                self.milestone_queue.append(f"{fmt(m)} Knowledge Points!")
                templates = DYNAMIC_NEWS_MILESTONE.get(str(int(m)), [])
                if templates and not self.sandbox_mode:
                    self._queue_news(random.choice(templates))

    # ── Achievements ─────────────────────────────────────────────────────────

    def _check_achievements(self):
        merit_bonus = 1 + int(
            self._skill_sum("merit_bonus") + self._honor_sum("merit_bonus"))
        for a in ACHIEVEMENTS:
            if a.id in self.achievements_unlocked:
                continue
            match a.check:
                case "kp_total":        hit = self.all_time_kp >= a.check_value
                case "clicks":          hit = self.total_clicks >= a.check_value
                case "building_count":  hit = (self.building_counts.get(a.check_target, 0) or self._zone_building_counts.get(a.check_target, 0)) >= a.check_value
                case "all_buildings":   hit = all(self.building_counts[b.name] > 0 for b in BUILDINGS)
                case "prestige":        hit = self.prestige_count >= a.check_value
                case "total_buildings": hit = sum(self.building_counts.values()) >= a.check_value
                case "combo":           hit = self.max_combo_reached >= a.check_value
                case "honors":          hit = self.total_honors_earned >= a.check_value
                case "endowments":      hit = self.total_endow_earned  >= a.check_value
                case "star_level":      hit = (max(self.star_milestones_hit.values(), default=0) >= a.check_value)
                case "scholars":        hit = len(self.scholars_purchased) >= a.check_value
                case "all_scholars":    hit = len(self.scholars_purchased) >= len(SCHOLARS)
                case "faculty_count":   hit = self._total_faculty_hires >= a.check_value
                case "daily_done":      hit = self._total_daily_done    >= a.check_value
                case "seasons_seen":    hit = len(self._seasons_seen)   >= a.check_value
                case "alumni_earned":   hit = self.total_alumni_earned  >= a.check_value
                case "research_legacy": hit = self.alumni_research_count >= a.check_value
                case "upgrades_count":  hit = len(self.upgrades_purchased) >= a.check_value
                case "events_collected":hit = self._total_events_collected >= a.check_value
                case "focus_used":      hit = self._total_focus_uses >= a.check_value
                case "diplomas":        hit = self.diplomas >= a.check_value
                case "max_single_bld":  hit = max(self.building_counts.values(), default=0) >= a.check_value
                case "quiz_tier":       hit = a.check_target in self.quiz_tiers_earned
                case "quiz_million":    hit = self.one_in_million
                case _:                 hit = False
            if hit:
                self.achievements_unlocked.add(a.id)
                reward = a.merit_reward * merit_bonus
                self.merit_points  += reward
                self.new_achievements.append(a.id)
                self.ach_toast_timer = 4.0
                if not self.sandbox_mode:
                    self._queue_news(random.choice(DYNAMIC_NEWS_ACHIEVEMENT), name=a.name)

    # ── Prestige ──────────────────────────────────────────────────────────────

    @property
    def prestige_eligible(self) -> bool:
        return self.total_kp >= 2_000_000

    @property
    def diplomas_on_prestige(self) -> int:
        # Log-based: scales with KP magnitude, can't trigger runaway feedback
        # ~8 at 2M KP, ~48 at 1B, ~80 at 1T, ~112 at 1Qa, hard cap ~200
        base  = max(1, math.floor(math.log10(max(10.0, self.total_kp / 100_000)) * 8)) + self._cw_diploma_bonus + self.quiz_perm_diploma_bonus + round(self._hero_stat("reputation") * 0.5)
        bonus = self._skill_sum("prestige_bonus")
        return max(1, math.floor(base * (1 + bonus) * self._season_diploma_mult()))

    def do_prestige(self):
        if not self.prestige_eligible:
            return
        earned = self.diplomas_on_prestige
        self.diplomas       += earned
        self.merit_points   += 2
        self.prestige_count += 1
        self._queue_news(random.choice(DYNAMIC_NEWS_PRESTIGE))
        self._first_buy_news_shown.clear()
        # Reset run-specific state
        self.kp                 = 0.0
        self.total_kp           = 0.0
        self.building_counts    = {b.name: 0 for b in BUILDINGS}
        self.upgrades_purchased = set()
        self._check_achievements()
        self.save()

    # ── Hero Creation ─────────────────────────────────────────────────────────

    def update_hero(self, dt: float):
        if self.hero is None:
            return
        self.hero.setdefault("xp", 0.0)
        self.hero.setdefault("level", 1)
        self.hero.setdefault("stat_points", 0)
        self.hero["xp"] += self.kps() * 0.0002 * dt
        while True:
            lvl = self.hero["level"]
            needed = self._hero_xp_needed(lvl)
            if self.hero["xp"] < needed:
                break
            self.hero["xp"] -= needed
            self.hero["level"] += 1
            self.hero["stat_points"] += 1
            if self.hero["level"] % 5 == 0:
                self._queue_news(
                    f"{self.hero['name']} reached Level {self.hero['level']}! "
                    f"({self.hero['stat_points']} stat point(s) to spend)"
                )

    def train_hero_stat(self, stat_key: str) -> bool:
        if self.hero is None or self.hero.get("stat_points", 0) <= 0:
            return False
        if stat_key not in self.hero.get("stats", {}):
            return False
        self.hero["stats"][stat_key] += 1
        self.hero["stat_points"] -= 1
        return True

    def can_create_hero(self) -> bool:
        return self.hero is None and self.diplomas >= HERO_CREATION_COST

    def create_hero(self, world_manager=None) -> bool:
        """Sacrifice diplomas, compute hero stats from path investment, grant Hero Academy."""
        if not self.can_create_hero():
            return False
        # Count MP spent per path
        path_mp: dict[str, int] = {p: 0 for p in HERO_PATH_STATS}
        for sk in SKILLS:
            if sk.id in self.skills_purchased and sk.path in path_mp:
                path_mp[sk.path] += sk.cost
        total_mp = max(1, sum(path_mp.values()))
        # Convert to 0-50 stat scores (proportional, capped at 50)
        stats: dict[str, int] = {}
        dominant_path = max(path_mp, key=lambda p: path_mp[p]) if total_mp > 0 else "Foundation"
        for path, (stat_key, _) in HERO_PATH_STATS.items():
            score = min(50, round(path_mp[path] / total_mp * 100))
            stats[stat_key] = score
        self.diplomas -= HERO_CREATION_COST
        self.hero = {
            "name":           f"Hero of {self.school_name}",
            "dominant_path":  dominant_path,
            "stats":          stats,
            "xp":             0.0,
            "level":          1,
            "stat_points":    0,
        }
        # Grant first Hero Academy in Zone 10
        if world_manager is not None:
            zg = world_manager.zones.get(10)
            if zg is not None:
                bname = "Hero Academy"
                zg.building_counts[bname] = zg.building_counts.get(bname, 0) + 1
        self._queue_news(f"A hero has risen from {self.school_name}! The first Hero Academy opens its doors.")
        self.save()
        return True

    # ── Offline ───────────────────────────────────────────────────────────────

    def _apply_offline(self, elapsed: float):
        self.game_time += elapsed   # advance in-game calendar through the offline period
        cap_hours = 8.0 + self._skill_sum("offline_cap") + self._dipl_sum("offline_cap_bonus")
        effective  = min(elapsed, cap_hours * 3600)
        hours      = effective / 3600
        efficiency = (0.5 + self._dipl_sum("offline_eff") + self._honor_sum("offline_eff")
                      + self._endow_sum("offline_eff")) * self._season_offline_mult()
        gained     = self.kps() * effective * efficiency
        self.kp          += gained
        self.total_kp    += gained
        self.all_time_kp += gained
        self.offline_kp_gained  = gained
        self.offline_hours      = hours
        self.offline_cap_hours  = cap_hours
        self.show_offline_popup = gained > 1.0

    # ── Save / Load ───────────────────────────────────────────────────────────

    def save(self):
        if self.sandbox_mode:
            return
        data = {
            "kp":                       self.kp,
            "total_kp":                 self.total_kp,
            "all_time_kp":              self.all_time_kp,
            "total_clicks":             self.total_clicks,
            "click_base":               self.click_base,
            "building_counts":          self.building_counts,
            "upgrades_purchased":       list(self.upgrades_purchased),
            "skills_purchased":         list(self.skills_purchased),
            "achievements_unlocked":    list(self.achievements_unlocked),
            "diplomas":                 self.diplomas,
            "merit_points":             self.merit_points,
            "prestige_count":           self.prestige_count,
            "diploma_upgrades_purchased": list(self.diploma_upgrades_purchased),
            "honors":                   self.honors,
            "total_honors_earned":      self.total_honors_earned,
            "honor_upgrades_purchased": list(self.honor_upgrades_purchased),
            "endowments":               self.endowments,
            "total_endow_earned":       self.total_endow_earned,
            "endow_upgrades_purchased": list(self.endow_upgrades_purchased),
            "alumni_points":            self.alumni_points,
            "total_alumni_earned":      self.total_alumni_earned,
            "alumni_upgrades_purchased":list(self.alumni_upgrades_purchased),
            "alumni_research_count":    self.alumni_research_count,
            "kps_samples":              self._kps_samples,
            "max_combo_reached":        self.max_combo_reached,
            "story_shown":              list(self.story_shown),
            "milestones_hit":           list(self.milestones_hit),
            "school_name":              self.school_name,
            "show_headmaster":          self.show_headmaster,
            "offline_cap_hours":        self.offline_cap_hours,
            "focus_points":             self.focus_points,
            "inspectors_done":          list(self._inspectors_done),
            "scholars_purchased":       list(self.scholars_purchased),
            "star_milestones":          self.star_milestones_hit,
            "faculty_bonuses":          self.faculty_bonuses,
            "game_time":                self.game_time,
            "daily_missions":           self.daily_missions,
            "daily_date":               self._daily_date,
            "kp_today":                 self._kp_today,
            "clicks_today":             self._clicks_today,
            "buys_today":               self._buys_today,
            "total_faculty_hires":      self._total_faculty_hires,
            "total_daily_done":         self._total_daily_done,
            "seasons_seen":             list(self._seasons_seen),
            "best_kps":                 self.best_kps,
            "best_run_kp":              self.best_run_kp,
            "total_events_collected":   self._total_events_collected,
            "total_focus_uses":         self._total_focus_uses,
            "cosmetic_theme":           self.cosmetic_theme,
            "quiz_tiers_earned":        list(self.quiz_tiers_earned),
            "quiz_perm_kps_bonus":      self.quiz_perm_kps_bonus,
            "quiz_perm_diploma_bonus":  self.quiz_perm_diploma_bonus,
            "one_in_million":           self.one_in_million,
            "hero":                     self.hero,
            "last_save":                time.time(),
        }
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
        self.last_save_time = time.time()

    def load(self):
        if not os.path.exists(SAVE_FILE):
            return
        try:
            with open(SAVE_FILE) as f:
                d = json.load(f)
            self.kp           = d.get("kp", 0.0)
            self.total_kp     = d.get("total_kp", 0.0)
            self.all_time_kp  = d.get("all_time_kp", 0.0)
            self.total_clicks = d.get("total_clicks", 0)
            self.click_base   = d.get("click_base", 1.0)
            for k, v in d.get("building_counts", {}).items():
                if k in self.building_counts:
                    self.building_counts[k] = v
            self.upgrades_purchased    = set(d.get("upgrades_purchased", []))
            self.skills_purchased      = set(d.get("skills_purchased", []))
            self.achievements_unlocked = set(d.get("achievements_unlocked", []))
            raw_diplomas        = d.get("diplomas", 0)
            self.diplomas       = min(raw_diplomas, 2000)   # cap extreme pre-fix values
            self.merit_points   = d.get("merit_points", 0)
            self.prestige_count = d.get("prestige_count", 0)
            self.diploma_upgrades_purchased = set(d.get("diploma_upgrades_purchased", []))
            self.honors                     = min(d.get("honors", 0), 500)  # cap pre-fix runaway
            self.total_honors_earned        = d.get("total_honors_earned", 0)
            self.honor_upgrades_purchased   = set(d.get("honor_upgrades_purchased", []))
            self.endowments                 = d.get("endowments", 0)
            self.total_endow_earned         = d.get("total_endow_earned", 0)
            self.endow_upgrades_purchased   = set(d.get("endow_upgrades_purchased", []))
            self.alumni_points              = d.get("alumni_points", 0)
            self.total_alumni_earned        = d.get("total_alumni_earned", 0)
            self.alumni_upgrades_purchased  = set(d.get("alumni_upgrades_purchased", []))
            self.alumni_research_count      = d.get("alumni_research_count", 0)
            self._kps_samples = [[float(s[0]), float(s[1])] for s in d.get("kps_samples", []) if len(s) == 2]
            self.max_combo_reached          = d.get("max_combo_reached", 0)
            self.story_shown                = set(d.get("story_shown", []))
            self.milestones_hit             = set(d.get("milestones_hit", []))
            self.school_name                = d.get("school_name", "Edu Empire Academy")
            self.show_headmaster            = d.get("show_headmaster", True)
            self.offline_cap_hours          = d.get("offline_cap_hours", 8.0)
            self.focus_points               = d.get("focus_points", 0.0)
            self._inspectors_done           = set(d.get("inspectors_done", []))
            self.scholars_purchased         = set(d.get("scholars_purchased", []))
            self.star_milestones_hit        = d.get("star_milestones", {})
            self.faculty_bonuses            = d.get("faculty_bonuses", {})
            self.game_time                  = d.get("game_time", 0.0)
            self.daily_missions             = d.get("daily_missions", [])
            self._daily_date                = d.get("daily_date", "")
            self._kp_today                  = d.get("kp_today", 0.0)
            self._clicks_today              = d.get("clicks_today", 0)
            self._buys_today                = d.get("buys_today", 0)
            self._total_faculty_hires       = d.get("total_faculty_hires", 0)
            self._total_daily_done          = d.get("total_daily_done", 0)
            self._seasons_seen              = set(d.get("seasons_seen", []))
            self.best_kps                   = d.get("best_kps", 0.0)
            self.best_run_kp                = d.get("best_run_kp", 0.0)
            self._total_events_collected    = d.get("total_events_collected", 0)
            self._total_focus_uses          = d.get("total_focus_uses", 0)
            self.cosmetic_theme             = d.get("cosmetic_theme", "classic")
            self.quiz_tiers_earned          = set(d.get("quiz_tiers_earned", []))
            self.quiz_perm_kps_bonus        = d.get("quiz_perm_kps_bonus", 0.0)
            self.quiz_perm_diploma_bonus    = d.get("quiz_perm_diploma_bonus", 0)
            self.one_in_million             = d.get("one_in_million", False)
            self.hero                       = d.get("hero", None)
            elapsed = time.time() - d.get("last_save", time.time())
            if elapsed > 30:
                self._apply_offline(elapsed)
        except Exception:
            pass

    def reset(self):
        self.__init__()
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)

    @property
    def session_seconds(self) -> float:
        return time.time() - self.session_start
