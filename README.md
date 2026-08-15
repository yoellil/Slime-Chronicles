# Chronicles of Reincarnation

A Python-first, fan-made incremental RPG prototype inspired by *Your Chronicle*
and *That Time I Got Reincarnated as a Slime*.

## Play

```powershell
python server.py --open
```

Then visit `http://127.0.0.1:8787`. The game saves automatically to a local
SQLite database in `data/chronicles.db`.

No third-party Python packages are required. The Python engine owns character
routes, actions, combat, progression, story choices, offline Focus recovery,
and saves. The browser files provide only the visual interface.

## Systems

- **Actions** — timed actions with a queue, background loops, instant trades,
  permanent upgrades, and Next story checkpoints.
- **Combat** — automated expeditions with multi-enemy encounters, research
  drops, monster summoning, and active/passive party slots.
- **Routines & Habits** — spend the Habit Points from a Dark Ritual on
  routines (Worship the Storm Dragon, Sword Drills with Hakuro, Trade with
  Dwargon...) for permanent resource and stat multipliers.
- **Seeds** — expedition bosses drop Physical or Magical seeds; feed them to
  Rimuru or an ally for permanent base stats that survive every reset.
- **Sins** — Gluttony devours food, Sloth speeds up loops, Greed/Pride/Envy/
  Wrath multiply Gold, XP, Research and Attack, and Lust improves recruitment.
- **Feast** — creatures drop themed foods (Orc Pork, Hipokute Herb, Cave
  Mushroom...) that stack into permanent modifiers scaled by Gluttony.
- **Prestige** — Dark Ritual for Habits and Inspiration, the Astral World for
  permanent upgrades, and Reincarnation, which records an ending, grants a
  class, and restarts the story so other endings can be pursued.

## Test

```powershell
python -m unittest discover -s tests -v
```

This is an unofficial fan prototype. It is not affiliated with or endorsed by
the owners of *That Time I Got Reincarnated as a Slime* or *Your Chronicle*.

