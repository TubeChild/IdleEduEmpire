"""ZoneGame + WorldManager — multi-zone idle system (zones 2-10)."""
import json
import math
import os
import random
import time

from zones_data import ZONE_DEFS, ZONE_BY_ID
from data import CW_SHOP

WORLD_SAVE = os.path.join(os.path.dirname(__file__), "world.json")

_STAR_THRESHOLDS  = [1_000, 10_000, 100_000, 1_000_000]
_STAR_LEVEL_MULTS = [1.25, 1.50, 2.00, 3.00]


def _fmt(n: float) -> str:
    if n >= 1e15: return f"{n/1e15:.2f}Qa"
    if n >= 1e12: return f"{n/1e12:.2f}T"
    if n >= 1e9:  return f"{n/1e9:.2f}B"
    if n >= 1e6:  return f"{n/1e6:.2f}M"
    if n >= 1e3:  return f"{n/1e3:.2f}K"
    return f"{n:.1f}"


class ZoneGame:
    """One zone instance (zones 2-9). Runs same KP economy as Zone 1 but zone-themed."""

    ACTIVE_CD = 180.0   # default active mechanic cooldown (seconds)

    def __init__(self, zone_id: int):
        self.zone_id  = zone_id
        self.zone_def = ZONE_BY_ID[zone_id]

        # KP economy
        self.kp           = 0.0
        self.total_kp     = 0.0     # resets on prestige
        self.all_time_kp  = 0.0
        self.total_clicks = 0
        self.click_base   = 1.0

        # Buildings
        blds = self.zone_def["buildings"]
        self.building_counts:    dict = {b["name"]: 0 for b in blds}
        self.upgrades_purchased: set  = set()
        self.star_milestones_hit: dict = {}

        # Prestige layers (l1 ≈ diplomas, l2 ≈ honors, l3 ≈ endowments, l4 ≈ alumni)
        self.prestige_count = 0   # number of zone prestiges (= l1 earns)
        self.l1 = 0    # zone-specific currency 1
        self.l2 = 0
        self.l3 = 0
        self.l4 = 0

        # Zone mechanic
        self.mechanic_value       = 0.0    # 0.0–1.0 range
        self.mechanic_active_cd   = 0.0    # seconds until active is available
        self.mechanic_active_timer = 0.0   # active boost timer (if any)
        self.mechanic_boost_mult   = 1.0   # running boost from active mechanic
        self._sin_punishment_timer = 0.0   # zone 9 punishment timer

        # Events (simplified)
        self.pending_event: dict | None = None
        self.active_boost:  dict | None = None
        self.event_timer = random.uniform(120, 200)

        # Session / save
        self._last_save = time.time()
        self._discoveries: set = set()   # for prehistoric discovery mechanic

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def buildings(self) -> list:
        return self.zone_def["buildings"]

    @property
    def upgrades(self) -> list:
        return self.zone_def["upgrades"]

    @property
    def prestige_layers(self) -> list:
        return self.zone_def["prestige_layers"]

    @property
    def zone_name(self) -> str:
        return self.zone_def["name"]

    @property
    def zone_color(self) -> tuple:
        return self.zone_def["theme_color"]

    @property
    def mechanic_def(self) -> dict:
        return self.zone_def["mechanic"]

    @property
    def l1_name(self) -> str: return self.prestige_layers[0]["name"]
    @property
    def l2_name(self) -> str: return self.prestige_layers[1]["name"]
    @property
    def l3_name(self) -> str: return self.prestige_layers[2]["name"]
    @property
    def l4_name(self) -> str: return self.prestige_layers[3]["name"]

    @property
    def prestige_eligible(self) -> bool:
        req = self.prestige_layers[0].get("prestige_kp", 2_000_000)
        return self.total_kp >= req

    @property
    def l1_on_prestige(self) -> int:
        req = self.prestige_layers[0].get("prestige_kp", 2_000_000)
        return max(1, math.floor(math.sqrt(self.total_kp / max(1, req))))

    @property
    def l2_rate(self) -> int:
        return self.prestige_layers[1].get("from_l1", 15)

    @property
    def l3_rate(self) -> int:
        return self.prestige_layers[2].get("from_l2", 5)

    @property
    def l4_rate(self) -> int:
        return self.prestige_layers[3].get("from_l3", 3)

    # ── KPS calculations ──────────────────────────────────────────────────────

    def _upgrade_mult(self, bname: str) -> float:
        mult = 1.0
        for u in self.upgrades:
            if u["id"] in self.upgrades_purchased:
                if u["target"] == bname or u["target"] == "all":
                    mult *= u["mult"]
        return mult

    def _star_mult(self, bname: str) -> float:
        level = self.star_milestones_hit.get(bname, 0)
        result = 1.0
        for i in range(level):
            result *= _STAR_LEVEL_MULTS[i]
        return result

    def building_kps(self, bname: str) -> float:
        bd  = next(b for b in self.buildings if b["name"] == bname)
        cnt = self.building_counts[bname]
        return bd["base_kps"] * cnt * self._upgrade_mult(bname) * self._star_mult(bname)

    def _global_mult(self) -> float:
        l1b = self.prestige_layers[0]["global_bonus"]
        l2b = self.prestige_layers[1]["global_bonus"]
        l3b = self.prestige_layers[2]["global_bonus"]
        l4b = self.prestige_layers[3]["global_bonus"]
        prestige_bonus = (1.0 + self.l1 * l1b) * (1.0 + self.l2 * l2b) * \
                         (1.0 + self.l3 * l3b) * (1.0 + self.l4 * l4b)
        return prestige_bonus * self._mechanic_mult()

    def _mechanic_mult(self) -> float:
        m   = self.zone_def["mechanic"]
        val = self.mechanic_value   # 0.0–1.0
        if m["inverted"]:
            base = 1.0 - val * m["max_effect"]
        else:
            base = 1.0 + val * m["max_effect"]
        # Zone 9 sin punishment
        if self.zone_id == 9 and self._sin_punishment_timer > 0:
            base *= 0.5
        return max(0.05, base) * self.mechanic_boost_mult

    def kps(self) -> float:
        raw = sum(self.building_kps(b["name"]) for b in self.buildings)
        if self.active_boost:
            raw *= self.active_boost["value"]
        return raw * self._global_mult()

    @property
    def click_power(self) -> float:
        return self.click_base * (1.0 + self.prestige_count * 0.05)

    # ── Building costs ────────────────────────────────────────────────────────

    def _cost_at(self, bname: str, n: int) -> float:
        bd   = next(b for b in self.buildings if b["name"] == bname)
        return max(1.0, bd["base_cost"] * (1.15 ** n))

    def building_cost(self, bname: str) -> float:
        return self._cost_at(bname, self.building_counts[bname])

    def building_cost_n(self, bname: str, n: int) -> float:
        cur = self.building_counts[bname]
        return sum(self._cost_at(bname, cur + i) for i in range(n))

    def building_max_buyable(self, bname: str) -> int:
        n, total, cur = 0, 0.0, self.building_counts[bname]
        while True:
            c = self._cost_at(bname, cur + n)
            if total + c > self.kp or n >= 10_000:
                break
            total += c
            n += 1
        return n

    def upgrade_cost(self, uid: str) -> float:
        u = next((x for x in self.upgrades if x["id"] == uid), None)
        return float(u["cost"]) if u else 1e30

    # ── Star milestones ───────────────────────────────────────────────────────

    def _check_star(self):
        for b in self.buildings:
            cnt = self.building_counts[b["name"]]
            cur = self.star_milestones_hit.get(b["name"], 0)
            for level, threshold in enumerate(_STAR_THRESHOLDS, 1):
                if cnt >= threshold and cur < level:
                    self.star_milestones_hit[b["name"]] = level

    # ── Purchases ─────────────────────────────────────────────────────────────

    def buy_building(self, bname: str) -> bool:
        cost = self.building_cost(bname)
        if self.kp < cost:
            return False
        first = self.building_counts[bname] == 0
        self.kp -= cost
        self.building_counts[bname] += 1
        if first:
            self._discoveries.add(bname)
        self._check_star()
        return True

    def buy_building_n(self, bname: str, n: int) -> bool:
        if n <= 0: return False
        cost = self.building_cost_n(bname, n)
        if self.kp < cost: return False
        first = self.building_counts[bname] == 0
        self.kp -= cost
        self.building_counts[bname] += n
        if first:
            self._discoveries.add(bname)
        self._check_star()
        return True

    def buy_upgrade(self, uid: str) -> bool:
        cost = self.upgrade_cost(uid)
        if uid in self.upgrades_purchased or self.kp < cost:
            return False
        self.kp -= cost
        self.upgrades_purchased.add(uid)
        return True

    def click(self) -> float:
        gained = self.click_power
        self.kp          += gained
        self.total_kp    += gained
        self.all_time_kp += gained
        self.total_clicks += 1
        return gained

    # ── Prestige ──────────────────────────────────────────────────────────────

    def do_prestige(self):
        if not self.prestige_eligible:
            return
        earned = self.l1_on_prestige
        self.l1            += earned
        self.prestige_count += 1
        self.kp                 = 0.0
        self.total_kp           = 0.0
        self.building_counts    = {b["name"]: 0 for b in self.buildings}
        self.upgrades_purchased = set()

    def convert_to_l2(self) -> bool:
        if self.l1 < self.l2_rate:
            return False
        self.l1 -= self.l2_rate
        self.l2 += 1
        return True

    def convert_to_l3(self) -> bool:
        if self.l2 < self.l3_rate:
            return False
        self.l2 -= self.l3_rate
        self.l3 += 1
        return True

    def convert_to_l4(self) -> bool:
        if self.l3 < self.l4_rate:
            return False
        self.l3 -= self.l4_rate
        self.l4 += 1
        return True

    # ── Zone mechanic ─────────────────────────────────────────────────────────

    def can_active(self) -> bool:
        m = self.mechanic_def
        if self.mechanic_active_cd > 0:
            return False
        if m["active_cost_layer"] == 1 and self.l1 < m["active_cost"]:
            return False
        if m["active_effect"] == "spend_mana_burst" and self.mechanic_value < 0.1:
            return False
        return True

    def do_active_mechanic(self) -> bool:
        if not self.can_active():
            return False
        m = self.mechanic_def
        effect = m["active_effect"]

        if m["active_cost_layer"] == 1 and m["active_cost"] > 0:
            self.l1 -= m["active_cost"]

        if effect == "empty":
            self.mechanic_value = 0.0
            self.mechanic_boost_mult = 1.5
            self.mechanic_active_timer = 30.0
            self.mechanic_active_cd = self.ACTIVE_CD

        elif effect == "kps_boost":
            self.mechanic_boost_mult = 2.0
            self.mechanic_active_timer = 30.0
            self.mechanic_active_cd = self.ACTIVE_CD

        elif effect in ("kp_burst", "kp_burst_5m", "kp_burst_10m"):
            secs = {"kp_burst": 60.0, "kp_burst_5m": 300.0, "kp_burst_10m": 600.0}[effect]
            gained = self.kps() * secs
            self.kp += gained; self.total_kp += gained; self.all_time_kp += gained
            self.mechanic_active_cd = self.ACTIVE_CD

        elif effect == "spend_mana_burst":
            secs = 300.0 * self.mechanic_value   # proportional to mana
            gained = self.kps() * secs
            self.kp += gained; self.total_kp += gained; self.all_time_kp += gained
            self.mechanic_value = 0.0
            self.mechanic_active_cd = 0.0        # mana-gated, not cooldown-gated

        elif effect == "rng_miracle":
            if random.random() < 0.75:
                self.mechanic_boost_mult = 3.0
                self.mechanic_active_timer = 20.0
            else:
                self.l1 += 1
            self.mechanic_active_cd = 90.0

        elif effect == "sin_boost":
            self.mechanic_value = min(1.0, self.mechanic_value + 0.25)
            self.mechanic_boost_mult = 2.0
            self.mechanic_active_timer = 30.0
            self.mechanic_active_cd = self.ACTIVE_CD

        return True

    def _passive_mechanic(self, dt: float):
        m = self.mechanic_def
        self.mechanic_value = max(0.0, min(1.0, self.mechanic_value + m["fill_rate"] * dt))

        # Zone 9: sin punishment chance
        if self.zone_id == 9 and self._sin_punishment_timer <= 0:
            sin_chance = self.mechanic_value * 0.01 * dt   # up to 1% per second at max sin
            if random.random() < sin_chance:
                self._sin_punishment_timer = 15.0

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float):
        gained = self.kps() * dt
        self.kp          += gained
        self.total_kp    += gained
        self.all_time_kp += gained

        self._passive_mechanic(dt)

        if self.mechanic_active_cd > 0:
            self.mechanic_active_cd = max(0.0, self.mechanic_active_cd - dt)
        if self.mechanic_active_timer > 0:
            self.mechanic_active_timer = max(0.0, self.mechanic_active_timer - dt)
            if self.mechanic_active_timer <= 0:
                self.mechanic_boost_mult = 1.0
        if self._sin_punishment_timer > 0:
            self._sin_punishment_timer = max(0.0, self._sin_punishment_timer - dt)

        if self.active_boost:
            self.active_boost["remaining"] -= dt
            if self.active_boost["remaining"] <= 0:
                self.active_boost = None

        if self.pending_event is None and self.active_boost is None:
            self.event_timer -= dt
            if self.event_timer <= 0:
                self._spawn_event()

    def _spawn_event(self):
        events = [
            {"name": "Inspired Student!",   "desc": "+2 min KP bonus",
             "type": "kp_bonus", "value_mult": 120},
            {"name": "Guest Lecturer!",      "desc": "+3 min KPS boost for 60s",
             "type": "kps_boost", "value": 2.0, "duration": 60},
            {"name": f"{self.zone_name} Grant!","desc": f"+1 {self.l1_name}",
             "type": "l1_bonus", "value": 1},
        ]
        ev = random.choice(events).copy()
        if ev["type"] == "kp_bonus":
            ev["kp_amount"] = self.kps() * ev["value_mult"]
        self.pending_event = ev
        self.event_timer   = random.uniform(120, 200)

    def collect_event(self):
        ev = self.pending_event
        if not ev: return
        self.pending_event = None
        t = ev["type"]
        if t == "kp_bonus":
            a = ev.get("kp_amount", 0)
            self.kp += a; self.total_kp += a; self.all_time_kp += a
        elif t == "kps_boost":
            self.active_boost = {
                "type": "kps_boost", "value": ev["value"],
                "remaining": ev["duration"], "duration": ev["duration"],
            }
        elif t == "l1_bonus":
            self.l1 += int(ev["value"])

    # ── Save / load ───────────────────────────────────────────────────────────

    def save_data(self) -> dict:
        return {
            "kp": self.kp, "total_kp": self.total_kp, "all_time_kp": self.all_time_kp,
            "total_clicks": self.total_clicks, "click_base": self.click_base,
            "building_counts": self.building_counts,
            "upgrades_purchased": list(self.upgrades_purchased),
            "star_milestones_hit": self.star_milestones_hit,
            "prestige_count": self.prestige_count,
            "l1": self.l1, "l2": self.l2, "l3": self.l3, "l4": self.l4,
            "mechanic_value": self.mechanic_value,
            "mechanic_active_cd": self.mechanic_active_cd,
            "discoveries": list(self._discoveries),
        }

    def load_data(self, d: dict):
        self.kp           = d.get("kp", 0.0)
        self.total_kp     = d.get("total_kp", 0.0)
        self.all_time_kp  = d.get("all_time_kp", 0.0)
        self.total_clicks = d.get("total_clicks", 0)
        self.click_base   = d.get("click_base", 1.0)
        for k, v in d.get("building_counts", {}).items():
            if k in self.building_counts:
                self.building_counts[k] = v
        self.upgrades_purchased  = set(d.get("upgrades_purchased", []))
        self.star_milestones_hit = d.get("star_milestones_hit", {})
        self.prestige_count      = d.get("prestige_count", 0)
        self.l1 = d.get("l1", 0)
        self.l2 = d.get("l2", 0)
        self.l3 = d.get("l3", 0)
        self.l4 = d.get("l4", 0)
        self.mechanic_value     = d.get("mechanic_value", 0.0)
        self.mechanic_active_cd = d.get("mechanic_active_cd", 0.0)
        self._discoveries       = set(d.get("discoveries", []))


# ── WorldManager ──────────────────────────────────────────────────────────────

class WorldManager:
    """Manages all zones (2-9), Cosmic Wisdom currency, and zone unlocking."""

    # Cosmic Wisdom awards
    CW_PER_PRESTIGE  = 1
    CW_PER_L2        = 5
    CW_PER_L3        = 15
    CW_PER_L4        = 50

    def __init__(self):
        self.zones: dict[int, ZoneGame] = {z["id"]: ZoneGame(z["id"]) for z in ZONE_DEFS}
        self.cosmic_wisdom       = 0
        self.total_cw_earned     = 0
        self.cw_purchased: set = set()   # set of CW_SHOP item ids
        # Initialize prev-counters to 0 so first prestige/conversion awards CW correctly
        self._prev_prestiges: dict[int, int] = {zid: 0 for zid in self.zones}
        self._prev_l2: dict[int, int]        = {zid: 0 for zid in self.zones}
        self._prev_l3: dict[int, int]        = {zid: 0 for zid in self.zones}
        self._prev_l4: dict[int, int]        = {zid: 0 for zid in self.zones}
        self.load()

    # ── Unlock logic ──────────────────────────────────────────────────────────

    def is_unlocked(self, zone_id: int, zone1_game) -> bool:
        z = ZONE_BY_ID[zone_id]
        req = z["unlock"]
        if req["zone"] == 1:
            if req["type"] == "prestige":
                return zone1_game.prestige_count >= req["value"]
            elif req["type"] == "alumni":
                return zone1_game.total_alumni_earned >= req["value"]
        else:
            src_zone = self.zones.get(req["zone"])
            if src_zone is None:
                return False
            if req["type"] == "prestige":
                return src_zone.prestige_count >= req["value"]
            elif req["type"] == "alumni":
                return src_zone.l4 >= req["value"]
        return False

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float, zone1_game) -> int:
        """Update all unlocked zones. Returns CW earned this tick."""
        cw_gained = 0
        for zid, zg in self.zones.items():
            if not self.is_unlocked(zid, zone1_game):
                continue
            zg.update(dt)
            # Award CW for prestige progress
            prev_p = self._prev_prestiges.get(zid, zg.prestige_count)
            if zg.prestige_count > prev_p:
                cw_gained += (zg.prestige_count - prev_p) * self.CW_PER_PRESTIGE
                self._prev_prestiges[zid] = zg.prestige_count
            prev_l2 = self._prev_l2.get(zid, zg.l2)
            if zg.l2 > prev_l2:
                cw_gained += (zg.l2 - prev_l2) * self.CW_PER_L2
                self._prev_l2[zid] = zg.l2
            prev_l3 = self._prev_l3.get(zid, zg.l3)
            if zg.l3 > prev_l3:
                cw_gained += (zg.l3 - prev_l3) * self.CW_PER_L3
                self._prev_l3[zid] = zg.l3
            prev_l4 = self._prev_l4.get(zid, zg.l4)
            if zg.l4 > prev_l4:
                cw_gained += (zg.l4 - prev_l4) * self.CW_PER_L4
                self._prev_l4[zid] = zg.l4

        if cw_gained:
            self.cosmic_wisdom   += cw_gained
            self.total_cw_earned += cw_gained
        return cw_gained

    def all_zone_building_counts(self) -> dict:
        """Merged building_counts across all zone games (zones 2-10)."""
        merged: dict = {}
        for zg in self.zones.values():
            for bname, cnt in zg.building_counts.items():
                merged[bname] = merged.get(bname, 0) + cnt
        return merged

    # ── CW Shop ───────────────────────────────────────────────────────────────

    def buy_cw_upgrade(self, uid: str) -> bool:
        """Purchase a CW shop item. Returns True if purchase succeeded."""
        item = next((x for x in CW_SHOP if x["id"] == uid), None)
        if item is None or uid in self.cw_purchased:
            return False
        req = item.get("req")
        if req and req not in self.cw_purchased:
            return False
        if self.cosmic_wisdom < item["cost"]:
            return False
        self.cosmic_wisdom -= item["cost"]
        self.cw_purchased.add(uid)
        return True

    def cross_zone_mult(self) -> float:
        """Product of all zone_global_mult CW upgrades purchased."""
        mult = 1.0
        for item in CW_SHOP:
            if item["effect"] == "zone_global_mult" and item["id"] in self.cw_purchased:
                mult *= item["value"]
        return mult

    def zone1_diploma_bonus(self) -> int:
        """Sum of zone1_diploma_bonus CW upgrades purchased."""
        return sum(item["value"] for item in CW_SHOP
                   if item["effect"] == "zone1_diploma_bonus"
                   and item["id"] in self.cw_purchased)

    def zone1_click_mult(self) -> float:
        """Product of zone1_click_mult CW upgrades purchased."""
        mult = 1.0
        for item in CW_SHOP:
            if item["effect"] == "zone1_click_mult" and item["id"] in self.cw_purchased:
                mult *= item["value"]
        return mult

    def cosmetic_unlocked(self, cosmetic_id: str) -> bool:
        """True if the given cosmetic CW upgrade has been purchased."""
        req_item = next((x for x in CW_SHOP
                         if x["effect"] == "cosmetic" and x["value"] == cosmetic_id), None)
        if req_item is None:
            return False
        return req_item["id"] in self.cw_purchased

    # ── Save / load ───────────────────────────────────────────────────────────

    def save(self):
        data = {
            "cosmic_wisdom":   self.cosmic_wisdom,
            "total_cw_earned": self.total_cw_earned,
            "cw_purchased":    list(self.cw_purchased),
            "zones": {str(zid): zg.save_data() for zid, zg in self.zones.items()},
        }
        with open(WORLD_SAVE, "w") as f:
            json.dump(data, f, indent=2)

    def load(self):
        if not os.path.exists(WORLD_SAVE):
            return
        try:
            with open(WORLD_SAVE) as f:
                d = json.load(f)
            self.cosmic_wisdom   = d.get("cosmic_wisdom", 0)
            self.total_cw_earned = d.get("total_cw_earned", 0)
            self.cw_purchased    = set(d.get("cw_purchased", []))
            zones_data = d.get("zones", {})
            for zid, zg in self.zones.items():
                zd = zones_data.get(str(zid))
                if zd:
                    zg.load_data(zd)
            # Init prev-counters from loaded state
            for zid, zg in self.zones.items():
                self._prev_prestiges[zid] = zg.prestige_count
                self._prev_l2[zid] = zg.l2
                self._prev_l3[zid] = zg.l3
                self._prev_l4[zid] = zg.l4
        except Exception:
            pass

    # ── Total cross-zone KPS (for display) ───────────────────────────────────

    def total_kps(self, zone1_game) -> float:
        total = sum(
            zg.kps()
            for zid, zg in self.zones.items()
            if self.is_unlocked(zid, zone1_game)
        )
        return total
