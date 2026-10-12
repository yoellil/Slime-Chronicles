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


class StoryWiringTests(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine(random.Random(7))

    def fresh(self):
        state = self.engine.new_game("rimuru")
        state["pending_story"] = None
        return state

    def test_every_phase_can_be_checked_without_crashing(self):
        from game.content import PHASE_ORDER, STORY_NODES

        for phase in PHASE_ORDER:
            state = self.fresh()
            state["story_phase"] = phase
            state["total_runs"] = 9
            state["total_victories"] = 99
            state["gold"] = 50
            state["zone_runs"] = {zone: 3 for zone in state["zone_runs"]}
            state["action_counts"] = {action: 3 for action in state["action_counts"]}
            state["friendships"] = {"goblin_village": 9, "kijin": 9}
            self.engine.refresh(state)
            for node_id in state["available_stories"]:
                self.assertIn(node_id, STORY_NODES)

    def test_side_quest_never_moves_the_main_story(self):
        state = self.fresh()
        state["story_phase"] = "orc_lord_arc"
        state["pending_story"] = "lost_lantern"
        self.engine.make_story_choice(state, "retrieve")
        self.assertEqual(state["story_phase"], "orc_lord_arc")

    def test_main_story_never_moves_backwards(self):
        state = self.fresh()
        state["story_phase"] = "protect_village"
        state["pending_story"] = "escape_cave"
        self.engine.make_story_choice(state, "devour_seal")
        self.assertEqual(state["story_phase"], "protect_village")

    def test_checkpoints_must_be_taken_in_order(self):
        state = self.fresh()
        state.update(level=20, magicules=99999, gold=99999)
        with self.assertRaises(GameError):
            self.engine.perform_next(state, "next_tempest")
        self.engine.perform_next(state, "next_escape")
        self.assertIn("sealed_cave", state["unlocked_zones"])

    def test_checkpoint_opens_its_region(self):
        state = self.fresh()
        state.update(level=20, magicules=99999, gold=99999, story_phase="chapter_one_complete")
        self.engine.refresh(state)
        self.engine.perform_next(state, "next_dwargon")
        self.assertIn("dwargon", state["unlocked_zones"])
        self.assertEqual(state["story_phase"], "dwarf_kingdom")

    def test_passed_checkpoints_are_marked_done(self):
        state = self.fresh()
        state["story_phase"] = "chapter_one_complete"
        self.engine.refresh(state)
        self.assertIn("next_escape", state["next_actions_completed"])
        self.assertIn("next_village", state["next_actions_completed"])

    def test_habit_points_raise_gains(self):
        state = self.fresh()
        base = self.engine._multiplier(state, "magicules")
        state["habit_points"] = 10
        self.assertAlmostEqual(self.engine._multiplier(state, "magicules"), base * 1.2)

    def test_sins_amplify_their_gain(self):
        state = self.fresh()
        base = self.engine._multiplier(state, "gold")
        state["sins"] = {"greed": {"level": 3}}
        self.assertAlmostEqual(self.engine._multiplier(state, "gold"), base * 1.3)

    def test_party_slots_cap_without_spending(self):
        state = self.fresh()
        state.update(level=9, magicules=999, gold=999, max_party_slots=5)
        with self.assertRaises(GameError):
            self.engine.perform_upgrade(state, "expand_party")
        self.assertEqual(state["magicules"], 999)


class ManaAndPathTests(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine(random.Random(11))

    def fresh(self):
        state = self.engine.new_game("rimuru")
        state["pending_story"] = None
        state["unlocked_actions"] += ["analyze_moss", "gather_dew"]
        return state

    def test_mental_tasks_spend_mana_and_physical_ones_spend_focus(self):
        state = self.fresh()
        mana, focus = state["mana"], state["focus"]
        self.engine.start_activity(state, "analyze_moss")
        self.assertEqual(state["mana"], mana - 3)
        self.assertEqual(state["focus"], focus)
        self.engine.cancel_activity(state)
        self.assertEqual(state["mana"], mana)
        self.engine.start_activity(state, "gather_dew")
        self.assertEqual(state["focus"], focus - 1)

    def test_not_enough_mana_is_refused(self):
        state = self.fresh()
        state["mana"] = 1
        with self.assertRaises(GameError):
            self.engine.start_activity(state, "analyze_moss")

    def test_loops_restore_mana_and_can_run_beside_a_task(self):
        state = self.fresh()
        state["mana"] = 2
        self.engine.start_activity(state, "gather_dew")
        self.engine.start_loop(state, "rest_loop")
        state["loops"]["rest_loop"]["next_tick"] = 0
        self.engine._process_loops(state)
        self.assertGreater(state["mana"], 2)

    def test_queued_mana_task_resumes_when_mana_returns(self):
        state = self.fresh()
        state["mana"] = 0
        state["action_queue"] = ["analyze_moss"]
        self.engine._resume_queue(state)
        self.assertIsNone(state["activity"])
        state["mana"] = 10
        self.engine._resume_queue(state)
        self.assertEqual(state["activity"]["action_id"], "analyze_moss")

    def test_auto_repeat_restarts_the_action_and_cancel_stops_it(self):
        state = self.fresh()
        self.engine.toggle_auto_action(state, "gather_dew")
        self.assertEqual(state["activity"]["action_id"], "gather_dew")
        state["activity"]["ends_at"] = 0
        self.engine.refresh(state)
        self.assertEqual(state["action_counts"]["gather_dew"], 1)
        self.assertEqual(state["activity"]["action_id"], "gather_dew")
        self.engine.cancel_activity(state)
        self.assertIsNone(state["auto_action"])
        self.engine.refresh(state)
        self.assertIsNone(state["activity"])

    def test_repeating_task_catches_up_while_you_were_away(self):
        state = self.fresh()
        state["focus"] = 20
        self.engine.toggle_auto_action(state, "gather_dew")
        state["activity"]["started_at"] -= 60
        state["activity"]["ends_at"] -= 60  # a minute ago: room for many 3 second cycles
        self.engine.refresh(state)
        self.assertGreater(state["action_counts"]["gather_dew"], 5)
        self.assertLessEqual(state["focus"], 20)  # each cycle paid its Focus

    def test_loop_catch_up_logs_one_summary_line(self):
        state = self.fresh()
        self.engine.start_loop(state, "rest_loop")
        state["loops"]["rest_loop"]["next_tick"] -= 120
        self.engine._process_loops(state)
        self.assertEqual(sum(1 for entry in state["log"] if entry["text"].startswith("Auto:")), 1)
        self.assertGreater(state["action_counts"]["rest_loop"], 10)

    def test_rest_works_beside_a_running_task(self):
        state = self.fresh()
        state.update(gold=50, hp=3)
        self.engine.start_activity(state, "gather_dew")
        self.engine.rest(state)
        self.assertEqual(state["hp"], state["max_hp"])

    def test_cannot_start_a_conversation_mid_dungeon_or_over_another(self):
        state = self.fresh()
        state["available_stories"] = ["lost_lantern", "herbalist"]
        state["unlocked_zones"] = ["sealed_cave"]
        self.engine.start_story(state, "lost_lantern")
        with self.assertRaises(GameError):
            self.engine.start_story(state, "herbalist")
        state["pending_story"] = None
        self.engine.start_dungeon(state, "sealed_cave")
        with self.assertRaises(GameError):
            self.engine.start_story(state, "herbalist")

    def test_starting_a_conversation_pauses_a_repeating_task(self):
        state = self.fresh()
        state["available_stories"] = ["lost_lantern"]
        focus = state["focus"]
        self.engine.toggle_auto_action(state, "gather_dew")
        self.engine.start_story(state, "lost_lantern")
        self.assertIsNone(state["activity"])
        self.assertEqual(state["focus"], focus)
        self.engine.refresh(state)
        self.assertIsNone(state["activity"])  # stays paused while the conversation is open
        self.engine.make_story_choice(state, "ignore")
        self.engine.refresh(state)
        self.assertEqual(state["activity"]["action_id"], "gather_dew")

    def test_unstartable_queue_item_is_skipped_not_stuck(self):
        state = self.fresh()
        state["unlocked_actions"].append("train_allies")
        state["focus"] = 20
        state["action_queue"] = ["train_allies", "gather_dew"]
        self.engine._resume_queue(state)
        self.assertEqual(state["action_queue"], ["gather_dew"])

    def test_entering_a_dungeon_pauses_and_refunds_the_task(self):
        state = self.fresh()
        state["unlocked_zones"] = ["sealed_cave"]
        focus = state["focus"]
        self.engine.toggle_auto_action(state, "gather_dew")
        self.engine.start_dungeon(state, "sealed_cave")
        self.assertIsNone(state["activity"])
        self.assertEqual(state["focus"], focus)
        self.assertEqual(state["auto_action"], "gather_dew")

    def test_actions_build_paths(self):
        state = self.fresh()
        self.engine.start_activity(state, "analyze_moss")
        state["activity"]["ends_at"] = 0
        self.engine.refresh(state)
        self.assertEqual(state["traits"]["scholar"], 1)

    def test_locked_choice_is_marked_and_refused(self):
        state = self.fresh()
        state["pending_story"] = "goblin_encounter"
        public = self.engine.public_state(state)
        locked = {o["id"]: o["locked"] for o in public["pending_choice"]["options"]}
        self.assertTrue(locked["show_strength"])
        self.assertFalse(locked["listen_first"])
        with self.assertRaises(GameError):
            self.engine.make_story_choice(state, "show_strength")
        state["traits"]["warrior"] = 3
        self.engine.make_story_choice(state, "show_strength")
        self.assertIn("forest_road", state["unlocked_zones"])

    def test_scene_answers_set_flags_that_change_later_lines(self):
        state = self.fresh()
        state["pending_story"] = "inner_voice"
        self.engine.make_story_choice(state, "ask_guidance", {"first_instinct": "taste"})
        self.assertIn("hungry_start", state["flags"])
        state["pending_story"] = "distant_roar"
        lines = [b["text"] for b in self.engine.public_state(state)["pending_choice"]["beats"] if "text" in b]
        self.assertTrue(any("Predator suggests" in text for text in lines))
        self.assertFalse(any("Politeness has" in text for text in lines))

    def test_path_story_is_offered_once_the_path_is_walked(self):
        state = self.fresh()
        state["story_phase"] = "protect_village"
        state["traits"]["builder"] = 6
        self.engine.refresh(state)
        self.assertIn("village_foundations", state["available_stories"])

    def test_story_choice_rewards_and_stats_apply(self):
        state = self.fresh()
        state["pending_story"] = "herbalist"
        before = state["max_hp"]
        self.engine.make_story_choice(state, "gather")
        self.assertEqual(state["max_hp"], before + 3)


if __name__ == "__main__":
    unittest.main()