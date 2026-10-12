"""Test devour instant action cost handling."""
from game.engine import GameEngine, GameError
import random

e = GameEngine(random.Random(4))
s = e.new_game("rimuru")
s["pending_story"] = None
s["level"] = 5
s["magicules"] = 20

# The devour action has magicules_cost: 15, but perform_instant only checks focus_cost and gold_cost.
# This means the action can be used without spending magicules. This is a bug.
try:
    r = e.perform_instant(s, "devour")
    print("RESULT: Devour OK - magicules:", s["magicules"], "| xp:", s["xp"])
    # If magicules wasn't reduced by 15, it's a bug
    if s["magicules"] != 5:
        print("BUG: magicules_cost was not applied! Expected 5, got", s["magicules"])
    else:
        print("CLEAN: magicules_cost was applied correctly")
except GameError as ex:
    print("RESULT: Devour rejected:", ex)
except Exception as ex:
    print("RESULT: Unexpected error:", ex)