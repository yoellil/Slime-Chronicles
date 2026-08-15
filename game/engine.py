"""Python-owned rules for Slime Chronicles."""

from __future__ import annotations

import copy
import random
import time
from typing import Any

from .content import (
    ACTIONS,
    ALLIES,
    ASTRAL_UPGRADES,
    DARK_RITUAL,
    ENDINGS,
    FOODS,
    HERO,
    REINCARNATION_CLASSES,
    RESEARCH_COSTS,
    ROUTINES,
    SEEDS,
    SIN_EFFECTS,
    SINS,
    SKILLS,
    STORY_NODES,
    STORY_OBJECTIVES,
    ZONES,
    food_for_enemy,
    hero_public,
    recruitment_chance,
    seed_for_boss,
)


class GameError(ValueError):
    """A player-facing invalid action."""


class GameEngine:
    VERSION = 4
    MAX_LOG = 64
    MAX_PARTY = 3
    MAX_PASSIVE = 2

    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()

    def landing_state(self) -> dict[str, Any]:
        return {"started": False, "hero": hero_public(), "game_title": "Slime Chronicles"}

    def new_game(self, character_id: str = "rimuru") -> dict[str, Any]:
        if character_id not in ("", "rimuru"):
            raise GameError("The current chapter begins with Rimuru.")
        base = HERO["base"]
        now = time.time()
        state: dict[str, Any] = {
            "version": self.VERSION,
            "started": True,
            "character": "rimuru",
            "created_at": now,
            "level": 1,
            "xp": 0,
            "xp_next": self.xp_needed(1),
            "hp": base["hp"],
            "max_hp": base["hp"],
            "mana": base["mana"],
            "max_mana": base["mana"],
            "attack": base["attack"],
            "defense": base["defense"],
            "speed": base["speed"],
            "gold": 0,
            "magicules": 0,
            "research": 0,
            "insight": 0,
            "focus": 12,
            "max_focus": 21,
            "focus_recovery_seconds": 85,
            "training": {"attack": 0, "mana": 0},
            "activity": None,
            # queued actions persist in the save so players can queue multiple runs
            "action_queue": [],
            "action_counts": {action_id: 0 for action_id in ACTIONS},
            "unlocked_actions": ["gather_dew"],
            "unlocked_zones": [],
            "zone_runs": {zone_id: 0 for zone_id in ZONES},
            "max_party_slots": self.MAX_PARTY,
            "max_passive_slots": self.MAX_PASSIVE,
            "unique_skill_slots": 0,
            "ultimate_skill_slots": 0,
            "dungeon_run": None,
            "battle": None,
            "loops": {},
            "allies": {},
            "active_party": [],
            "passive_party": [],
            "friendships": {},
            "story_phase": "awakening",
            "pending_story": "inner_voice",
            "available_stories": [],
            "story_history": [],
            "branches": {},
            "total_victories": 0,
            "total_runs": 0,
            "log": [],
            # --- Your Chronicle mechanics ---
            "instant_cooldowns": {},
            "upgrade_counts": {},
            "next_actions_completed": [],
            "research_unlocks": {},
            "habit_points": 0,
            "routines": {routine_id: 0 for routine_id in ROUTINES},
            "inspiration": 0,
            "seeds": {seed_id: 0 for seed_id in SEEDS},
            "seed_bonus": {"attack": 0, "defense": 0, "max_hp": 0, "max_mana": 0},
            "ally_seeds": {},
            "foods": {food_id: 0 for food_id in FOODS},
            "gluttony_stacks": {food_id: 0 for food_id in FOODS},
            "endings": [],
            "astral_upgrades": {},
            "reincarnations": 0,
            "reincarnation_class": None,
            "sins": {},
            "prestige_multipliers": {"magicules": 1.0, "gold": 1.0, "xp": 1.0, "attack": 1.0, "hp": 1.0, "insight": 0},
        }
        self._log(state, "You awaken in darkness with no body you recognize.", "story")
        self._log(state, "A voice inside your mind is waiting for an answer.", "system")
        return state

    def _migrate(self, state: dict[str, Any]) -> None:
        """Bring an older save up to the current engine without wiping progress."""
        template = self.new_game(state.get("character", "rimuru"))
        template["log"] = state.get("log", [])
        for key, value in template.items():
            if key in ("version", "log"):
                continue
            state.setdefault(key, copy.deepcopy(value))
        for mapping in ("routines", "seeds", "foods", "gluttony_stacks", "seed_bonus"):
            for key, value in template[mapping].items():
                state[mapping].setdefault(key, value)
        state["version"] = self.VERSION
        self._log(state, "Your chronicle was rewritten to include routines, seeds, and feasts.", "system")

    @staticmethod
    def xp_needed(level: int) -> int:
        return max(16, round(16 * (level**1.5)))

    def refresh(self, state: dict[str, Any]) -> dict[str, Any]:
        if not state.get("started"):
            return self.landing_state()
        if state.get("version") != self.VERSION:
            self._migrate(state)
        activity = state.get("activity")
        if activity and time.time() >= activity["ends_at"]:
            self._complete_activity(state)
        # process any running loop actions
        self._process_loops(state)
        # recover focus over time
        self._recover_focus(state)
        # keep Max HP in sync with habit/sin/astral multipliers
        self._sync_hp_multiplier(state)
        # process instant action cooldowns
        self._process_cooldowns(state)
        self._check_story_progress(state)
        return self.public_state(state)

    def start_activity(self, state: dict[str, Any], action_id: str) -> dict[str, Any]:
        self._ensure_ready(state)
        if state.get("pending_story"):
            raise GameError("Resolve the current conversation before starting another task.")
        if state.get("activity"):
            raise GameError("Another action is already underway.")
        if state.get("dungeon_run"):
            raise GameError("Finish or abandon the current expedition first.")
        if action_id not in state["unlocked_actions"] or action_id not in ACTIONS:
            raise GameError("That action has not been discovered in this storyline.")
        action = ACTIONS[action_id]
        if action.get("party_training") and not state["active_party"]:
            raise GameError("Recruit and activate at least one ally before party training.")
        # Compute duration with a minimum based on declared difficulty so
        # actions consistently take time according to their challenge.
        duration = max(action.get("duration", 0), self._duration_from_difficulty(action.get("difficulty")))
        started = time.time()
        state["activity"] = {
            "action_id": action_id,
            "name": action["name"],
            "started_at": started,
            "ends_at": started + duration,
            "duration": duration,
        }
        self._log(state, f"Started {action['name']} ({duration} seconds).", "action")
        return self.public_state(state)

    def enqueue_action(self, state: dict[str, Any], action_id: str, count: int = 1) -> dict[str, Any]:
        """Add one or more actions to the player's persistent action queue.

        If no action is currently running, the first queued action will start immediately.
        """
        self._ensure_ready(state)
        if action_id not in ACTIONS:
            raise GameError("That action is unknown.")
        if action_id not in state.get("unlocked_actions", []):
            raise GameError("That action has not been discovered in this storyline.")
        if count < 1:
            raise GameError("Invalid queue count.")
        # append action_id count times
        for _ in range(count):
            state.setdefault("action_queue", []).append(action_id)
        self._log(state, f"Queued {count}x {ACTIONS[action_id]['name']}.", "system")
        # if nothing is running, start the next queued action now
        if not state.get("activity") and not state.get("pending_story") and not state.get("dungeon_run"):
            next_action = state["action_queue"].pop(0)
            try:
                self.start_activity(state, next_action)
            except GameError as e:
                # if starting fails, put it back on the front and report
                state.setdefault("action_queue", []).insert(0, next_action)
                self._log(state, f"Queued action could not start: {str(e)}", "system")
        return self.public_state(state)

    def cancel_activity(self, state: dict[str, Any]) -> dict[str, Any]:
        if not state.get("activity"):
            raise GameError("No timed action is running.")
        name = state["activity"]["name"]
        state["activity"] = None
        self._log(state, f"Cancelled {name}; no rewards were gained.", "system")
        return self.public_state(state)

    # ============================================================
    # Loop actions
    # ============================================================
    def start_loop(self, state: dict[str, Any], action_id: str) -> dict[str, Any]:
        self._ensure_ready(state)
        if action_id not in ACTIONS or ACTIONS[action_id].get("type") != "loop":
            raise GameError("That is not a loop action.")
        if state["level"] < ACTIONS[action_id].get("unlock_level", 1):
            raise GameError(f"Unlocks at level {ACTIONS[action_id].get('unlock_level', 1)}.")
        if state.get("pending_story"):
            raise GameError("Resolve the current conversation first.")
        if state.get("dungeon_run") and not self._has_astral(state, "doppelganger"):
            raise GameError("Finish the current expedition first, or unlock Doppelganger.")
        if state.get("activity") and not self._has_astral(state, "doppelganger"):
            raise GameError("Finish the current action first, or unlock Doppelganger.")
        if action_id in state.get("loops", {}):
            raise GameError("That loop is already running.")
        now = time.time()
        action = ACTIONS[action_id]
        state.setdefault("loops", {})[action_id] = {
            "action_id": action_id,
            "active": True,
            "started_at": now,
            "last_tick": now,
            "next_tick": now + action.get("interval", 10),
            "interval": action.get("interval", 10),
        }
        self._log(state, f"Loop started: {action['name']} runs in the background.", "action")
        return self.public_state(state)

    def stop_loop(self, state: dict[str, Any], action_id: str) -> dict[str, Any]:
        loops = state.get("loops", {})
        if action_id not in loops:
            raise GameError("That loop is not running.")
        name = ACTIONS[action_id]["name"]
        del loops[action_id]
        self._log(state, f"Stopped loop: {name}.", "system")
        return self.public_state(state)

    # ============================================================
    # Instant actions
    # ============================================================
    def perform_instant(self, state: dict[str, Any], action_id: str) -> dict[str, Any]:
        self._ensure_ready(state)
        if action_id not in ACTIONS or ACTIONS[action_id].get("type") != "instant":
            raise GameError("That is not an instant action.")
        action = ACTIONS[action_id]
        if state["level"] < action.get("unlock_level", 1):
            raise GameError(f"Unlocks at level {action.get('unlock_level', 1)}.")
        # check cooldown
        cooldowns = state.setdefault("instant_cooldowns", {})
        now = time.time()
        if action_id in cooldowns and now < cooldowns[action_id]:
            remaining = int(cooldowns[action_id] - now)
            raise GameError(f"On cooldown — {remaining}s remaining.")
        # check costs
        focus_cost = action.get("focus_cost", 0)
        gold_cost = action.get("gold_cost", 0)
        magicules_cost = action.get("magicules_cost", 0)
        if state["focus"] < focus_cost:
            raise GameError("Not enough Focus.")
        if state["gold"] < gold_cost:
            raise GameError("Not enough Gold.")
        if state["magicules"] < magicules_cost:
            raise GameError("Not enough Magicules.")
        # apply costs
        state["focus"] -= focus_cost
        state["gold"] -= gold_cost
        state["magicules"] -= magicules_cost
        # apply rewards with multipliers
        magicules = round(action.get("magicules", 0) * self._multiplier(state, "magicules"))
        gold = round(action.get("gold", 0) * self._multiplier(state, "gold"))
        insight = round(action.get("insight", 0) + self._multiplier(state, "insight"))
        xp = round(action.get("xp", 0) * self._multiplier(state, "xp"))
        state["magicules"] += magicules
        state["gold"] += gold
        state["insight"] += insight
        if xp:
            self._grant_xp(state, xp)
        # set cooldown
        cooldowns[action_id] = now + action.get("cooldown", 10)
        gains = [f"+{magicules} Magicules" if magicules else "", f"+{gold} Gold" if gold else "", f"+{insight} Insight" if insight else "", f"+{xp} XP" if xp else ""]
        self._log(state, f"{action['name']}: {', '.join(part for part in gains if part) or 'no gain'}.", "action")
        return self.public_state(state)

    # ============================================================
    # Upgrade actions
    # ============================================================
    def perform_upgrade(self, state: dict[str, Any], action_id: str) -> dict[str, Any]:
        self._ensure_ready(state)
        if action_id not in ACTIONS or ACTIONS[action_id].get("type") != "upgrade":
            raise GameError("That is not an upgrade action.")
        action = ACTIONS[action_id]
        if state["level"] < action.get("unlock_level", 1):
            raise GameError(f"Unlocks at level {action.get('unlock_level', 1)}.")
        # check costs
        for resource, cost in action.get("cost", {}).items():
            if state.get(resource, 0) < cost:
                raise GameError(f"Not enough {resource.replace('_', ' ').title()}.")
        # apply costs
        for resource, cost in action.get("cost", {}).items():
            state[resource] -= cost
        # apply effects
        for stat, amount in action.get("effect", {}).items():
            if stat == "party_slots":
                if state.get("max_party_slots", self.MAX_PARTY) >= self.MAX_PARTY + 2:
                    raise GameError("Party slots are already at maximum.")
                state["max_party_slots"] = state.get("max_party_slots", self.MAX_PARTY) + 1
            elif stat == "passive_slots":
                if state.get("max_passive_slots", self.MAX_PASSIVE) >= self.MAX_PASSIVE + 2:
                    raise GameError("Passive slots are already at maximum.")
                state["max_passive_slots"] = state.get("max_passive_slots", self.MAX_PASSIVE) + 1
            else:
                state[stat] = state.get(stat, 0) + amount
                if stat == "max_hp":
                    state["hp"] = min(state["max_hp"], state["hp"] + amount)
                if stat == "max_mana":
                    state["mana"] = min(state["max_mana"], state["mana"] + amount)
        # track upgrade count
        state.setdefault("upgrade_counts", {})[action_id] = state.get("upgrade_counts", {}).get(action_id, 0) + 1
        self._log(state, f"Upgrade complete: {action['name']}.", "growth")
        return self.public_state(state)

    # ============================================================
    # Next actions (story checkpoints)
    # ============================================================
    def perform_next(self, state: dict[str, Any], action_id: str) -> dict[str, Any]:
        self._ensure_ready(state)
        if action_id not in ACTIONS or ACTIONS[action_id].get("type") != "next":
            raise GameError("That is not a next action.")
        action = ACTIONS[action_id]
        if action_id in state.get("next_actions_completed", []):
            raise GameError("That checkpoint has already been completed.")
        # check costs
        for resource, cost in action.get("cost", {}).items():
            if state.get(resource, 0) < cost:
                raise GameError(f"Not enough {resource.replace('_', ' ').title()}.")
        # apply costs
        for resource, cost in action.get("cost", {}).items():
            state[resource] -= cost
        # mark completed
        state.setdefault("next_actions_completed", []).append(action_id)
        # advance story phase if applicable
        target_phase = action.get("story_phase")
        if target_phase and state["story_phase"] != target_phase:
            state["story_phase"] = target_phase
            self._log(state, f"STORY ADVANCED — {action['name']} completed. New chapter begins.", "story")
            if target_phase == "epilogue":
                self._record_ending(state)
        self._log(state, f"Checkpoint complete: {action['name']}.", "growth")
        self._check_story_progress(state)
        return self.public_state(state)

    # ============================================================
    # Research & Summoning
    # ============================================================
    def summon_ally(self, state: dict[str, Any], ally_id: str) -> dict[str, Any]:
        self._ensure_ready(state)
        if ally_id not in ALLIES:
            raise GameError("That creature is unknown.")
        if ally_id in state["allies"]:
            raise GameError("That creature has already joined you.")
        cost = RESEARCH_COSTS.get(ally_id)
        if not cost:
            raise GameError("That creature cannot be summoned through research.")
        if state["research"] < cost:
            raise GameError(f"Need {cost} Research to summon {ALLIES[ally_id]['name']}.")
        state["research"] -= cost
        self._grant_ally(state, ally_id, guaranteed=True)
        state.setdefault("research_unlocks", {})[ally_id] = True
        self._log(state, f"RESEARCH COMPLETE — {ALLIES[ally_id]['name']} summoned through research.", "growth")
        return self.public_state(state)

    # ============================================================
    # Prestige — Dark Ritual
    # ============================================================
    def dark_ritual(self, state: dict[str, Any]) -> dict[str, Any]:
        self._ensure_ready(state)
        if state["level"] < DARK_RITUAL["min_level"]:
            raise GameError(f"Dark Ritual requires level {DARK_RITUAL['min_level']}.")
        if state.get("activity") or state.get("dungeon_run"):
            raise GameError("Finish all activities before performing the Dark Ritual.")
        # calculate gains
        level = state["level"]
        habit_gain = level * DARK_RITUAL["habit_per_level"]
        inspiration_gain = (level // 10) * DARK_RITUAL["inspiration_per_10_levels"]
        # reset progress
        base = HERO["base"]
        state["level"] = 1
        state["xp"] = 0
        state["xp_next"] = self.xp_needed(1)
        state["hp"] = base["hp"]
        state["max_hp"] = base["hp"]
        state["mana"] = base["mana"]
        state["max_mana"] = base["mana"]
        state["attack"] = base["attack"]
        state["defense"] = base["defense"]
        state["speed"] = base["speed"]
        state["gold"] = 0
        state["magicules"] = 0
        state["research"] = 0
        state["insight"] = 0
        state["activity"] = None
        state["action_queue"] = []
        state["dungeon_run"] = None
        state["battle"] = None
        state["loops"] = {}
        state["instant_cooldowns"] = {}
        # keep allies, friendships, story progress, upgrades
        # add habit points and inspiration
        state["habit_points"] = state.get("habit_points", 0) + habit_gain
        state["inspiration"] = state.get("inspiration", 0) + inspiration_gain
        self._apply_seed_bonus(state)
        self._log(state, f"DARK RITUAL — Gained {habit_gain} Habit Points and {inspiration_gain} Inspiration.", "growth")
        return self.public_state(state)

    def buy_astral_upgrade(self, state: dict[str, Any], upgrade_id: str) -> dict[str, Any]:
        self._ensure_ready(state)
        if upgrade_id not in ASTRAL_UPGRADES:
            raise GameError("That astral upgrade is unknown.")
        upgrade = ASTRAL_UPGRADES[upgrade_id]
        current_level = state.get("astral_upgrades", {}).get(upgrade_id, 0)
        if current_level >= upgrade["max_level"]:
            raise GameError("That upgrade is already at maximum level.")
        if state["inspiration"] < upgrade["cost"]:
            raise GameError("Not enough Inspiration.")
        state["inspiration"] -= upgrade["cost"]
        state.setdefault("astral_upgrades", {})[upgrade_id] = current_level + 1
        self._log(state, f"Astral upgrade: {upgrade['name']} (level {current_level + 1}).", "growth")
        return self.public_state(state)

    # ============================================================
    # Routines & Habits
    # ============================================================
    def assign_habit(self, state: dict[str, Any], routine_id: str, points: int = 1) -> dict[str, Any]:
        self._ensure_ready(state)
        if routine_id not in ROUTINES:
            raise GameError("That routine is unknown.")
        if points < 1:
            raise GameError("Assign at least one Habit Point.")
        if state.get("habit_points", 0) < points:
            raise GameError("Not enough Habit Points.")
        state["habit_points"] -= points
        routines = state.setdefault("routines", {})
        routines[routine_id] = routines.get(routine_id, 0) + points
        self._log(state, f"Routine strengthened: {ROUTINES[routine_id]['name']} ({routines[routine_id]} Habit Points).", "growth")
        return self.public_state(state)

    def unassign_habit(self, state: dict[str, Any], routine_id: str, points: int = 1) -> dict[str, Any]:
        self._ensure_ready(state)
        if routine_id not in ROUTINES:
            raise GameError("That routine is unknown.")
        routines = state.setdefault("routines", {})
        if points < 1 or routines.get(routine_id, 0) < points:
            raise GameError("That routine does not hold that many Habit Points.")
        routines[routine_id] -= points
        state["habit_points"] = state.get("habit_points", 0) + points
        self._log(state, f"Routine relaxed: {ROUTINES[routine_id]['name']} ({routines[routine_id]} Habit Points).", "system")
        return self.public_state(state)

    # ============================================================
    # Seeds — permanent base stats
    # ============================================================
    def feed_seed(self, state: dict[str, Any], seed_id: str, target: str = "hero") -> dict[str, Any]:
        self._ensure_ready(state)
        if seed_id not in SEEDS:
            raise GameError("That seed is unknown.")
        if state.get("seeds", {}).get(seed_id, 0) < 1:
            raise GameError(f"You have no {SEEDS[seed_id]['name']}. Defeat expedition bosses to harvest them.")
        seed = SEEDS[seed_id]
        state["seeds"][seed_id] -= 1
        if target == "hero":
            bonus = state.setdefault("seed_bonus", {"attack": 0, "defense": 0, "max_hp": 0, "max_mana": 0})
            for stat, amount in seed["hero"].items():
                bonus[stat] = bonus.get(stat, 0) + amount
                state[stat] = state.get(stat, 0) + amount
                if stat == "max_hp":
                    state["hp"] = min(state["max_hp"], state["hp"] + amount)
                if stat == "max_mana":
                    state["mana"] = min(state["max_mana"], state["mana"] + amount)
            gains = ", ".join(f"+{amount} {stat.replace('_', ' ').title()}" for stat, amount in seed["hero"].items())
            self._log(state, f"You absorb a {seed['name']}: {gains}.", "growth")
            return self.public_state(state)
        if target not in state.get("allies", {}):
            state["seeds"][seed_id] += 1
            raise GameError("That creature has not joined your allies.")
        ally_seeds = state.setdefault("ally_seeds", {}).setdefault(target, {"attack": 0, "defense": 0})
        for stat, amount in seed["ally"].items():
            ally_seeds[stat] = ally_seeds.get(stat, 0) + amount
        gains = ", ".join(f"+{amount} {stat.title()}" for stat, amount in seed["ally"].items())
        self._log(state, f"{ALLIES[target]['name']} devours a {seed['name']}: {gains}.", "growth")
        return self.public_state(state)

    # ============================================================
    # Gluttony — food
    # ============================================================
    def consume_food(self, state: dict[str, Any], food_id: str, count: int = 1) -> dict[str, Any]:
        self._ensure_ready(state)
        if food_id not in FOODS:
            raise GameError("That food is unknown.")
        if "gluttony" not in state.get("sins", {}):
            raise GameError("Awaken the sin of Gluttony before devouring food.")
        available = state.get("foods", {}).get(food_id, 0)
        if count < 1 or available < count:
            raise GameError("You do not have that much food stored.")
        state["foods"][food_id] = available - count
        stacks = state.setdefault("gluttony_stacks", {})
        stacks[food_id] = stacks.get(food_id, 0) + count
        self._log(state, f"Gluttony devours {count}× {FOODS[food_id]['name']} — {stacks[food_id]} stacks held.", "growth")
        return self.public_state(state)

    # ============================================================
    # Reincarnation
    # ============================================================
    def reincarnate(self, state: dict[str, Any], class_id: str) -> dict[str, Any]:
        self._ensure_ready(state)
        if class_id not in REINCARNATION_CLASSES:
            raise GameError("That reincarnation class is unknown.")
        if state["level"] < 10:
            raise GameError("Reincarnation requires level 10.")
        if state.get("activity") or state.get("dungeon_run"):
            raise GameError("Finish all activities before reincarnating.")
        cls = REINCARNATION_CLASSES[class_id]
        reincarnations = state.get("reincarnations", 0)
        # reset everything except permanent multipliers
        base = HERO["base"]
        state["level"] = 1
        state["xp"] = 0
        state["xp_next"] = self.xp_needed(1)
        state["hp"] = base["hp"] + cls["base_bonus"].get("max_hp", 0) + cls["per_reincarnation"].get("max_hp", 0) * reincarnations
        state["max_hp"] = state["hp"]
        state["mana"] = base["mana"] + cls["base_bonus"].get("max_mana", 0) + cls["per_reincarnation"].get("max_mana", 0) * reincarnations
        state["max_mana"] = state["mana"]
        state["attack"] = base["attack"] + cls["base_bonus"].get("attack", 0) + cls["per_reincarnation"].get("attack", 0) * reincarnations
        state["defense"] = base["defense"] + cls["base_bonus"].get("defense", 0) + cls["per_reincarnation"].get("defense", 0) * reincarnations
        state["speed"] = base["speed"]
        state["gold"] = 0
        state["magicules"] = 0
        state["research"] = 0
        state["insight"] = 0
        state["activity"] = None
        state["action_queue"] = []
        state["dungeon_run"] = None
        state["battle"] = None
        state["loops"] = {}
        state["instant_cooldowns"] = {}
        state["allies"] = {}
        state["active_party"] = []
        state["passive_party"] = []
        state["friendships"] = {}
        state["reincarnations"] = reincarnations + 1
        state["reincarnation_class"] = class_id
        state["ally_seeds"] = {}
        self._apply_seed_bonus(state)
        # keep astral upgrades, habit points, routines, inspiration, story progress
        self._record_ending(state)
        # the chronicle can be told again from the beginning
        state["story_phase"] = "awakening"
        state["pending_story"] = "inner_voice"
        state["available_stories"] = []
        state["story_history"] = []
        state["branches"] = {}
        state["unlocked_actions"] = ["gather_dew"]
        state["unlocked_zones"] = []
        state["next_actions_completed"] = []
        self._log(state, f"REINCARNATION — You are reborn as a {cls['name']}. The world remembers your legend.", "story")
        return self.public_state(state)

    # ============================================================
    # Sin system
    # ============================================================
    def unlock_sin(self, state: dict[str, Any], sin_id: str) -> dict[str, Any]:
        self._ensure_ready(state)
        if sin_id not in SINS:
            raise GameError("That sin is unknown.")
        sin = SINS[sin_id]
        if state["level"] < sin["unlock_level"]:
            raise GameError(f"{sin['name']} unlocks at level {sin['unlock_level']}.")
        if sin_id in state.get("sins", {}):
            raise GameError("That sin is already unlocked.")
        state.setdefault("sins", {})[sin_id] = {"level": 1}
        self._log(state, f"SIN AWAKENED — {sin['name']}: {sin['description']}", "growth")
        return self.public_state(state)

    def level_sin(self, state: dict[str, Any], sin_id: str) -> dict[str, Any]:
        self._ensure_ready(state)
        if sin_id not in state.get("sins", {}):
            raise GameError("That sin is not unlocked.")
        cost = 10 * state["sins"][sin_id]["level"]
        if state["magicules"] < cost:
            raise GameError(f"Leveling {SINS[sin_id]['name']} costs {cost} Magicules.")
        state["magicules"] -= cost
        state["sins"][sin_id]["level"] += 1
        self._log(state, f"{SINS[sin_id]['name']} leveled to {state['sins'][sin_id]['level']}.", "growth")
        return self.public_state(state)

    def start_dungeon(self, state: dict[str, Any], zone_id: str) -> dict[str, Any]:
        self._ensure_ready(state)
        if state.get("pending_story"):
            raise GameError("Finish the current conversation first.")
        if state.get("activity") and not self._has_astral(state, "doppelganger"):
            raise GameError("Wait for the current action to finish, or unlock Doppelganger.")
        if state.get("dungeon_run"):
            raise GameError("An expedition is already in progress.")
        if zone_id not in state["unlocked_zones"] or zone_id not in ZONES:
            raise GameError("That region has not been unlocked by the story.")
        zone = ZONES[zone_id]
        state["dungeon_run"] = {
            "zone_id": zone_id,
            "zone_name": zone["name"],
            "encounter": 1,
            "total": zone["total_encounters"],
            "victories": 0,
            "recruited": [],
            "earned_gold": 0,
            "earned_magicules": 0,
        }
        self._spawn_encounter(state)
        self._log(state, f"Expedition begun: {zone['name']} — {zone['total_encounters']} encounters await.", "story")
        return self.public_state(state)

    def combat_turn(self, state: dict[str, Any], skill_id: str, target: int | None = None) -> dict[str, Any]:
        """Perform a combat turn against a chosen enemy in the encounter.

        target: optional index (0-based) of the enemy in the encounter's enemies list.
        If not provided, the first alive enemy is targeted (legacy behaviour).
        """
        self._ensure_ready(state)
        battle = state.get("battle")
        if not battle or not battle.get("enemies"):
            raise GameError("There is no enemy to attack.")
        skill = next((item for item in SKILLS if item["id"] == skill_id), None)
        if not skill or state["level"] < skill["level"]:
            raise GameError("That skill has not been unlocked.")
        if state["mana"] < skill["mana"]:
            raise GameError("Not enough Mana.")
        state["mana"] -= skill["mana"]

        enemies = battle["enemies"]
        # event queue for UI playback
        events: list[dict] = []

        # resolve target choice
        chosen = None
        chosen_idx = None
        if target is not None:
            try:
                idx = int(target)
                if idx < 0 or idx >= len(enemies):
                    raise IndexError
                cand = enemies[idx]
                if cand["hp"] <= 0:
                    raise GameError("That target is already defeated.")
                chosen = cand
                chosen_idx = idx
            except ValueError:
                chosen = next((e for e in enemies if e["name"] == str(target) and e["hp"] > 0), None)
                if not chosen:
                    raise GameError("Invalid target specified.")
                chosen_idx = enemies.index(chosen)
            except IndexError:
                raise GameError("Target index out of range.")
        else:
            chosen = next((e for e in enemies if e["hp"] > 0), None)
            chosen_idx = enemies.index(chosen) if chosen else None
        if not chosen:
            raise GameError("No hostile target remains.")

        # compute damage
        hp_before = chosen["hp"]
        execute = skill.get("execute")
        if execute and hp_before / chosen["max_hp"] <= execute:
            damage = hp_before
            state["magicules"] += 4
            verb = "devoured"
        else:
            party_attack, _ = self._party_bonuses(state)
            effective_defense = chosen["defense"] * (1 - skill.get("pierce", 0))
            variance = self.rng.randint(0, max(1, state["level"] // 3 + 1))
            attack_mult = self._multiplier(state, "attack")
            damage = max(1, round((state["attack"] * attack_mult + party_attack) * skill["power"] + variance - effective_defense))
            verb = "hit"
        hp_after = max(0, hp_before - damage)
        chosen["hp"] = hp_after

        # create skill event
        events.append({
            "id": f"evt-{int(time.time() * 1000)}-{self.rng.randint(0,9999)}",
            "type": "skill",
            "actor": "player",
            "skill": skill["id"],
            "target": chosen_idx,
            "damage": damage,
            "hp_before": hp_before,
            "hp_after": hp_after,
        })

        self._log(state, f"{skill['name']} {verb} {chosen['name']} for {damage} damage.", "combat")

        if chosen["hp"] <= 0:
            # handle per-enemy victory (xp, gold, magicules, recruitment)
            run = state.get("dungeon_run")
            recruited_before = len(run.get("recruited", [])) if run else 0
            self._win_enemy(state, chosen)
            recruited_after = len(run.get("recruited", [])) if run else 0
            # victory event
            events.append({
                "id": f"evt-{int(time.time() * 1000)}-{self.rng.randint(0,9999)}",
                "type": "defeat",
                "target": chosen_idx,
                "name": chosen.get("name"),
            })
            # recruitment event if occurred
            if recruited_after > recruited_before:
                recruited_id = run["recruited"][-1]
                events.append({
                    "id": f"evt-{int(time.time() * 1000)}-{self.rng.randint(0,9999)}",
                    "type": "recruit",
                    "ally_id": recruited_id,
                })
            # if no alive enemies remain in this encounter, advance the run
            if not any(e["hp"] > 0 for e in enemies):
                run = state["dungeon_run"]
                if run["encounter"] >= run["total"]:
                    zone_id = run["zone_id"]
                    state["zone_runs"][zone_id] += 1
                    state["total_runs"] += 1
                    self._log(state, f"EXPEDITION COMPLETE — {run['zone_name']} cleared through all {run['total']} encounters.", "story")
                    events.append({"id": f"evt-{int(time.time() * 1000)}-{self.rng.randint(0,9999)}", "type": "expedition_complete", "zone": run["zone_name"]})
                    state["dungeon_run"] = None
                    state["battle"] = None
                    self._check_story_progress(state)
                    # attach events to a transient field on state so public_state can include them
                    if state.get("battle") is None:
                        state.setdefault("last_battle_events", []).extend(events)
                    else:
                        state["battle"].setdefault("events", []).extend(events)
                    return self.public_state(state)
                # advance to next encounter
                run["encounter"] += 1
                state["hp"] = min(state["max_hp"], state["hp"] + max(3, state["max_hp"] // 5))
                state["mana"] = min(state["max_mana"], state["mana"] + max(2, state["max_mana"] // 6))
                events.append({"id": f"evt-{int(time.time() * 1000)}-{self.rng.randint(0,9999)}", "type": "encounter_advance", "next": run["encounter"]})
                self._spawn_encounter(state)
                state["battle"].setdefault("events", []).extend(events)
                return self.public_state(state)

        # enemy retaliates (first alive enemy attacks)
        attacker = next((e for e in enemies if e["hp"] > 0), None)
        if attacker:
            attacker_idx = enemies.index(attacker)
            _, party_defense = self._party_bonuses(state)
            enemy_damage = max(1, attacker["attack"] + self.rng.randint(0, 2) - state["defense"] - party_defense)
            player_hp_before = state["hp"]
            state["hp"] = max(0, state["hp"] - enemy_damage)
            player_hp_after = state["hp"]
            # advance encounter-wide turn counter
            battle["turn"] = battle.get("turn", 1) + 1
            self._log(state, f"{attacker['name']} retaliates for {enemy_damage} damage.", "danger")
            # enemy attack event
            events.append({
                "id": f"evt-{int(time.time() * 1000)}-{self.rng.randint(0,9999)}",
                "type": "attack",
                "actor": "enemy",
                "enemy_index": attacker_idx,
                "damage": enemy_damage,
                "player_hp_before": player_hp_before,
                "player_hp_after": player_hp_after,
            })
            if state["hp"] <= 0:
                run_name = state["dungeon_run"]["zone_name"]
                state["battle"] = None
                state["dungeon_run"] = None
                state["hp"] = max(1, state["max_hp"] // 2)
                state["mana"] = max(0, state["max_mana"] // 2)
                self._log(state, f"The {run_name} expedition failed. You escape with half vitality.", "danger")
                events.append({"id": f"evt-{int(time.time() * 1000)}-{self.rng.randint(0,9999)}", "type": "expedition_failed", "zone": run_name})
        # attach events to battle for client playback
        battle.setdefault("events", []).extend(events)
        return self.public_state(state)

    def abandon_dungeon(self, state: dict[str, Any]) -> dict[str, Any]:
        run = state.get("dungeon_run")
        if not run:
            raise GameError("There is no expedition to abandon.")
        name = run["zone_name"]
        state["battle"] = None
        state["dungeon_run"] = None
        self._log(state, f"You abandon the {name} expedition. Rewards already earned are kept.", "system")
        return self.public_state(state)

    def rest(self, state: dict[str, Any]) -> dict[str, Any]:
        if state.get("activity") or state.get("dungeon_run"):
            raise GameError("Rest is only available between activities and expeditions.")
        cost = max(2, state["level"] * 2)
        if state["gold"] < cost:
            raise GameError(f"A safe rest costs {cost} gold.")
        state["gold"] -= cost
        state["hp"] = state["max_hp"]
        state["mana"] = state["max_mana"]
        self._log(state, f"Rested safely for {cost} gold. Vitality and Mana restored.", "action")
        return self.public_state(state)

    def toggle_party_member(self, state: dict[str, Any], ally_id: str) -> dict[str, Any]:
        if ally_id not in state["allies"]:
            raise GameError("That creature has not joined your allies.")
        if state.get("dungeon_run"):
            raise GameError("Party formation cannot change during an expedition.")
        if ally_id in state["active_party"]:
            state["active_party"].remove(ally_id)
            self._log(state, f"{ALLIES[ally_id]['name']} leaves the active party but remains an ally.", "system")
        elif ally_id in state["passive_party"]:
            state["passive_party"].remove(ally_id)
            self._log(state, f"{ALLIES[ally_id]['name']} leaves the passive party.", "system")
        else:
            max_active = state.get("max_party_slots", self.MAX_PARTY)
            max_passive = state.get("max_passive_slots", self.MAX_PASSIVE)
            if len(state["active_party"]) < max_active:
                state["active_party"].append(ally_id)
                self._log(state, f"{ALLIES[ally_id]['name']} joins the active party.", "growth")
            elif len(state["passive_party"]) < max_passive:
                state["passive_party"].append(ally_id)
                self._log(state, f"{ALLIES[ally_id]['name']} joins the passive party.", "growth")
            else:
                raise GameError("No party slots available. Remove an ally first.")
        return self.public_state(state)

    def make_story_choice(self, state: dict[str, Any], option_id: str) -> dict[str, Any]:
        node_id = state.get("pending_story")
        if not node_id or node_id not in STORY_NODES:
            raise GameError("There is no conversation waiting for a response.")
        node = STORY_NODES[node_id]
        option = next((item for item in node["options"] if item["id"] == option_id), None)
        if not option:
            raise GameError("That response is not available.")
        for action_id in option.get("unlock_actions", []):
            self._unlock(state["unlocked_actions"], action_id)
        for zone_id in option.get("unlock_zones", []):
            self._unlock(state["unlocked_zones"], zone_id)
        for friend, amount in option.get("friendship", {}).items():
            state["friendships"][friend] = state["friendships"].get(friend, 0) + amount
        if option.get("grant_ally"):
            self._grant_ally(state, option["grant_ally"], guaranteed=True)
        state["branches"][node_id] = option["branch"]
        state["story_history"].append(
            {"node": node_id, "speaker": node["speaker"], "choice": option["label"], "reply": option["reply"]}
        )
        state["story_phase"] = node["next_phase"]
        state["pending_story"] = None
        # remove node from available_stories if present
        if "available_stories" in state and node_id in state["available_stories"]:
            try:
                state["available_stories"].remove(node_id)
            except ValueError:
                pass
        self._log(state, f"{node['speaker']}: {option['reply']}", "story")
        self._log(state, option["result"], "growth")
        self._check_story_progress(state)
        return self.public_state(state)

    def start_story(self, state: dict[str, Any], node_id: str) -> dict[str, Any]:
        """Activate an available story node so the conversation appears (manual trigger).

        The node must be discovered (in state['available_stories']) and no action must be running.
        """
        if not node_id or node_id not in STORY_NODES:
            raise GameError("That conversation is unknown.")
        if state.get("activity"):
            raise GameError("Finish the current action before starting a conversation.")
        if node_id not in state.get("available_stories", []) and state.get("pending_story") != node_id:
            raise GameError("That conversation is not available right now.")
        state["pending_story"] = node_id
        node = STORY_NODES[node_id]
        self._log(state, f"STORY STARTED — {node['title']}. A conversation opens.", "story")
        return self.public_state(state)

    def public_state(self, state: dict[str, Any]) -> dict[str, Any]:
        if not state.get("started"):
            return self.landing_state()
        data = copy.deepcopy(state)
        now = time.time()
        # Basic public meta
        data["game_title"] = "Slime Chronicles"
        data["hero"] = hero_public()
        data["character_info"] = data["hero"]
        data["story_objective"] = STORY_OBJECTIVES[state["story_phase"]]
        data["story_progress"] = self._story_progress(state)
        data["chronicle_progress"] = data["story_progress"]
        data["pending_story"] = copy.deepcopy(STORY_NODES.get(state.get("pending_story")))
        # older client expects 'pending_choice' — provide the same payload under that key
        data["pending_choice"] = copy.deepcopy(data["pending_story"])

        # Resource naming for front-end convenience
        data["resource_key"] = HERO.get("resource", "magicules")
        data["resource_label"] = HERO.get("resource_label", "Magicules")

        # Focus / UI niceties (frontend expects these keys)
        data["focus"] = state.get("focus", 12)
        data["max_focus"] = state.get("max_focus", 21)
        data["focus_recovery_seconds"] = state.get("focus_recovery_seconds", 85)
        data["alignment"] = state.get("alignment", "Unwritten")

        # Normalize unlocked actions for UI (map duration -> cost, resource field)
        normalized_actions = []
        for action_id in state.get("unlocked_actions", []):
            action = copy.deepcopy(ACTIONS[action_id])
            # map duration to a small Focus cost for the UI
            duration = action.get("duration", 6)
            action["cost"] = max(1, round(duration / 3))
            # primary resource gain (e.g., magicules)
            action["resource"] = action.get(data["resource_key"], action.get("magicules", 0))
            normalized_actions.append(action)
        data["actions"] = normalized_actions

        # Present a compact view of the persistent action queue for the UI
        queue = state.get("action_queue", []) or []
        # aggregate contiguous identical actions into counts for nicer display
        agg = []
        if queue:
            current = queue[0]
            count = 1
            for item in queue[1:]:
                if item == current:
                    count += 1
                else:
                    agg.append({"id": current, "count": count, "name": ACTIONS[current]["name"]})
                    current = item
                    count = 1
            agg.append({"id": current, "count": count, "name": ACTIONS[current]["name"]})
        data["action_queue"] = agg

        if data.get("activity"):
            data["activity"]["remaining"] = max(0, round(data["activity"]["ends_at"] - now, 1))
            elapsed = data["activity"]["duration"] - data["activity"]["remaining"]
            data["activity"]["progress"] = max(0, min(100, round(elapsed / data["activity"]["duration"] * 100)))

        data["skills"] = [
            {**copy.deepcopy(skill), "unlocked": state["level"] >= skill["level"]} for skill in SKILLS
        ]
        data["zones"] = [
            {
                "id": zone_id,
                "name": ZONES[zone_id]["name"],
                "subtitle": ZONES[zone_id]["subtitle"],
                "total_encounters": ZONES[zone_id]["total_encounters"],
                "runs": state["zone_runs"][zone_id],
                "unlocked": zone_id in state["unlocked_zones"],
                "boss": ZONES[zone_id]["boss"]["name"],
            }
            for zone_id in ZONES
        ]
        data["party"] = []
        for ally_id, progress in state["allies"].items():
            base = ALLIES[ally_id]
            level_bonus = progress["level"] - 1
            ally_seeds = state.get("ally_seeds", {}).get(ally_id, {})
            data["party"].append(
                {
                    **copy.deepcopy(base),
                    **copy.deepcopy(progress),
                    "attack": base["attack"] + level_bonus + ally_seeds.get("attack", 0),
                    "defense": base["defense"] + level_bonus // 2 + ally_seeds.get("defense", 0),
                    "seeds": copy.deepcopy(ally_seeds),
                    "active": ally_id in state["active_party"],
                    "passive": ally_id in state["passive_party"],
                }
            )
        attack_bonus, defense_bonus = self._party_bonuses(state)
        data["party_bonus"] = {"attack": attack_bonus, "defense": defense_bonus}
        if data.get("battle"):
            enemies = data["battle"].get("enemies") if isinstance(data["battle"].get("enemies"), list) else None
            if enemies:
                current = next((e for e in enemies if e.get("hp", 0) > 0), None)
                data["battle"]["current_target"] = current
                if current:
                    data["battle"]["recruit_chance"] = round(recruitment_chance(current["strength"]) * 100)
            else:
                # legacy single-enemy shape support
                strength = data["battle"].get("strength")
                if strength is not None:
                    data["battle"]["recruit_chance"] = round(recruitment_chance(strength) * 100)

        # present any discovered story nodes for the UI to list and optionally start
        data["available_stories"] = [
            {**copy.deepcopy(STORY_NODES[n]), "id": n} for n in state.get("available_stories", [])
        ]

        # --- Your Chronicle additions ---
        # Loop actions (all available loops with active status)
        data["loops"] = []
        for action_id, action in ACTIONS.items():
            if action.get("type") == "loop" and state["level"] >= action.get("unlock_level", 1):
                data["loops"].append({
                    **copy.deepcopy(action),
                    "active": action_id in state.get("loops", {}),
                })

        # Instant actions
        data["instant_actions"] = []
        for action_id, action in ACTIONS.items():
            if action.get("type") == "instant" and state["level"] >= action.get("unlock_level", 1):
                cooldown_until = state.get("instant_cooldowns", {}).get(action_id, 0)
                remaining = max(0, int(cooldown_until - now))
                data["instant_actions"].append({
                    **copy.deepcopy(action),
                    "cooldown_remaining": remaining,
                })

        # Upgrade actions
        data["upgrade_actions"] = []
        for action_id, action in ACTIONS.items():
            if action.get("type") == "upgrade" and state["level"] >= action.get("unlock_level", 1):
                data["upgrade_actions"].append({
                    **copy.deepcopy(action),
                    "purchased": state.get("upgrade_counts", {}).get(action_id, 0),
                })

        # Next actions
        data["next_actions"] = []
        for action_id, action in ACTIONS.items():
            if action.get("type") == "next":
                completed = action_id in state.get("next_actions_completed", [])
                data["next_actions"].append({
                    **copy.deepcopy(action),
                    "completed": completed,
                    "can_afford": all(state.get(res, 0) >= cost for res, cost in action.get("cost", {}).items()),
                })

        # Research & summoning
        data["research_costs"] = copy.deepcopy(RESEARCH_COSTS)
        data["summonable_allies"] = []
        for ally_id, cost in RESEARCH_COSTS.items():
            if ally_id not in state["allies"]:
                data["summonable_allies"].append({
                    "id": ally_id,
                    "name": ALLIES[ally_id]["name"],
                    "species": ALLIES[ally_id]["species"],
                    "role": ALLIES[ally_id]["role"],
                    "cost": cost,
                    "can_afford": state["research"] >= cost,
                })

        # Prestige
        data["dark_ritual"] = {
            **copy.deepcopy(DARK_RITUAL),
            "can_perform": state["level"] >= DARK_RITUAL["min_level"],
            "habit_gain": state["level"] * DARK_RITUAL["habit_per_level"],
            "inspiration_gain": (state["level"] // 10) * DARK_RITUAL["inspiration_per_10_levels"],
        }

        # Astral upgrades
        data["astral_upgrades"] = []
        for upgrade_id, upgrade in ASTRAL_UPGRADES.items():
            current_level = state.get("astral_upgrades", {}).get(upgrade_id, 0)
            data["astral_upgrades"].append({
                **copy.deepcopy(upgrade),
                "id": upgrade_id,
                "level": current_level,
                "maxed": current_level >= upgrade["max_level"],
                "can_afford": state["inspiration"] >= upgrade["cost"],
            })

        # Reincarnation
        data["reincarnation_classes"] = copy.deepcopy(REINCARNATION_CLASSES)
        data["can_reincarnate"] = state["level"] >= 10

        # Sins
        data["sins"] = []
        for sin_id, sin in SINS.items():
            unlocked = sin_id in state.get("sins", {})
            data["sins"].append({
                **copy.deepcopy(sin),
                "id": sin_id,
                "unlocked": unlocked,
                "level": state.get("sins", {}).get(sin_id, {}).get("level", 0),
                "can_unlock": state["level"] >= sin["unlock_level"],
            })

        # Sin effect summaries so the UI can explain what each sin does
        for entry in data["sins"]:
            entry["effect"] = SIN_EFFECTS.get(entry["id"], {}).get("summary", "")
            entry["level_cost"] = 10 * max(1, entry["level"])

        # Routines & Habits
        data["routines"] = [
            {
                **copy.deepcopy(routine),
                "assigned": state.get("routines", {}).get(routine_id, 0),
                "bonus": round(routine["per_point"] * state.get("routines", {}).get(routine_id, 0) * 100),
            }
            for routine_id, routine in ROUTINES.items()
        ]

        # Seeds
        data["seeds"] = [
            {
                **copy.deepcopy(seed),
                "held": state.get("seeds", {}).get(seed_id, 0),
            }
            for seed_id, seed in SEEDS.items()
        ]
        data["seed_bonus"] = copy.deepcopy(state.get("seed_bonus", {}))

        # Gluttony food
        gluttony_level = self._sin_level(state, "gluttony")
        data["foods"] = [
            {
                **copy.deepcopy(food),
                "stored": state.get("foods", {}).get(food_id, 0),
                "stacks": state.get("gluttony_stacks", {}).get(food_id, 0),
                "bonus": round(food["per_stack"] * state.get("gluttony_stacks", {}).get(food_id, 0) * gluttony_level * 100, 1),
            }
            for food_id, food in FOODS.items()
        ]
        data["gluttony_level"] = gluttony_level

        # Endings recorded across every life
        data["endings"] = [
            {**copy.deepcopy(ending), "branches": sorted(ending["branches"]), "achieved": ending_id in state.get("endings", [])}
            for ending_id, ending in ENDINGS.items()
        ]

        # Rank is the Your Chronicle name for the current level
        data["rank"] = state["level"]

        # Prestige multipliers
        data["prestige_multipliers"] = copy.deepcopy(state.get("prestige_multipliers", {}))
        data["active_multipliers"] = {
            resource: round(self._multiplier(state, resource), 3)
            for resource in ("magicules", "gold", "xp", "attack", "hp", "research")
        }

        return data

    def _complete_activity(self, state: dict[str, Any]) -> None:
        activity = state["activity"]
        action = ACTIONS[activity["action_id"]]
        action_id = action["id"]
        state["activity"] = None
        state["action_counts"][action_id] += 1
        state["magicules"] += round(action["magicules"] * self._multiplier(state, "magicules"))
        state["insight"] += action["insight"] + self._multiplier(state, "insight")
        state["hp"] = min(state["max_hp"], state["hp"] + action.get("heal", 0))
        self._grant_xp(state, round(action["xp"] * self._multiplier(state, "xp")))
        for friend, amount in action.get("friendship", {}).items():
            state["friendships"][friend] = state["friendships"].get(friend, 0) + amount
        trained = action.get("training")
        if trained:
            state["training"][trained] += 1
            if state["training"][trained] % 4 == 0:
                if trained == "attack":
                    state["attack"] += 1
                    self._log(state, "Repeated shapeshifting permanently adds 1 Attack.", "growth")
                else:
                    state["max_mana"] += 2
                    state["mana"] += 2
                    self._log(state, "Magicule circulation permanently adds 2 maximum Mana.", "growth")
        if action.get("party_training"):
            for ally_id in state["active_party"]:
                ally = state["allies"][ally_id]
                ally["bond"] += 1
                if ally["bond"] % 3 == 0:
                    ally["level"] += 1
                    self._log(state, f"{ALLIES[ally_id]['name']} reaches ally level {ally['level']}.", "growth")
        self._log(state, f"Completed {action['name']}: +{action['xp']} XP, +{action['magicules']} Magicules.", "action")
        # After completing an activity, if the player queued additional actions, start the next one automatically
        if state.get("action_queue"):
            # pop next queued action and attempt to start it, but only if no pending_story/dungeon
            try:
                if not state.get("pending_story") and not state.get("dungeon_run"):
                    next_action = state["action_queue"].pop(0)
                    # Attempt to start next action; if it fails, reinsert removed item and log
                    try:
                        self.start_activity(state, next_action)
                    except GameError as e:
                        # requeue if start failed due to validation (e.g., party training requires allies)
                        state.setdefault("action_queue", []).insert(0, next_action)
                        self._log(state, f"Queued action could not start: {str(e)}", "system")
            except Exception:
                pass

    def _process_loops(self, state: dict[str, Any]) -> None:
        """Process any active background loop actions and grant their periodic rewards.

        Loops are stored in state['loops'] as a mapping of loop_id -> loop data. Each active
        loop grants the base action's rewards every `interval` seconds. To avoid long
        processing on stale resumes, at most 10 ticks are processed per refresh.
        """
        loops = state.get("loops", {}) or {}
        if not loops:
            return
        now = time.time()
        for lid, loop in list(loops.items()):
            try:
                if not loop.get("active"):
                    continue
                action_id = loop.get("action_id")
                if not action_id or action_id not in ACTIONS:
                    continue
                action = ACTIONS[action_id]
                interval = self.loop_interval(state, loop.get("interval", action.get("interval", 10)))
                # last_tick defaults to when the loop started; fallback to now
                last = loop.get("last_tick", loop.get("started_at", now))
                next_tick = loop.get("next_tick", last + interval)
                ticks = 0
                # grant up to 10 missed ticks to prevent long stalls
                while now >= next_tick and ticks < 10:
                    # apply periodic rewards (light version of completing the action)
                    state["magicules"] += round(action.get("magicules", 0) * self._multiplier(state, "magicules"))
                    state["insight"] += action.get("insight", 0) + self._multiplier(state, "insight")
                    state["gold"] += round(action.get("gold", 0) * self._multiplier(state, "gold"))
                    state["research"] += round(action.get("research", 0) * self._multiplier(state, "research"))
                    state["hp"] = min(state.get("max_hp", 0), state.get("hp", 0) + action.get("heal", 0))
                    state["mana"] = min(state.get("max_mana", 0), state.get("mana", 0) + action.get("mana_regen", 0))
                    self._grant_xp(state, round(action.get("xp", 0) * self._multiplier(state, "xp")))
                    # record a passive completion count so story unlocks still see progress
                    state.setdefault("action_counts", {})[action_id] = state.setdefault("action_counts", {}).get(action_id, 0) + 1
                    self._log(state, f"Auto: {action['name']} produced rewards.", "action")
                    ticks += 1
                    last = next_tick
                    next_tick += interval
                loop["last_tick"] = last
                loop["next_tick"] = next_tick
            except Exception:
                # avoid any loop processing error from blocking the rest of the refresh
                continue

    def _recover_focus(self, state: dict[str, Any]) -> None:
        """Recover focus over time, including while the browser was closed."""
        now = time.time()
        last = state.get("_last_focus_tick")
        if last is None:
            state["_last_focus_tick"] = now
            return
        interval = max(1, state.get("focus_recovery_seconds", 85))
        recovered = int((now - last) / interval)
        if recovered <= 0:
            return
        # keep the remainder so partial progress toward the next point is not lost
        state["_last_focus_tick"] = last + recovered * interval
        state["focus"] = min(state.get("max_focus", 21), state.get("focus", 0) + recovered)

    def _process_cooldowns(self, state: dict[str, Any]) -> None:
        """Clean up expired instant action cooldowns."""
        now = time.time()
        cooldowns = state.get("instant_cooldowns", {})
        expired = [k for k, v in cooldowns.items() if now >= v]
        for k in expired:
            del cooldowns[k]

    def _spawn_encounter(self, state: dict[str, Any]) -> None:
        run = state["dungeon_run"]
        zone = ZONES[run["zone_id"]]
        is_boss = run["encounter"] == run["total"]
        scale = 1 + (state["zone_runs"][run["zone_id"]] * 0.08)

        if is_boss:
            enemy = copy.deepcopy(zone["boss"])
            enemy["hp"] = round(enemy["hp"] * scale)
            enemy["attack"] = round(enemy["attack"] * scale)
            enemy["defense"] = round(enemy["defense"] * scale)
            enemy["max_hp"] = enemy["hp"]
            state["battle"] = {
                "enemies": [enemy],
                "boss": True,
                "turn": 1,
                "encounter": run["encounter"],
                "total_encounters": run["total"],
            }
            self._log(
                state,
                f"Encounter {run['encounter']}/{run['total']}: {enemy['name']} — Expedition Boss.",
                "combat",
            )
            return

        pool = list(zone.get("enemies", []))
        group_size = min(max(1, self.rng.randint(1, 3)), max(1, len(pool)))
        chosen = self.rng.sample(pool, k=group_size) if len(pool) >= group_size else [self.rng.choice(pool) for _ in range(group_size)]
        enemies = []
        for item in chosen:
            e = copy.deepcopy(item)
            e["hp"] = round(e["hp"] * scale)
            e["attack"] = round(e["attack"] * scale)
            e["defense"] = round(e["defense"] * scale)
            e["max_hp"] = e["hp"]
            enemies.append(e)
        state["battle"] = {"enemies": enemies, "boss": False, "turn": 1, "encounter": run["encounter"], "total_encounters": run["total"]}
        names = ", ".join(e["name"] for e in enemies)
        self._log(state, f"Encounter {run['encounter']}/{run['total']}: a band of {len(enemies)} — {names}.", "combat")

    def _win_enemy(self, state: dict[str, Any], enemy: dict[str, Any]) -> None:
        """Process rewards and recruitment for a single defeated enemy within an encounter."""
        run = state["dungeon_run"]
        # apply rewards per-enemy
        state["gold"] += round(enemy.get("gold", 0) * self._multiplier(state, "gold"))
        state["magicules"] += round(enemy.get("magicules", 0) * self._multiplier(state, "magicules"))
        state["research"] += round(enemy.get("research", 0) * self._multiplier(state, "research"))
        run["earned_gold"] += enemy.get("gold", 0)
        run["earned_magicules"] += enemy.get("magicules", 0)
        run["victories"] += 1
        state["total_victories"] += 1
        self._grant_xp(state, round(enemy.get("xp", 0) * self._multiplier(state, "xp")))
        self._drop_food(state, enemy)
        if state.get("battle", {}).get("boss"):
            self._drop_seed(state, enemy)
        recruited = self._try_recruit(state, enemy)
        if recruited:
            run["recruited"].append(recruited)
        self._log(state, f"Victory: +{enemy.get('xp',0)} XP, +{enemy.get('gold',0)} gold, +{enemy.get('magicules',0)} Magicules, +{enemy.get('research',0)} Research.", "victory")

    def _drop_food(self, state: dict[str, Any], enemy: dict[str, Any]) -> None:
        """Defeated creatures leave food behind; Gluttony devours it immediately."""
        food_id = food_for_enemy(enemy.get("name", ""))
        if not food_id:
            return
        food = FOODS[food_id]
        if self._sin_level(state, "gluttony"):
            stacks = state.setdefault("gluttony_stacks", {})
            stacks[food_id] = stacks.get(food_id, 0) + 1
            self._log(state, f"Gluttony devours {food['name']} — {stacks[food_id]} stacks held.", "growth")
            return
        foods = state.setdefault("foods", {})
        foods[food_id] = foods.get(food_id, 0) + 1
        self._log(state, f"{food['name']} is stored away. Awaken Gluttony to devour it.", "system")

    def _drop_seed(self, state: dict[str, Any], enemy: dict[str, Any]) -> None:
        """Expedition bosses always yield a seed for permanent stat growth."""
        seed_id = seed_for_boss(enemy.get("name", ""))
        seeds = state.setdefault("seeds", {})
        seeds[seed_id] = seeds.get(seed_id, 0) + 1
        self._log(state, f"BOSS DROP — {SEEDS[seed_id]['name']} harvested from {enemy.get('name', 'the boss')}.", "victory")

    def _try_recruit(self, state: dict[str, Any], battle: dict[str, Any]) -> str | None:
        ally_id = battle.get("ally_id")
        if not ally_id or ally_id in state["allies"]:
            return None
        chance = min(0.99, recruitment_chance(battle["strength"]) + SIN_EFFECTS["lust"]["per_level"] * self._sin_level(state, "lust"))
        if self.rng.random() > chance:
            self._log(state, f"{battle['name']} retreats. Ally chance was {round(chance * 100)}%.", "system")
            return None
        self._grant_ally(state, ally_id)
        return ally_id

    def _grant_ally(self, state: dict[str, Any], ally_id: str, guaranteed: bool = False) -> None:
        if ally_id in state["allies"]:
            state["allies"][ally_id]["bond"] += 1
            return
        state["allies"][ally_id] = {"level": 1, "bond": 0, "joined_by_story": guaranteed}
        max_active = state.get("max_party_slots", self.MAX_PARTY)
        if len(state["active_party"]) < max_active:
            state["active_party"].append(ally_id)
        self._log(state, f"NEW ALLY — {ALLIES[ally_id]['name']} the {ALLIES[ally_id]['species']} joins you.", "growth")

    def _grant_xp(self, state: dict[str, Any], amount: int) -> None:
        state["xp"] += amount
        while state["xp"] >= state["xp_next"]:
            state["xp"] -= state["xp_next"]
            state["level"] += 1
            state["xp_next"] = self.xp_needed(state["level"])
            state["max_hp"] += 5
            state["max_mana"] += 2
            state["attack"] += 1
            if state["level"] % 3 == 0:
                state["defense"] += 1
            state["hp"] = state["max_hp"]
            state["mana"] = state["max_mana"]
            self._log(state, f"EVOLUTION — Level {state['level']}. New strength settles into your slime body.", "growth")

    def _check_story_progress(self, state: dict[str, Any]) -> None:
        # Do not interrupt active timed actions with new story discoveries; discoveries will be
        # considered once the player is free to start a conversation.
        if state.get("pending_story"):
            return
        if state.get("activity"):
            return
        phase = state["story_phase"]
        # small helper: nodes already seen
        completed = {entry["node"] for entry in state.get("story_history", [])}
        # Primary story progression
        # Primary story progression: add nodes to available_stories rather than forcing a popup
        def offer(node_id):
            if node_id not in state.get("available_stories", []) and node_id not in completed:
                state.setdefault("available_stories", []).append(node_id)
                node = STORY_NODES[node_id]
                self._log(state, f"STORY DISCOVERED — {node['title']}. It is available in the story panel.", "story")

        if phase == "first_steps" and sum(state["action_counts"].values()) >= 3:
            offer("distant_roar")
        elif phase == "seek_dragon" and state["zone_runs"].get("sealed_cave", 0) >= 1:
            offer("meet_veldora")
        elif phase == "learn_from_friend" and state["action_counts"].get("magicule_circulation", 0) >= 2:
            offer("goblin_encounter")
        elif phase == "protect_village" and state["zone_runs"].get("forest_road", 0) >= 1:
            offer("wolf_decision")
        elif phase == "chapter_one_complete" and state.get("total_runs", 0) >= 2:
            offer("crossroads")
        elif phase == "alliance_paths" and sum(state.get("friendships", {}).values()) >= 6:
            offer("forge_alliance")
        elif phase == "journey_to_capital" and state.get("total_victories", 0) >= 10:
            offer("capital_approach")
        elif phase == "prepare_final" and state.get("zone_runs", {}).get("lizard_marsh", 0) >= 2:
            offer("final_campaign")
        # --- New anime story phases ---
        elif phase == "dwarf_kingdom" and state.get("zone_runs", {}).get("dwargon", 0) >= 1:
            offer("meet_gazel")
        elif phase == "orc_lord_arc" and state.get("zone_runs", {}).get("orc_territory", 0) >= 1:
            offer("orc_lord_defeat")
        elif phase == "lizardmen_alliance" and state.get("zone_runs", {}).get("lizardmen_territory", 0) >= 1:
            offer("lizardmen_meeting")
        elif phase == "tempest_federation" and state.get("zone_runs", {}).get("tempest_forest", 0) >= 1:
            offer("kijin_arrival")
        elif phase == "falmuth_relations" and state.get("zone_runs", {}).get("falmuth", 0) >= 1:
            offer("falmuth_contact")
        elif phase == "farmus_invasion" and state.get("zone_runs", {}).get("falmuth", 0) >= 2:
            offer("falmuth_betrayal")
        elif phase == "demon_lord_awakening" and state.get("total_victories", 0) >= 30:
            offer("harvest_festival")
        elif phase == "walpurgis" and state.get("zone_runs", {}).get("demon_lord_domain", 0) >= 1:
            offer("clayman_defeat")
        elif phase == "harvest_festival" and state.get("total_victories", 0) >= 50:
            offer("epilogue")

        # Side quests — discovered by common play activities (add them to available_stories)
        if state.get("action_counts", {}).get("silent_scout", 0) >= 1 and "lost_lantern" not in completed:
            offer("lost_lantern")
        if state.get("action_counts", {}).get("gather_dew", 0) >= 2 and "herbalist" not in completed:
            offer("herbalist")
        if state.get("zone_runs", {}).get("forest_road", 0) >= 1 and "bridge_repair" not in completed:
            offer("bridge_repair")
        if state.get("total_victories", 0) >= 3 and "bandit_contract" not in completed:
            offer("bandit_contract")
        if state.get("gold", 0) >= 8 and "merchant_offer" not in completed:
            offer("merchant_offer")
        if state.get("action_counts", {}).get("analyze_moss", 0) >= 1 and "hidden_library" not in completed:
            offer("hidden_library")
        if state.get("zone_runs", {}).get("ancient_ruins", 0) >= 1 and "ruins_cipher" not in completed:
            offer("ruins_cipher")
        if sum(state.get("friendships", {}).values()) >= 4 and "mercenary_trial" not in completed:
            offer("mercenary_trial")
        if state.get("zone_runs", {}).get("lizard_marsh", 0) >= 1 and "pond_rescue" not in completed:
            offer("pond_rescue")
        if state.get("zone_runs", {}).get("ancient_ruins", 0) >= 2 and "ancient_relic" not in completed:
            offer("ancient_relic")
        # --- New anime side quests ---
        if state.get("zone_runs", {}).get("forest_road", 0) >= 1 and "goblin_feast" not in completed:
            offer("goblin_feast")
        if state.get("zone_runs", {}).get("dwargon", 0) >= 1 and "dwarf_weapon" not in completed:
            offer("dwarf_weapon")
        if state.get("zone_runs", {}).get("tempest_forest", 0) >= 1 and "kijin_training" not in completed:
            offer("kijin_training")
        if state.get("zone_runs", {}).get("tempest_forest", 0) >= 1 and "shion_cooking" not in completed:
            offer("shion_cooking")
        if state.get("zone_runs", {}).get("tempest_forest", 0) >= 1 and "diablo_errand" not in completed:
            offer("diablo_errand")

    @staticmethod
    def _story_progress(state: dict[str, Any]) -> int:
        base = {
            "awakening": 2,
            "first_steps": 10,
            "seek_dragon": 28,
            "learn_from_friend": 48,
            "protect_village": 66,
            "chapter_one_complete": 100,
            "alliance_paths": 22,
            "journey_to_capital": 40,
            "prepare_final": 68,
            "dwarf_kingdom": 12,
            "orc_lord_arc": 25,
            "lizardmen_alliance": 35,
            "tempest_federation": 45,
            "falmuth_relations": 55,
            "demon_lord_awakening": 65,
            "walpurgis": 75,
            "farmus_invasion": 85,
            "harvest_festival": 95,
            "epilogue": 100,
        }[state["story_phase"]]
        if state["story_phase"] == "first_steps":
            return min(24, base + sum(state["action_counts"].values()) * 4)
        if state["story_phase"] == "seek_dragon" and state.get("dungeon_run"):
            return min(46, base + state["dungeon_run"]["victories"] * 3)
        if state["story_phase"] == "learn_from_friend":
            return min(64, base + state["action_counts"]["magicule_circulation"] * 8)
        if state["story_phase"] == "protect_village" and state.get("dungeon_run"):
            return min(98, base + state["dungeon_run"]["victories"] * 5)
        if state["story_phase"] == "alliance_paths":
            return min(36, base + sum(state.get("friendships", {}).values()) * 4)
        if state["story_phase"] == "journey_to_capital" and state.get("total_victories"):
            return min(64, base + min(30, state.get("total_victories", 0) * 3))
        if state["story_phase"] == "prepare_final" and state.get("dungeon_run"):
            return min(92, base + state["dungeon_run"].get("victories", 0) * 6)
        if state["story_phase"] == "dwarf_kingdom":
            return min(22, base + state.get("zone_runs", {}).get("dwargon", 0) * 5)
        if state["story_phase"] == "orc_lord_arc":
            return min(33, base + state.get("zone_runs", {}).get("orc_territory", 0) * 8)
        if state["story_phase"] == "lizardmen_alliance":
            return min(43, base + state.get("zone_runs", {}).get("lizardmen_territory", 0) * 8)
        if state["story_phase"] == "tempest_federation":
            return min(53, base + state.get("zone_runs", {}).get("tempest_forest", 0) * 8)
        if state["story_phase"] == "falmuth_relations":
            return min(63, base + state.get("zone_runs", {}).get("falmuth", 0) * 8)
        if state["story_phase"] == "demon_lord_awakening":
            return min(73, base + min(10, state.get("total_victories", 0) // 5))
        if state["story_phase"] == "walpurgis":
            return min(83, base + state.get("zone_runs", {}).get("demon_lord_domain", 0) * 8)
        if state["story_phase"] == "farmus_invasion":
            return min(93, base + state.get("zone_runs", {}).get("falmuth", 0) * 8)
        if state["story_phase"] == "harvest_festival":
            return min(99, base + min(4, state.get("total_victories", 0) // 20))
        return base

    def _party_bonuses(self, state: dict[str, Any]) -> tuple[int, int]:
        attack = 0
        defense = 0
        for ally_id in state["active_party"]:
            if ally_id not in state["allies"]:
                continue
            base = ALLIES[ally_id]
            level = state["allies"][ally_id]["level"]
            seeds = state.get("ally_seeds", {}).get(ally_id, {})
            attack += max(1, (base["attack"] + level - 1) // 2) + seeds.get("attack", 0)
            defense += max(0, (base["defense"] + (level - 1) // 2) // 2) + seeds.get("defense", 0)
        # passive party members grant half bonuses
        for ally_id in state.get("passive_party", []):
            if ally_id not in state["allies"]:
                continue
            base = ALLIES[ally_id]
            level = state["allies"][ally_id]["level"]
            attack += max(0, (base["attack"] + level - 1) // 4)
            defense += max(0, (base["defense"] + (level - 1) // 2) // 4)
        return attack, defense

    def _sync_hp_multiplier(self, state: dict[str, Any]) -> None:
        """Fold the Max HP multiplier into the stat without compounding it."""
        applied = state.get("_hp_mult_bonus", 0)
        raw = state.get("max_hp", 0) - applied
        wanted = round(raw * self._multiplier(state, "hp")) - raw
        if wanted == applied:
            return
        state["max_hp"] = raw + wanted
        state["_hp_mult_bonus"] = wanted
        state["hp"] = min(state["max_hp"], max(1, state.get("hp", 1) + (wanted - applied)))

    def _apply_seed_bonus(self, state: dict[str, Any]) -> None:
        """Re-apply permanent seed growth after a reset rebuilds the base stats."""
        for stat, amount in state.get("seed_bonus", {}).items():
            if not amount:
                continue
            state[stat] = state.get(stat, 0) + amount
        state["hp"] = state["max_hp"]
        state["mana"] = state["max_mana"]

    def _record_ending(self, state: dict[str, Any]) -> str:
        """Write the ending this life earned, based on the branches chosen."""
        chosen = list(state.get("branches", {}).values())
        best_id = "wanderer"
        best_score = 0
        for ending_id, ending in ENDINGS.items():
            score = sum(1 for branch in chosen if branch in ending["branches"])
            if score > best_score:
                best_id, best_score = ending_id, score
        ending = ENDINGS[best_id]
        endings = state.setdefault("endings", [])
        if best_id in endings:
            self._log(state, f"ENDING — {ending['name']} is written again in the chronicle.", "story")
            return best_id
        endings.append(best_id)
        reward = ending.get("reward", {})
        state["inspiration"] = state.get("inspiration", 0) + reward.get("inspiration", 0)
        self._log(
            state,
            f"NEW ENDING — {ending['name']}: {ending['description']} (+{reward.get('inspiration', 0)} Inspiration)",
            "story",
        )
        return best_id

    @staticmethod
    def _sin_level(state: dict[str, Any], sin_id: str) -> int:
        return state.get("sins", {}).get(sin_id, {}).get("level", 0)

    def _habit_multiplier(self, state: dict[str, Any], resource: str) -> float:
        points = 0.0
        for routine_id, assigned in state.get("routines", {}).items():
            routine = ROUTINES.get(routine_id)
            if routine and routine["resource"] == resource:
                points += routine["per_point"] * assigned
        return 1 + points

    def _food_multiplier(self, state: dict[str, Any], resource: str) -> float:
        gluttony = self._sin_level(state, "gluttony")
        if not gluttony:
            return 1.0
        bonus = 0.0
        for food_id, stacks in state.get("gluttony_stacks", {}).items():
            food = FOODS.get(food_id)
            if food and food["stat"] == resource:
                bonus += food["per_stack"] * stacks * gluttony
        return 1 + bonus

    def _sin_multiplier(self, state: dict[str, Any], resource: str) -> float:
        bonus = 0.0
        for sin_id, effect in SIN_EFFECTS.items():
            if effect["kind"] != "multiplier" or effect.get("resource") != resource:
                continue
            bonus += effect["per_level"] * self._sin_level(state, sin_id)
        return 1 + bonus

    def loop_interval(self, state: dict[str, Any], interval: float) -> float:
        """Sloth makes background loops tick faster, up to 60% faster."""
        speed = min(0.6, SIN_EFFECTS["sloth"]["per_level"] * self._sin_level(state, "sloth"))
        return max(1.0, interval * (1 - speed))

    def _multiplier(self, state: dict[str, Any], resource: str) -> float:
        """Get the prestige multiplier for a resource."""
        mult = state.get("prestige_multipliers", {}).get(resource, 1.0)
        # apply astral upgrade multipliers
        astral = state.get("astral_upgrades", {})
        if resource == "magicules" and "soul_amplifier" in astral:
            mult *= 1 + ASTRAL_UPGRADES["soul_amplifier"]["per_level"] * astral["soul_amplifier"]
        if resource == "gold" and "golden_touch" in astral:
            mult *= 1 + ASTRAL_UPGRADES["golden_touch"]["per_level"] * astral["golden_touch"]
        if resource == "attack" and "predator_essence" in astral:
            mult *= 1 + ASTRAL_UPGRADES["predator_essence"]["per_level"] * astral["predator_essence"]
        if resource == "hp" and "unbreakable_slime" in astral:
            mult *= 1 + ASTRAL_UPGRADES["unbreakable_slime"]["per_level"] * astral["unbreakable_slime"]
        if resource == "insight" and "eternal_insight" in astral:
            mult += ASTRAL_UPGRADES["eternal_insight"]["per_level"] * astral["eternal_insight"]
        if resource == "insight":
            # Insight is a flat bonus rather than a multiplier.
            return mult
        return mult * self._habit_multiplier(state, resource) * self._sin_multiplier(state, resource) * self._food_multiplier(state, resource)

    def _has_astral(self, state: dict[str, Any], upgrade_id: str) -> bool:
        return state.get("astral_upgrades", {}).get(upgrade_id, 0) > 0

    @staticmethod
    def _duration_from_difficulty(difficulty: str | None) -> int:
        mapping = {
            "Simple": 3,
            "Measured": 6,
            "Demanding": 10,
            "Complex": 14,
            "Social": 7,
            "Intense": 18,
        }
        if not difficulty:
            return 6
        return mapping.get(difficulty, 8)

    @staticmethod
    def _unlock(collection: list[str], item: str) -> None:
        if item not in collection:
            collection.append(item)

    @staticmethod
    def _ensure_ready(state: dict[str, Any]) -> None:
        if not state.get("started"):
            raise GameError("Begin the slime chronicle first.")

    def _log(self, state: dict[str, Any], text: str, kind: str) -> None:
        state["log"].append({"text": text, "kind": kind, "time": int(time.time())})
        state["log"] = state["log"][-self.MAX_LOG :]