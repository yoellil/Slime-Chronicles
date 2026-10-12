"""High-level mechanics flow test."""
from game.engine import GameEngine
import random

e = GameEngine(random.Random(4))
s = e.new_game("rimuru")
s["pending_story"] = None
s["level"] = 5
s["magicules"] = 100
s["gold"] = 50
s["research"] = 30
s["focus"] = 20
s["inspiration"] = 5

ok = True

try:
    e.perform_upgrade(s, "expand_body")
    print("Upgrade: OK (max_hp=" + str(s["max_hp"]) + ")")
except Exception as ex:
    print("Upgrade FAIL:", ex)
    ok = False

try:
    e.perform_next(s, "next_escape")
    print("Next: OK")
except Exception as ex:
    print("Next FAIL:", ex)
    ok = False

try:
    e.summon_ally(s, "cave_bat")
    print("Summon: OK (allies=" + str(len(s["allies"])) + ")")
except Exception as ex:
    print("Summon FAIL:", ex)
    ok = False

try:
    e.buy_astral_upgrade(s, "soul_amplifier")
    print("Astral: OK")
except Exception as ex:
    print("Astral FAIL:", ex)
    ok = False

try:
    e.dark_ritual(s)
    print("Ritual: OK (habits=" + str(s["habit_points"]) + ")")
except Exception as ex:
    print("Ritual FAIL:", ex)
    ok = False

s["level"] = 10
try:
    e.reincarnate(s, "demon_lord")
    print("Reincarnate: OK (count=" + str(s["reincarnations"]) + ")")
except Exception as ex:
    print("Reincarnate FAIL:", ex)
    ok = False

s["level"] = 8
s["magicules"] = 50
try:
    e.unlock_sin(s, "gluttony")
    e.level_sin(s, "gluttony")
    print("Sin: OK (level=" + str(s["sins"]["gluttony"]["level"]) + ")")
except Exception as ex:
    print("Sin FAIL:", ex)
    ok = False

print()
print("MECHANICS FLOW:", "ALL OK" if ok else "HAS FAILURES")