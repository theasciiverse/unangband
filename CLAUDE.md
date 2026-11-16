# Unangband (Asciiverse packaging)

The Unnamed Angband by Andrew Doull, Duncan Lowther (DGoldDragon28) and
others (C, curses, GPL-2.0), packaged for the Asciiverse catalog (id
`unangband`, kind `game`, genre `roguelike`). Not our code: the game
stays as its authors made it; list every change in PATCHES.md and keep
each offerable upstream.

- `upstream` is github.com/DGoldDragon28/Unangband (branch `master`);
  ours is branch `asciiverse`, `origin` github.com/theasciiverse/unangband
  (private).
- Build: `sh asciiverse/build.sh` (static in alpine:3.22 under docker in
  CI; locally it links the host's ncursesw), then `sh asciiverse/stage.sh`
  for `stage/`: the program with `lib/` beside it.
- Release: tag `v<upstream describe>-av.<n>` (first
  `v0.7.0-pre1-11-av.1`) and push it; the workflow builds Linux and
  macOS. No Windows build (PATCHES.md).
- Player files live in `$XDG_STATE_HOME/unangband`. Tests and scripted
  runs always set a scratch `XDG_STATE_HOME` and `HOME` (and
  `USER=player`: the default character name is the login name) in the
  same command and run under `systemd-run --user --scope -p MemoryMax=4G`.
  No sound is built.
- Preview: `python3 asciiverse/record-preview.py` after stage.sh (needs
  tmux and asciinema 3). Catalog drafts: `asciiverse/unangband.toml` and
  `.md`; copies go in hub/catalog, the cast in hub/site/casts.
