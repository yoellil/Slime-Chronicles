"""Python-owned rules for Slime Chronicles."""

from __future__ import annotations

import copy
import random
import time
from typing import Any

from .content import (
    ACTIONS,
    ALLIES,
    HERO,
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
    VERSION = 2
    MAX_LOG = 64
    MAX_PARTY = 3

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
            "insight": 0,
            "training": {"attack": 0, "mana": 0},
            "activity": None,
            # queued actions persist in the save so players can queue multiple runs
            "action_queue": [],
            "action_counts": {action_id: 0 for action_id in ACTIONS},
            "unlocked_actions": ["gather_dew"],
            "unlocked_zones": [],
            "zone_runs": {zone_id: 0 for zone_id in ZONES},
            "dungeon_run": None,
            "battle": None,
            "allies": {},
            "active_party": [],
            "friendships": {},
            "story_phase": "awakening",
            "pending_story": "inner_voice",
            "available_stories": [],
            "story_history": [],
            "branches": {},
            "total_victories": 0,
            "total_runs": 0,
            "log": [],
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
        activity = state.get("activity")
        if activity and time.time() >= activity["ends_at"]:
            self._complete_activity(state)
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
            try:
                next_action = state["action_queue"].pop(0)
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

    def start_dungeon(self, state: dict[str, Any], zone_id: str) -> dict[str, Any]:
        self._ensure_ready(state)
        if state.get("pending_story"):
            raise GameError("Finish the current conversation first.")
        if state.get("activity"):
            raise GameError("Wait for the current action to finish.")
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
        # resolve target choice
        chosen = None
        if target is not None:
            try:
                idx = int(target)
                if idx < 0 or idx >= len(enemies):
                    raise IndexError
                cand = enemies[idx]
                if cand["hp"] <= 0:
                    raise GameError("That target is already defeated.")
                chosen = cand
            except ValueError:
                chosen = next((e for e in enemies if e["name"] == str(target) and e["hp"] > 0), None)
                if not chosen:
                    raise GameError("Invalid target specified.")
            except IndexError:
                raise GameError("Target index out of range.")
        else:
            chosen = next((e for e in enemies if e["hp"] > 0), None)
        if not chosen:
            raise GameError("No hostile target remains.")

        execute = skill.get("execute")
        if execute and chosen["hp"] / chosen["max_hp"] <= execute:
            damage = chosen["hp"]
            state["magicules"] += 4
            verb = "devoured"
        else:
            party_attack, _ = self._party_bonuses(state)
            effective_defense = chosen["defense"] * (1 - skill.get("pierce", 0))
            variance = self.rng.randint(0, max(1, state["level"] // 3 + 1))
            damage = max(1, round((state["attack"] + party_attack) * skill["power"] + variance - effective_defense))
            verb = "hit"
        chosen["hp"] = max(0, chosen["hp"] - damage)
        self._log(state, f"{skill['name']} {verb} {chosen['name']} for {damage} damage.", "combat")

        if chosen["hp"] <= 0:
            # handle per-enemy victory (xp, gold, magicules, recruitment)
            self._win_enemy(state, chosen)
            # if no alive enemies remain in this encounter, advance the run
            if not any(e["hp"] > 0 for e in enemies):
                run = state["dungeon_run"]
                if run["encounter"] >= run["total"]:
                    zone_id = run["zone_id"]
                    state["zone_runs"][zone_id] += 1
                    state["total_runs"] += 1
                    self._log(state, f"EXPEDITION COMPLETE — {run['zone_name']} cleared through all {run['total']} encounters.", "story")
                    state["dungeon_run"] = None
                    state["battle"] = None
                    self._check_story_progress(state)
                    return self.public_state(state)
                # advance to next encounter
                run["encounter"] += 1
                state["hp"] = min(state["max_hp"], state["hp"] + max(3, state["max_hp"] // 5))
                state["mana"] = min(state["max_mana"], state["mana"] + max(2, state["max_mana"] // 6))
                self._spawn_encounter(state)
                return self.public_state(state)

        # enemy retaliates (first alive enemy attacks)
        attacker = next((e for e in enemies if e["hp"] > 0), None)
        if attacker:
            _, party_defense = self._party_bonuses(state)
            enemy_damage = max(1, attacker["attack"] + self.rng.randint(0, 2) - state["defense"] - party_defense)
            state["hp"] = max(0, state["hp"] - enemy_damage)
            # advance encounter-wide turn counter
            battle["turn"] = battle.get("turn", 1) + 1
            self._log(state, f"{attacker['name']} retaliates for {enemy_damage} damage.", "danger")
            if state["hp"] <= 0:
                run_name = state["dungeon_run"]["zone_name"]
                state["battle"] = None
                state["dungeon_run"] = None
                state["hp"] = max(1, state["max_hp"] // 2)
                state["mana"] = max(0, state["max_mana"] // 2)
                self._log(state, f"The {run_name} expedition failed. You escape with half vitality.", "danger")
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
        else:
            if len(state["active_party"]) >= self.MAX_PARTY:
                raise GameError("The active party can contain at most three allies.")
            state["active_party"].append(ally_id)
            self._log(state, f"{ALLIES[ally_id]['name']} joins the active party.", "growth")
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
            data["party"].append(
                {
                    **copy.deepcopy(base),
                    **copy.deepcopy(progress),
                    "attack": base["attack"] + level_bonus,
                    "defense": base["defense"] + level_bonus // 2,
                    "active": ally_id in state["active_party"],
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
        return data

    def _complete_activity(self, state: dict[str, Any]) -> None:
        activity = state["activity"]
        action = ACTIONS[activity["action_id"]]
        action_id = action["id"]
        state["activity"] = None
        state["action_counts"][action_id] += 1
        state["magicules"] += action["magicules"]
        state["insight"] += action["insight"]
        state["hp"] = min(state["max_hp"], state["hp"] + action.get("heal", 0))
        self._grant_xp(state, action["xp"])
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
        state["gold"] += enemy.get("gold", 0)
        state["magicules"] += enemy.get("magicules", 0)
        run["earned_gold"] += enemy.get("gold", 0)
        run["earned_magicules"] += enemy.get("magicules", 0)
        run["victories"] += 1
        state["total_victories"] += 1
        self._grant_xp(state, enemy.get("xp", 0))
        recruited = self._try_recruit(state, enemy)
        if recruited:
            run["recruited"].append(recruited)
        self._log(state, f"Victory: +{enemy.get('xp',0)} XP, +{enemy.get('gold',0)} gold, +{enemy.get('magicules',0)} Magicules.", "victory")

    def _try_recruit(self, state: dict[str, Any], battle: dict[str, Any]) -> str | None:
        ally_id = battle.get("ally_id")
        if not ally_id or ally_id in state["allies"]:
            return None
        chance = recruitment_chance(battle["strength"])
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
        if len(state["active_party"]) < self.MAX_PARTY:
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
        return attack, defense

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

