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
    HABIT_BONUS,
    HERO,
    PATHS,
    PATH_TRIGGERS,
    PHASE_ORDER,
    PHASE_UNLOCKS,
    REINCARNATION_CLASSES,
    RESEARCH_COSTS,
    SINS,
    SKILLS,
    STORY_NODES,
    STORY_OBJECTIVES,
    ZONES,
    hero_public,
    recruitment_chance,
)


class GameError(ValueError):
    """A player-facing invalid action."""


class GameEngine:
    VERSION = 3
    MAX_LOG = 64
    MAX_PARTY = 3
    MAX_PASSIVE = 2
    MAX_CATCH_UP = 120  # tasks completed per refresh when you return after a long absence
    MAX_LOOP_TICKS = 300
    _chain_at: float | None = None

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
            "auto_action": None,
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
            "inspiration": 0,
            "traits": {key: 0 for key in PATHS},
            "flags": [],
            "astral_upgrades": {},
            "reincarnations": 0,
            "reincarnation_class": None,
            "sins": {},
            "prestige_multipliers": {"magicules": 1.0, "gold": 1.0, "xp": 1.0, "attack": 1.0, "hp": 1.0, "insight": 0},
        }
        self._log(state, "You awaken in darkness with no body you recognize.", "story")
        self._log(state, "A voice inside your mind is waiting for an answer.", "system")
        return state

    @staticmethod
    def xp_needed(level: int) -> int:
        return max(16, round(16 * (level**1.5)))

    def refresh(self, state: dict[str, Any]) -> dict[str, Any]:
        if not state.get("started"):
            return self.landing_state()
        if state.get("version") != self.VERSION:
            replacement = self.new_game()
            replacement["log"].append(
                {"text": "Your earlier save was reshaped for the new Rimuru-only story.", "kind": "system", "time": int(time.time())}
            )
            state.clear()
            state.update(replacement)
        # recover focus over time first, so a repeating task can spend it while you were away
        self._recover_focus(state)
        # finish tasks that ended while you were away; queued and repeating tasks chain from where the last one ended
        for _ in range(self.MAX_CATCH_UP):
            activity = state.get("activity")
            if not activity or time.time() < activity["ends_at"]:
                break
            self._chain_at = activity["ends_at"]
            try:
                self._complete_activity(state)
                self._resume_queue(state)
            finally:
                self._chain_at = None
        # process any running loop actions
        self._process_loops(state)
        # process instant action cooldowns
        self._process_cooldowns(state)
        self._resume_queue(state)
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
        cost_type, cost, duration = self._task_cost(action)
        if state[cost_type] < cost:
            hint = " Loops such as Rest bring Mana back." if cost_type == "mana" else ""
            raise GameError(f"Not enough {cost_type.title()}. Need {cost}, have {state[cost_type]}.{hint}")
        state[cost_type] -= cost
        started = self._chain_at or time.time()
        state["activity"] = {
            "action_id": action_id,
            "name": action["name"],
            "started_at": started,
            "ends_at": started + duration,
            "duration": duration,
            "cost_type": cost_type,
            "cost": cost,
        }
        self._log(state, f"Started {action['name']} ({duration} seconds), spent {cost} {cost_type.title()}.", "action")
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
            try:
                next_action = state["action_queue"].pop(0)
                self.start_activity(state, next_action)
            except GameError as e:
                # if starting fails, put it back on the front and report
                state.setdefault("action_queue", []).insert(0, next_action)
                self._log(state, f"Queued action could not start: {str(e)}", "system")
        return self.public_state(state)

    def toggle_auto_action(self, state: dict[str, Any], action_id: str) -> dict[str, Any]:
        """Repeat a timed action by itself whenever you are idle and can pay for it."""
        self._ensure_ready(state)
        if state.get("auto_action") == action_id:
            state["auto_action"] = None
            self._log(state, f"Auto-repeat off: {ACTIONS[action_id]['name']}.", "system")
        else:
            if action_id not in state["unlocked_actions"] or ACTIONS.get(action_id, {}).get("type") != "timed":
                raise GameError("That action has not been discovered in this storyline.")
            state["auto_action"] = action_id
            self._log(state, f"Auto-repeat on: {ACTIONS[action_id]['name']}.", "system")
            self._resume_queue(state)
        return self.public_state(state)

    def cancel_activity(self, state: dict[str, Any]) -> dict[str, Any]:
        if not state.get("activity"):
            raise GameError("No timed action is running.")
        if state.get("auto_action") == state["activity"]["action_id"]:
            state["auto_action"] = None
        self._drop_activity(state, "Cancelled")
        return self.public_state(state)

    def _drop_activity(self, state: dict[str, Any], verb: str) -> None:
        """Stop the running task and give back what it cost, since no rewards were gained."""
        activity = state["activity"]
        cost_type, cost, _ = self._task_cost(ACTIONS[activity["action_id"]])
        cost_type = activity.get("cost_type", cost_type)
        cost = activity.get("cost", cost)
        cap = state.get("max_mana" if cost_type == "mana" else "max_focus", 21)
        state[cost_type] = min(cap, state[cost_type] + cost)
        state["activity"] = None
        self._log(state, f"{verb} {activity['name']}; {cost} {cost_type.title()} refunded.", "system")

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
        insight = action.get("insight", 0) + self._multiplier(state, "insight")
        xp = round(action.get("xp", 0) * self._multiplier(state, "xp"))
        state["magicules"] += magicules
        state["gold"] += gold
        state["insight"] += insight
        if xp:
            self._grant_xp(state, xp)
        # set cooldown
        self._add_traits(state, action.get("traits"))
        cooldowns[action_id] = now + action.get("cooldown", 10)
        self._log(state, f"{action['name']}: +{magicules} Magicules, +{gold} Gold, +{insight} Insight.", "action")
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
        effect = action.get("effect", {})
        if "party_slots" in effect and state.get("max_party_slots", self.MAX_PARTY) >= self.MAX_PARTY + 2:
            raise GameError("Party slots are already at maximum.")
        if "passive_slots" in effect and state.get("max_passive_slots", self.MAX_PASSIVE) >= self.MAX_PASSIVE + 2:
            raise GameError("Passive slots are already at maximum.")
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
                state["max_party_slots"] = state.get("max_party_slots", self.MAX_PARTY) + 1
            elif stat == "passive_slots":
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
        if state["level"] < action.get("unlock_level", 1):
            raise GameError(f"Unlocks at level {action.get('unlock_level', 1)}.")
        target_phase = action.get("story_phase")
        if target_phase and self._phase_index(target_phase) <= self._phase_index(state["story_phase"]):
            raise GameError("The story has already moved past this checkpoint.")
        upcoming = sorted(
            (aid for aid, a in ACTIONS.items()
             if a.get("type") == "next" and aid not in state.get("next_actions_completed", [])
             and self._phase_index(a.get("story_phase", "")) > self._phase_index(state["story_phase"])),
            key=lambda aid: self._phase_index(ACTIONS[aid]["story_phase"]),
        )
        if upcoming and upcoming[0] != action_id:
            raise GameError(f"Complete “{ACTIONS[upcoming[0]]['name']}” first.")
        # check costs
        for resource, cost in action.get("cost", {}).items():
            if state.get(resource, 0) < cost:
                raise GameError(f"Not enough {resource.replace('_', ' ').title()}.")
        # apply costs
        for resource, cost in action.get("cost", {}).items():
            state[resource] -= cost
        # mark completed
        state.setdefault("next_actions_completed", []).append(action_id)
        if target_phase:
            state["story_phase"] = target_phase
            unlocks = PHASE_UNLOCKS.get(target_phase, {})
            for zone_id in unlocks.get("zones", []):
                self._unlock(state["unlocked_zones"], zone_id)
            for unlocked_action in unlocks.get("actions", []):
                self._unlock(state["unlocked_actions"], unlocked_action)
            self._log(state, f"STORY ADVANCED — {action['name']} completed. New chapter begins.", "story")
        self._log(state, f"Checkpoint complete: {action['name']}.", "growth")
        self._check_story_progress(state)
        return self.public_state(state)

    @staticmethod
    def _phase_index(phase: str) -> int:
        return PHASE_ORDER.index(phase) if phase in PHASE_ORDER else -1

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
        state["auto_action"] = None
        state["dungeon_run"] = None
        state["battle"] = None
        state["loops"] = {}
        state["instant_cooldowns"] = {}
        # keep allies, friendships, story progress, upgrades
        # add habit points and inspiration
        state["habit_points"] = state.get("habit_points", 0) + habit_gain
        state["inspiration"] = state.get("inspiration", 0) + inspiration_gain
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
        state["auto_action"] = None
        state["allies"] = {}
        state["active_party"] = []
        state["passive_party"] = []
        state["friendships"] = {}
        state["reincarnations"] = reincarnations + 1
        state["reincarnation_class"] = class_id
        # keep astral upgrades, habit points, inspiration, story progress
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
        if state.get("dungeon_run"):
            raise GameError("An expedition is already in progress.")
        if state.get("activity") and not self._has_astral(state, "doppelganger"):
            self._drop_activity(state, "Paused")  # repeats and the queue pick up again after the dungeon
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
        state["last_battle_events"] = []

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
                    state["last_run"] = dict(run)
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
            enemy_damage = max(1, round((attacker["attack"] + self.rng.randint(0, 2) - state["defense"] - party_defense) / self._multiplier(state, "hp")))
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
                state["last_run"] = dict(state["dungeon_run"])
                state["battle"] = None
                state["dungeon_run"] = None
                state["hp"] = max(1, state["max_hp"] // 2)
                state["mana"] = max(0, state["max_mana"] // 2)
                self._log(state, f"The {run_name} expedition failed. You escape with half vitality.", "danger")
                events.append({"id": f"evt-{int(time.time() * 1000)}-{self.rng.randint(0,9999)}", "type": "expedition_failed", "zone": run_name})
        # attach events to battle for client playback (battle may have just ended)
        if state.get("battle") is None:
            state.setdefault("last_battle_events", []).extend(events)
        else:
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
        if state.get("dungeon_run"):
            raise GameError("Rest is only available between expeditions.")
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

    def make_story_choice(self, state: dict[str, Any], option_id: str, beat_choices: dict | None = None) -> dict[str, Any]:
        node_id = state.get("pending_story")
        if not node_id or node_id not in STORY_NODES:
            raise GameError("There is no conversation waiting for a response.")
        node = STORY_NODES[node_id]
        option = next((item for item in node["options"] if item["id"] == option_id), None)
        if not option:
            raise GameError("That response is not available.")
        if option.get("requires") and not self._cond_ok(state, option["requires"]):
            raise GameError(option.get("hint") or "That choice is not open to you yet.")
        # answers given to questions earlier in the scene shape the story too
        picked = {}
        for beat in node.get("beats", []):
            ask_id = beat.get("ask")
            if not ask_id or not self._cond_ok(state, beat.get("if", {})):
                continue
            choice = next((o for o in beat["options"] if o["id"] == (beat_choices or {}).get(ask_id)), None)
            if choice:
                picked[ask_id] = choice["id"]
                self._apply_effects(state, choice)
        for action_id in option.get("unlock_actions", []):
            self._unlock(state["unlocked_actions"], action_id)
        for zone_id in option.get("unlock_zones", []):
            self._unlock(state["unlocked_zones"], zone_id)
        for friend, amount in option.get("friendship", {}).items():
            state["friendships"][friend] = state["friendships"].get(friend, 0) + amount
        if option.get("grant_ally"):
            self._grant_ally(state, option["grant_ally"], guaranteed=True)
        self._apply_effects(state, option)
        state["branches"][node_id] = option["branch"]
        state["story_history"].append(
            {"node": node_id, "speaker": node["speaker"], "choice": option["label"], "reply": option["reply"], "asked": picked}
        )
        # Side quests and path stories never move the main story; main beats never move it backwards.
        if not node["eyebrow"].startswith(("SIDE QUEST", "PATH")) and self._phase_index(node["next_phase"]) >= self._phase_index(state["story_phase"]):
            state["story_phase"] = node["next_phase"]
        state["pending_story"] = None
        if node_id in state.get("available_stories", []):
            state["available_stories"].remove(node_id)
        self._log(state, f"{node['speaker']}: {option['reply']}", "story")
        self._log(state, option["result"], "growth")
        self._check_story_progress(state)
        return self.public_state(state)

    def _apply_effects(self, state: dict[str, Any], effect: dict) -> None:
        """Flags, path points, rewards and permanent stat changes carried by a story choice."""
        flags = effect.get("flag", [])
        for flag in ([flags] if isinstance(flags, str) else flags):
            if flag not in state.setdefault("flags", []):
                state["flags"].append(flag)
        self._add_traits(state, effect.get("traits"))
        for key in ("gold", "magicules", "insight", "research"):
            if effect.get(key):
                state[key] += effect[key]
        if effect.get("xp"):
            self._grant_xp(state, effect["xp"])
        for stat, amount in effect.get("stats", {}).items():
            state[stat] = state.get(stat, 0) + amount
            if stat == "max_hp":
                state["hp"] = min(state["max_hp"], state["hp"] + amount)
            if stat == "max_mana":
                state["mana"] = min(state["max_mana"], state["mana"] + amount)

    def _add_traits(self, state: dict[str, Any], gains: dict | None) -> None:
        if not gains:
            return
        traits = state.setdefault("traits", {key: 0 for key in PATHS})
        for key, amount in gains.items():
            traits[key] = traits.get(key, 0) + amount

    def _dominant(self, state: dict[str, Any]) -> str | None:
        traits = state.get("traits", {})
        best = max(PATHS, key=lambda key: traits.get(key, 0))
        return best if traits.get(best, 0) >= 3 else None

    def _cond_ok(self, state: dict[str, Any], cond: dict) -> bool:
        for key, value in cond.items():
            if key == "flag" and value not in state.get("flags", []):
                return False
            if key == "not_flag" and value in state.get("flags", []):
                return False
            if key == "trait" and state.get("traits", {}).get(value[0], 0) < value[1]:
                return False
            if key == "dominant" and self._dominant(state) != value:
                return False
            if key == "friend" and state.get("friendships", {}).get(value[0], 0) < value[1]:
                return False
            if key == "any" and not any(self._cond_ok(state, c) for c in value):
                return False
        return True

    def _story_view(self, state: dict[str, Any], node_id: str | None) -> dict[str, Any] | None:
        """The scene as this save sees it: lines filtered by flags and paths, locked options marked."""
        node = STORY_NODES.get(node_id) if node_id else None
        if not node:
            return None
        view = copy.deepcopy(node)
        beats = []
        for beat in view.get("beats", []):
            if not self._cond_ok(state, beat.get("if", {})):
                continue
            for option in beat.get("options", []):
                option["lines"] = [ln for ln in option["lines"] if self._cond_ok(state, ln.get("if", {}))]
            beats.append(beat)
        view["beats"] = beats
        for option in view["options"]:
            option["locked"] = bool(option.get("requires")) and not self._cond_ok(state, option["requires"])
            if option.get("aftermath"):
                option["aftermath"] = [ln for ln in option["aftermath"] if self._cond_ok(state, ln.get("if", {}))]
        return view

    @staticmethod
    def _task_cost(action: dict) -> tuple[str, int, int]:
        """(resource, amount, seconds) for a timed action. Mental work spends Mana; the rest spends Focus."""
        duration = max(action.get("duration", 0), GameEngine._duration_from_difficulty(action.get("difficulty")))
        if action.get("mana_cost"):
            return "mana", action["mana_cost"], duration
        return "focus", action.get("focus_cost", max(1, round(duration / 3))), duration

    def _resume_queue(self, state: dict[str, Any]) -> None:
        """Start the next queued task as soon as there is room and enough Focus or Mana."""
        if state.get("activity") or state.get("pending_story") or state.get("dungeon_run"):
            return
        if not state.get("action_queue"):
            auto = state.get("auto_action")
            if auto in ACTIONS and auto in state.get("unlocked_actions", []):
                cost_type, cost, _ = self._task_cost(ACTIONS[auto])
                if state[cost_type] >= cost:
                    try:
                        self.start_activity(state, auto)
                    except GameError:
                        pass
            return
        next_action = state["action_queue"][0]
        cost_type, cost, _ = self._task_cost(ACTIONS[next_action])
        if state[cost_type] >= cost:
            state["action_queue"].pop(0)
            try:
                self.start_activity(state, next_action)
            except GameError as error:
                # a task that can never start (for example, training with no allies) must not jam the queue
                self._log(state, f"Skipped {ACTIONS[next_action]['name']}: {error}", "system")

    def start_story(self, state: dict[str, Any], node_id: str) -> dict[str, Any]:
        """Activate an available story node so the conversation appears (manual trigger).

        The node must be discovered (in state['available_stories']) and no action must be running.
        """
        if not node_id or node_id not in STORY_NODES:
            raise GameError("That conversation is unknown.")
        if state.get("dungeon_run"):
            raise GameError("Finish the expedition before starting a conversation.")
        if state.get("pending_story") and state["pending_story"] != node_id:
            raise GameError("Finish the current conversation first.")
        if node_id not in state.get("available_stories", []) and state.get("pending_story") != node_id:
            raise GameError("That conversation is not available right now.")
        if state.get("activity"):
            self._drop_activity(state, "Paused")  # a repeat or the queue resumes after the conversation
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
        data["story_objective"] = STORY_OBJECTIVES.get(state["story_phase"], "Carry on with the chronicle.")
        data["story_progress"] = self._story_progress(state)
        data["chronicle_progress"] = data["story_progress"]
        data["pending_story"] = self._story_view(state, state.get("pending_story"))
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
            cost_type, cost, duration = self._task_cost(action)
            action["cost"] = cost
            action["cost_type"] = cost_type
            action["duration"] = duration
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
            data["party"].append(
                {
                    **copy.deepcopy(base),
                    **copy.deepcopy(progress),
                    "attack": base["attack"] + level_bonus,
                    "defense": base["defense"] + level_bonus // 2,
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
            {key: copy.deepcopy(value) for key, value in STORY_NODES[n].items() if key not in ("beats", "options")} | {"id": n}
            for n in state.get("available_stories", [])
        ]
        dominant = self._dominant(state)
        data["traits"] = {key: state.get("traits", {}).get(key, 0) for key in PATHS}
        data["paths"] = copy.deepcopy(PATHS)
        data["dominant_path"] = dominant
        data["flags"] = list(state.get("flags", []))
        data["alignment"] = f"{PATHS[dominant]['name']}'s path" if dominant else "Unwritten"

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

        # Prestige multipliers
        data["prestige_multipliers"] = copy.deepcopy(state.get("prestige_multipliers", {}))

        # --- UI helpers ---
        data["server_time"] = now
        data["loop_state"] = copy.deepcopy(state.get("loops", {}))
        data["locked_actions"] = [
            {k: action.get(k) for k in ("id", "name", "type", "description", "unlock_level")}
            for action in ACTIONS.values()
            if action.get("type") in ("loop", "instant", "upgrade") and state["level"] < action.get("unlock_level", 1)
        ]
        data["rest_cost"] = max(2, state["level"] * 2)
        data["last_battle_events"] = list(state.get("last_battle_events", []))[-12:]

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
        self._add_traits(state, action.get("traits"))
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
                interval = loop.get("interval", action.get("interval", 10))
                # last_tick defaults to when the loop started; fallback to now
                last = loop.get("last_tick", loop.get("started_at", now))
                next_tick = loop.get("next_tick", last + interval)
                ticks = 0
                # catch up on missed ticks, within a sane limit
                sloth = self._multiplier(state, "loops")
                while now >= next_tick and ticks < self.MAX_LOOP_TICKS:
                    # apply periodic rewards (light version of completing the action)
                    state["magicules"] += round(action.get("magicules", 0) * self._multiplier(state, "magicules") * sloth)
                    state["insight"] += action.get("insight", 0) + self._multiplier(state, "insight")
                    state["gold"] += round(action.get("gold", 0) * self._multiplier(state, "gold") * sloth)
                    state["research"] += round(action.get("research", 0) * self._multiplier(state, "research") * sloth)
                    state["hp"] = min(state.get("max_hp", 0), state.get("hp", 0) + action.get("heal", 0))
                    state["mana"] = min(state.get("max_mana", 0), state.get("mana", 0) + action.get("mana_regen", 0))
                    self._grant_xp(state, round(action.get("xp", 0) * self._multiplier(state, "xp") * sloth))
                    # record a passive completion count so story unlocks still see progress
                    state.setdefault("action_counts", {})[action_id] = state.setdefault("action_counts", {}).get(action_id, 0) + 1
                    self._add_traits(state, action.get("traits"))
                    ticks += 1
                    last = next_tick
                    next_tick += interval
                if ticks:
                    self._log(state, f"Auto: {action['name']} ran {ticks} cycle{'s' if ticks != 1 else ''}.", "action")
                loop["last_tick"] = last
                loop["next_tick"] = next_tick
            except Exception:
                # avoid any loop processing error from blocking the rest of the refresh
                continue

    def _recover_focus(self, state: dict[str, Any]) -> None:
        """Recover focus over time based on focus_recovery_seconds."""
        now = time.time()
        # loops with focus_per_second (Meditation) grant Focus every second they run
        rate = sum(ACTIONS[a].get("focus_per_second", 0) for a in state.get("loops", {}) if a in ACTIONS)
        last_med = state.get("_last_meditate_tick", now)
        secs = int(now - last_med)
        if rate and secs >= 1:
            state["focus"] = min(state.get("max_focus", 21), state.get("focus", 12) + rate * secs)
            state["_last_meditate_tick"] = last_med + secs
        elif not rate:
            state["_last_meditate_tick"] = now
        last = state.get("_last_focus_tick", now)
        elapsed = now - last
        if elapsed >= 1:
            recovery_interval = state.get("focus_recovery_seconds", 85)
            # recover 1 focus per interval
            recovered = int(elapsed / recovery_interval)
            if recovered > 0:
                state["focus"] = min(state.get("max_focus", 21), state.get("focus", 12) + recovered)
                state["_last_focus_tick"] = now

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
        self._add_traits(state, {"warrior": 1})
        self._grant_xp(state, round(enemy.get("xp", 0) * self._multiplier(state, "xp")))
        recruited = self._try_recruit(state, enemy)
        if recruited:
            run["recruited"].append(recruited)
        self._log(state, f"Victory: +{enemy.get('xp',0)} XP, +{enemy.get('gold',0)} gold, +{enemy.get('magicules',0)} Magicules, +{enemy.get('research',0)} Research.", "victory")

    def _try_recruit(self, state: dict[str, Any], battle: dict[str, Any]) -> str | None:
        ally_id = battle.get("ally_id")
        if not ally_id or ally_id in state["allies"]:
            return None
        chance = min(0.9, recruitment_chance(battle["strength"]) * self._multiplier(state, "recruit"))
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
            if node_id not in STORY_NODES:
                return
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

        # Beats that follow the ones above (each waits for the previous beat to be resolved).
        zr = state.get("zone_runs", {})
        ac = state.get("action_counts", {})
        fr = state.get("friendships", {})
        triggers = [
            ("learn_from_friend", "veldora_analysis", ac.get("magicule_circulation", 0) >= 1),
            ("learn_from_friend", "escape_cave", ac.get("magicule_circulation", 0) >= 2),
            ("protect_village", "gobta_meeting", ac.get("talk_goblins", 0) >= 1 or state.get("total_victories", 0) >= 4),
            ("protect_village", "rigurd_pledge", fr.get("goblin_village", 0) >= 3),
            ("dwarf_kingdom", "dwarf_kingdom", True),
            ("dwarf_kingdom", "kaijin_meeting", "meet_gazel" in completed),
            ("orc_lord_arc", "orc_lord_approach", True),
            ("tempest_federation", "kijin_names", "kijin_arrival" in completed),
            ("tempest_federation", "tempest_founding", "kijin_names" in completed),
            ("tempest_federation", "diablo_summon", "tempest_founding" in completed),
            ("walpurgis", "walpurgis", True),
            ("farmus_invasion", "farmus_invasion", True),
            ("farmus_invasion", "shion_revival", "falmuth_betrayal" in completed),
            ("farmus_invasion", "falmuth_peace", "farmus_invasion" in completed),
            ("epilogue", "epilogue", True),
        ]
        for trigger_phase, node_id, ready in triggers:
            if phase == trigger_phase and ready:
                offer(node_id)
        for trigger in PATH_TRIGGERS:
            if phase in trigger["phases"] and trigger["node"] not in completed and self._cond_ok(state, trigger["cond"]):
                offer(trigger["node"])
        # The optional ruins open once the marsh road is walked.
        if "lizard_marsh" in state["unlocked_zones"] and state.get("total_runs", 0) >= 2:
            self._unlock(state["unlocked_zones"], "ancient_ruins")
        # Checkpoints the story has already carried you past count as done.
        here = self._phase_index(phase)
        for action_id, checkpoint in ACTIONS.items():
            target = checkpoint.get("story_phase")
            if checkpoint.get("type") == "next" and target and action_id not in state["next_actions_completed"] \
                    and self._phase_index(target) <= here:
                state["next_actions_completed"].append(action_id)

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
            attack += max(1, (base["attack"] + level - 1) // 2)
            defense += max(0, (base["defense"] + (level - 1) // 2) // 2)
        # passive party members grant half bonuses
        for ally_id in state.get("passive_party", []):
            if ally_id not in state["allies"]:
                continue
            base = ALLIES[ally_id]
            level = state["allies"][ally_id]["level"]
            attack += max(0, (base["attack"] + level - 1) // 4)
            defense += max(0, (base["defense"] + (level - 1) // 2) // 4)
        return attack, defense

    def _multiplier(self, state: dict[str, Any], resource: str) -> float:
        """Combined prestige, astral, habit and sin multiplier for a resource."""
        mult = state.get("prestige_multipliers", {}).get(resource, 1.0)
        astral = state.get("astral_upgrades", {})
        if resource in ("magicules", "gold", "xp"):
            mult *= 1 + HABIT_BONUS * state.get("habit_points", 0)
        if resource == "magicules" and "soul_amplifier" in astral:
            mult *= 1 + ASTRAL_UPGRADES["soul_amplifier"]["per_level"] * astral["soul_amplifier"]
        if resource == "gold" and "golden_touch" in astral:
            mult *= 1 + ASTRAL_UPGRADES["golden_touch"]["per_level"] * astral["golden_touch"]
        if resource == "xp" and "great_sage" in astral:
            mult *= 1 + ASTRAL_UPGRADES["great_sage"]["per_level"] * astral["great_sage"]
        if resource == "attack":
            if "predator_essence" in astral:
                mult *= 1 + ASTRAL_UPGRADES["predator_essence"]["per_level"] * astral["predator_essence"]
            if "ragnarok" in astral:
                mult *= 1 + ASTRAL_UPGRADES["ragnarok"]["per_level"] * astral["ragnarok"]
        if resource == "hp":
            if "unbreakable_slime" in astral:
                mult *= 1 + ASTRAL_UPGRADES["unbreakable_slime"]["per_level"] * astral["unbreakable_slime"]
            if "ragnarok" in astral:
                mult *= 1 + ASTRAL_UPGRADES["ragnarok"]["per_level"] * astral["ragnarok"]
        if resource == "insight":
            if "eternal_insight" in astral:
                mult += ASTRAL_UPGRADES["eternal_insight"]["per_level"] * astral["eternal_insight"]
            if "great_sage" in astral:
                mult += astral["great_sage"]
        sin_key = {"magicules": "gluttony", "gold": "greed", "xp": "pride", "research": "envy", "attack": "wrath",
                   "loops": "sloth", "recruit": "lust"}.get(resource)
        if sin_key and sin_key in state.get("sins", {}):
            mult *= 1 + SINS[sin_key]["per_level"] * state["sins"][sin_key]["level"]
        return mult

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