import random
import unittest

from game.engine import GameEngine, GameError


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine(random.Random(4))

    def test_routes_begin_with_distinct_stats_and_content(self):
        rimuru = self.engine.new_game("rimuru")
        diablo = self.engine.new_game("diablo")
        self.assertNotEqual(rimuru["max_hp"], diablo["max_hp"])
        self.assertEqual(self.engine.public_state(rimuru)["resource_label"], "Magicules")
        self.assertEqual(self.engine.public_state(diablo)["resource_label"], "Soul Embers")

    def test_actions_spend_focus_and_grant_progress(self):
        state = self.engine.new_game("rimuru")
        before = state["focus"]
        self.engine.perform_action(state, "gather_dew", 3)
        self.assertEqual(state["focus"], before - 3)
        self.assertEqual(state["magicules"], 9)
        self.assertGreater(state["xp"], 0)

    def test_locked_zone_rejects_early_entry(self):
        state = self.engine.new_game("diablo")
        with self.assertRaises(GameError):
            self.engine.start_battle(state, "crimson_court")

    def test_combat_eventually_awards_a_victory(self):
        state = self.engine.new_game("rimuru")
        self.engine.start_battle(state, "sealed_cave")
        for _ in range(20):
            if not state["battle"]:
                break
            self.engine.combat_turn(state, "slam")
        self.assertIsNone(state["battle"])
        self.assertEqual(state["total_victories"], 1)
        self.assertGreater(state["gold"], 0)

    def test_first_boss_unlocks_a_route_choice(self):
        state = self.engine.new_game("diablo")
        state["zone_progress"]["abyssal_reach"] = self.engine.BOSS_THRESHOLD
        state["zone_bosses"].append("abyssal_reach")
        public = self.engine.public_state(state)
        self.assertEqual(public["pending_choice"]["id"], "distant_call")
        self.engine.make_choice(state, "answer")
        self.assertEqual(state["alignment"], "Devotion")
        self.assertTrue(state["choice_resolved"])


if __name__ == "__main__":
    unittest.main()

