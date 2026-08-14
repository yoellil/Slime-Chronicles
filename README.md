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

## Test

```powershell
python -m unittest discover -s tests -v
```

This is an unofficial fan prototype. It is not affiliated with or endorsed by
the owners of *That Time I Got Reincarnated as a Slime* or *Your Chronicle*.

