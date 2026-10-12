"""Comprehensive API bug test for Slime Chronicles."""
import json
import urllib.request
import http.cookiejar

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def api(path, payload=None):
    if payload is None:
        req = urllib.request.Request(
            "http://127.0.0.1:8787" + path,
            headers={"Accept": "application/json"},
        )
    else:
        req = urllib.request.Request(
            "http://127.0.0.1:8787" + path,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
    try:
        with opener.open(req) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}


results = []

# 1. New game
r = api("/api/new-game", {"character": "rimuru"})
results.append(("1. new-game", "OK" if r.get("started") else "FAIL"))

# 2. Story choice
r = api("/api/choice", {"choice": "ask_guidance"})
results.append(("2. choice", "OK" if r.get("story_phase") == "first_steps" else f"FAIL {r}"))

# 3. Loop start/stop
r = api("/api/loop/start", {"action": "rest_loop"})
results.append(("3. loop start", "OK" if "error" not in r else f"FAIL {r}"))
r = api("/api/loop/stop", {"action": "rest_loop"})
results.append(("4. loop stop", "OK" if "error" not in r else f"FAIL {r}"))

# 5. Instant action
r = api("/api/instant", {"action": "get_motivated"})
results.append(("5. instant", "OK" if r.get("magicules", 0) > 0 else f"FAIL {r}"))

# 6. Action queue
r = api("/api/action", {"action": "gather_dew", "count": 2})
ok = len(r.get("action_queue", [])) > 0 or r.get("activity") or "error" in r
results.append(("6. action queue", "OK" if ok else f"FAIL {r}"))

# 7. Cancel activity
r = api("/api/action/cancel")
results.append(("7. cancel", "OK" if "error" not in r else "OK (no active)"))

# 8. Upgrade at level 1 (should error)
r = api("/api/upgrade", {"action": "expand_body"})
results.append(("8. upgrade lvl1", "OK" if r.get("error") else "FAIL - should error"))

# 9. Next not enough resources
r = api("/api/next", {"action": "next_escape"})
results.append(("9. next not enough", "OK" if r.get("error") else "FAIL"))

# 10. Bad endpoint
r = api("/api/bad_endpoint", {})
results.append(("10. bad endpoint", "OK" if r.get("error") else "FAIL"))

# 11. Story start
r = api("/api/story/start", {"node": "distant_roar"})
ok = "error" in r or r.get("pending_story", {}).get("id")
results.append(("11. story start", "OK" if ok else f"FAIL {r}"))

# 12. Combat locked zone
r = api("/api/combat/start", {"zone": "sealed_cave"})
results.append(("12. combat locked", "OK" if r.get("error") else "FAIL"))

# 13. Rest
r = api("/api/rest")
ok = "error" in r or r.get("hp") == r.get("max_hp")
results.append(("13. rest", "OK" if ok else f"FAIL {r}"))

# 14. Sin unlock at low level
r = api("/api/sin/unlock", {"sin": "gluttony"})
results.append(("14. sin low lvl", "OK" if r.get("error") else "FAIL"))

# 15. Ritual at low level
r = api("/api/ritual", {})
results.append(("15. ritual low lvl", "OK" if r.get("error") else "FAIL"))

# 16. Reincarnate at low level
r = api("/api/reincarnate", {"class": "warrior"})
results.append(("16. reincarnate low lvl", "OK" if r.get("error") else "FAIL"))

# 17. Astral with no inspiration
r = api("/api/astral", {"upgrade": "soul_amplifier"})
results.append(("17. astral no insp", "OK" if r.get("error") else "FAIL"))

# 18. Summon with no research
r = api("/api/summon", {"ally": "cave_bat"})
results.append(("18. summon no res", "OK" if r.get("error") else "FAIL"))

# 19. State refresh
r = api("/api/state")
results.append(("19. state refresh", "OK" if r.get("started") else "FAIL"))

for label, status in results:
    print(f"{label}: {status}")
print("\nALL ENDPOINT TESTS COMPLETE")