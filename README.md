# fse-mods

The mod catalog of [FSE](https://github.com/watdafawx/fse): mods made for fse, listed in `index.json`. The fse hub
(the **F** button in game) shows them in its **Get mods** tab and installs them into your mods folder (they load at
the game's next start).

## index.json

```json
{"mods": [{
  "name": "ai-crew", "title": "AI Crew", "author": "mtopfox", "description": "...",
  "repo": "https://github.com/watdafawx/ai-crew", "version": "0.11.0",
  "url": "https://github.com/watdafawx/ai-crew/releases/download/v0.11.0/ai-crew_0.11.0.zip",
  "sha256": "...", "fse": "0.10.0", "plugins": ["py"], "dependencies": ["base >= 2.0", "? fse-std"],
  "pypath": true
}]}
```

| field | meaning |
|---|---|
| `url`, `sha256` | the mod's zip (one top folder holding `info.json`) and its hash: the hub installs nothing whose hash differs |
| `fse` | the oldest fse it runs on |
| `plugins` | fse plugins it needs (the hub says which are missing) |
| `dependencies` | its `info.json`'s; required mods that aren't installed are shown (they come from the mod portal) |
| `pypath` | it has a Python half: its folder goes on `FSE_PYPATH` in `fse.env` |

FSE mods can run native code, so every version gets here through a reviewed change to this file, with the zip's
hash pinned. The hub installs `<mods>\<name>_<version>\` (a folder), removes older copies and enables it; a working
copy (a link, or a folder with `.git`) is never replaced.

## Adding a mod or a version

1. The mod lives in a public GitHub repo with `info.json` at its root. Commit and push the version.
2. `python add.py <path to the repo clone>`: zips that commit (without `test/`), makes the GitHub release
   `v<version>` with the zip, and writes the entry. For a new mod, set `fse`, `plugins` and `pypath` by hand and run
   it again (`--dry-run` prints the entry only).
3. Commit and push `index.json` (others: open a pull request).
