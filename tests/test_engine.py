import time
import random
import unittest

from game.engine import GameEngine, GameError


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine(random.Random(4))

    def test_new_game_creates_rimuru_state(self):
        state = self.engine.new_game("rimuru")
        self.assertTrue(state["started"])
        self.assertEqual(state["character"], "rimuru")
        self.assertEqual(state["level"], 1)
        self.assertEqual(state["magicules"], 0)
        self.assertEqual(state["research"], 0)
        self.assertEqual(state["habit_points"], 0)
        self.assertEqual(state["inspiration"], 0)
        self.assertEqual(state["reincarnations"], 0)

    def test_public_state_includes_your_chronicle_data(self):
        state = self.engine.new_game("rimuru")
        public = self.engine.public_state(state)
        self.assertIn("loops", public)
        self.assertIn("instant_actions", public)
        self.assertIn("upgrade_actions", public)
        self.assertIn("next_actions", public)
        self.assertIn("summonable_allies", public)
        self.assertIn("dark_ritual", public)
        self.assertIn("astral_upgrades", public)
        self.assertIn("reincarnation_classes", public)
        self.assertIn("sins", public)
        self.assertIn("prestige_multipliers", public)

    def test_loop_actions_start_and_stop(self):
        state = self.engine.new_game("rimuru")
        state["pending_story"] = None
        state["level"] = 2
        self.engine.start_loop(state, "rest_loop")
        self.assertIn("rest_loop", state["loops"])
        self.engine.stop_loop(state, "rest_loop")
        self.assertNotIn("rest_loop", state["loops"])

    def test_instant_actions_trade_resources(self):
        state = self.engine.new_game("rimuru")
        state["pending_story"] = None
        state["focus"] = 20
        before = state["magicules"]
        self.engine.perform_instant(state, "get_motivated")
        self.assertGreater(state["magicules"], before)
        self.assertLess(state["focus"], 20)

    def test_upgrade_actions_increase_stats(self):
        state = self.engine.new_game("rimuru")
        state["pending_story"] = None
        state["level"] = 2
        state["magicules"] = 50
        before_hp = state["max_hp"]
        self.engine.perform_upgrade(state, "expand_body")
        self.assertGreater(state["max_hp"], before_hp)

    def test_next_actions_advance_story(self):
        state = self.engine.new_game("rimuru")
        state["pending_story"] = None
        state["magicules"] = 100
        self.engine.perform_next(state, "next_escape")
        self.assertIn("next_escape", state["next_actions_completed"])

    def test_research_summoning(self):
        state = self.engine.new_game("rimuru")
        state["pending_story"] = None
        state["research"] = 20
        self.engine.summon_ally(state, "cave_bat")
        self.assertIn("cave_bat", state["allies"])

    def test_dark_ritual_resets_and_grants_habits(self):
        state = self.engine.new_game("rimuru")
        state["pending_story"] = None
        state["level"] = 5
        state["magicules"] = 100
        state["gold"] = 50
        self.engine.dark_ritual(state)
        self.assertEqual(state["level"], 1)
        self.assertGreater(state["habit_points"], 0)

    def test_astral_upgrades(self):
        state = self.engine.new_game("rimuru")
        state["pending_story"] = None
        state["inspiration"] = 5
        self.engine.buy_astral_upgrade(state, "soul_amplifier")
        self.assertEqual(state["astral_upgrades"]["soul_amplifier"], 1)

    def test_reincarnation(self):
        state = self.engine.new_game("rimuru")
        state["pending_story"] = None
        state["level"] = 10
        self.engine.reincarnate(state, "warrior")
        self.assertEqual(state["reincarnations"], 1)
        self.assertEqual(state["reincarnation_class"], "warrior")

    def test_sin_system(self):
        state = self.engine.new_game("rimuru")
        state["pending_story"] = None
        state["level"] = 8
        state["magicules"] = 50
        self.engine.unlock_sin(state, "gluttony")
        self.assertIn("gluttony", state["sins"])
        self.engine.level_sin(state, "gluttony")
        self.assertEqual(state["sins"]["gluttony"]["level"], 2)

    def test_combat_still_works(self):
        state = self.engine.new_game("rimuru")
        state["pending_story"] = None
        state["unlocked_zones"] = ["sealed_cave"]
        self.engine.start_dungeon(state, "sealed_cave")
        self.assertIsNotNone(state["battle"])
        for _ in range(100):
            if not state["battle"]:
                break
            self.engine.combat_turn(state, "slime_strike")
        self.assertIsNone(state["battle"])
        self.assertGreater(state["total_victories"], 0)

    def test_habit_points_assign_and_refund(self):
        state = self.engine.new_game("rimuru")
        state["habit_points"] = 3
        self.engine.assign_habit(state, "worship", 2)
        self.assertEqual(state["routines"]["worship"], 2)
        self.assertEqual(state["habit_points"], 1)
        self.engine.unassign_habit(state, "worship", 1)
        self.assertEqual(state["routines"]["worship"], 1)
        self.assertEqual(state["habit_points"], 2)
        with self.assertRaises(GameError):
            self.engine.assign_habit(state, "worship", 99)

    def test_routines_multiply_resources(self):
        state = self.engine.new_game("rimuru")
        base = self.engine._multiplier(state, "magicules")
        state["habit_points"] = 5
        self.engine.assign_habit(state, "worship", 5)
        self.assertAlmostEqual(self.engine._multiplier(state, "magicules"), base * 1.2)

    def test_seeds_feed_hero_and_ally(self):
        state = self.engine.new_game("rimuru")
        state["seeds"]["physical"] = 2
        before = state["attack"]
        self.engine.feed_seed(state, "physical", "hero")
        self.assertEqual(state["attack"], before + 1)
        self.assertEqual(state["seed_bonus"]["attack"], 1)
        state["allies"]["gobta"] = {"level": 1, "recruited_at": 0}
        self.engine.feed_seed(state, "physical", "gobta")
        self.assertEqual(state["ally_seeds"]["gobta"]["attack"], 1)
        with self.assertRaises(GameError):
            self.engine.feed_seed(state, "physical", "hero")

    def test_seed_bonus_survives_dark_ritual(self):
        state = self.engine.new_game("rimuru")
        state["seeds"]["physical"] = 1
        self.engine.feed_seed(state, "physical", "hero")
        state["pending_story"] = None
        state["level"] = 10
        self.engine.dark_ritual(state)
        self.assertEqual(state["seed_bonus"]["attack"], 1)
        self.assertEqual(state["attack"], self.engine.new_game("rimuru")["attack"] + 1)

    def test_food_requires_gluttony_then_stacks(self):
        state = self.engine.new_game("rimuru")
        state["foods"]["pork"] = 2
        with self.assertRaises(GameError):
            self.engine.consume_food(state, "pork")
        state["pending_story"] = None
        state["level"] = 8
        state["magicules"] = 50
        self.engine.unlock_sin(state, "gluttony")
        self.engine.consume_food(state, "pork", 2)
        self.assertEqual(state["gluttony_stacks"]["pork"], 2)
        self.assertEqual(state["foods"]["pork"], 0)
        self.assertGreater(self.engine._multiplier(state, "attack"), 1.0)

    def test_boss_drops_seed_and_food(self):
        state = self.engine.new_game("rimuru")
        state["pending_story"] = None
        state["unlocked_zones"] = ["sealed_cave"]
        state["attack"] = 80
        state["max_hp"] = state["hp"] = 900
        self.engine.start_dungeon(state, "sealed_cave")
        for _ in range(200):
            if not state["battle"]:
                break
            self.engine.combat_turn(state, "slime_strike")
        self.assertGreater(sum(state["seeds"].values()), 0)
        self.assertGreater(sum(state["foods"].values()) + sum(state["gluttony_stacks"].values()), 0)

    def test_sloth_speeds_up_loops(self):
        state = self.engine.new_game("rimuru")
        state["sins"]["sloth"] = {"level": 4, "unlocked_at": 0}
        self.assertAlmostEqual(self.engine.loop_interval(state, 10), 8.0)

    def test_reincarnation_records_ending_and_restarts_story(self):
        state = self.engine.new_game("rimuru")
        state["pending_story"] = None
        state["level"] = 10
        state["branches"] = {"first_words": "Diplomatic", "goblins": "Protective"}
        self.engine.reincarnate(state, "warrior")
        self.assertEqual(state["endings"], ["benevolent"])
        self.assertGreaterEqual(state["inspiration"], 2)
        self.assertEqual(state["story_phase"], "awakening")
        self.assertEqual(state["unlocked_actions"], ["gather_dew"])

    def test_focus_recovers_over_time(self):
        state = self.engine.new_game("rimuru")
        state["focus"] = 0
        state["focus_recovery_seconds"] = 10
        state["_last_focus_tick"] = time.time() - 35
        self.engine._recover_focus(state)
        self.assertEqual(state["focus"], 3)

    def test_instant_action_grants_xp_and_costs_magicules(self):
        state = self.engine.new_game("rimuru")
        state["pending_story"] = None
        state["level"] = 5
        state["focus"] = 20
        state["magicules"] = 0
        with self.assertRaises(GameError):
            self.engine.perform_instant(state, "devour")


if __name__ == "__main__":
    unittest.main()