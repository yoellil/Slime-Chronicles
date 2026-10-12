# Chronicles of Reincarnation

A Python-first, fan-made incremental RPG prototype inspired by *Your Chronicle*
and *That Time I Got Reincarnated as a Slime*.

## Play

```powershell
python server.py --open
```

Then visit `http://127.0.0.1:8787`. The game saves automatically to a local
SQLite database in `data/chronicles.db`.

No third-party Python packages are required. The Python engine owns actions,
combat, progression, story choices, offline Focus recovery and saves. The
browser files (`web/`) only draw the interface and send requests.

## What is in the box

- **Action, Loop, Instant**: click-to-run actions (queue them or repeat with the infinity button), background loops, instant trades. Mental tasks cost Mana, which loops restore.
- **Growth**: permanent upgrades, companions (party slots, Research summoning), sins.
- **Dungeon**: automated battles (step in for manual skills with keys 1-8), repeatable runs. **Story** scenes branch with your path (Scholar, Warrior, Diplomat, Builder). **Journey** lists the main checkpoints.
- **Beyond**: Dark Ritual, Astral World and Reincarnation prestige.

## Test

```powershell
python -m unittest discover -s tests -v
```

This is an unofficial fan prototype. It is not affiliated with or endorsed by
the owners of *That Time I Got Reincarnated as a Slime* or *Your Chronicle*.
