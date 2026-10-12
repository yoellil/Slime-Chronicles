"""Test scavenge instant action focus cost."""
from game.engine import GameEngine, GameError
import random

e = GameEngine(random.Random(4))
s = e.new_game("rimuru")
s["pending_story"] = None
s["level"] = 5
s["magicules"] = 50
s["gold"] = 30
s["focus"] = 10  # Start with enough focus

print('Before scavenge: focus =', s["focus"])

try:
    r = e.perform_instant(s, "scavenge")
    print('After scavenge: focus =', s["focus"], '| magicules =', s["magicules"], '| xp =', s["xp"])
    if s["focus"] != 7:  # 10 - 3 = 7
        print('BUG: focus_cost was not applied! Expected 7, got', s["focus"])
    else:
        print('OK: focus_cost was applied correctly')
except GameError as ex:
    print('ERROR:', ex)
except Exception as ex:
    print('UNEXPECTED ERROR:', ex)