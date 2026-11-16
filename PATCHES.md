# Changes from upstream

This is the Asciiverse packaging of Unangband (the Unnamed Angband) by
Andrew Doull, Duncan Lowther (DGoldDragon28) and others, from
[DGoldDragon28/Unangband](https://github.com/DGoldDragon28/Unangband)
(the `upstream` remote). Branch `asciiverse` starts at upstream's
`master`, commit `70ca6de` (2025-05-26): the `v.0.7.0-pre1` release of
2018-12-25 and eleven commits of fixes after it (`git describe`:
`v.0.7.0-pre1-11-g70ca6de`). It plays well, so it is preferred over the
older 0.6.6 release. Licence: GPL-2.0 (`LICENSE`). The commits below are
ours.

## Code

- **A colour fix in the curses frontend** (`src/main-gcu.c`):
  `colortable[]` had 28 entries (`BASIC_COLORS`), but the game draws in
  colours up to `TERM_FOREST` (38) and `Term_text_gcu()` looks them up
  with `colortable[a & 255]`, so it read past the end of the table. With
  the `_FORTIFY_SOURCE` that most compilers now turn on, the game
  aborted with "buffer overflow detected" ("software bug") when saving
  and quitting; AddressSanitizer showed the read. The table now has
  `MAX_COLORS` (256) entries; the colours with no curses mapping draw in
  the terminal's default colour. Offerable upstream as it is.
- **Paths** (`src/main.c`, `src/init2.c`, `src/externs.h`): when
  `ANGBAND_PATH` is not set, the game reads its data from a `lib` folder
  beside the running program, found through `/proc/self/exe` on Linux
  and `_NSGetExecutablePath()` on macOS (so av's symbolic link in
  `~/.local/bin` still finds it), instead of `./lib/` in the current
  folder. The player's folder, `~/.angband/Unangband` upstream, is
  `$XDG_STATE_HOME/unangband` (else `~/.local/state/unangband`),
  created with any missing parents. Built with `PRIVATE_USER_PATHS`, it
  also holds the `scores`, `bone`, `data` (the compiled `.raw` files)
  and `save` folders, so nothing is written into `lib`.

## Build settings

`asciiverse/build.sh` runs upstream's `src/Makefile.std` with the X11
module switched off (`SYS_x11=`), the curses frontend against ncursesw
(the system curses on macOS), and `-DPRIVATE_USER_PATHS`. Linux builds
are fully static in Alpine (musl, static ncurses); they read the
system's terminfo.

The game checks its data at every start and prints what it finds to
standard error ("Warning: Guardian ... wimpy"). That is upstream's own
behaviour and is left as it is; av sends standard error to the title's
log.

## Packaging (new files)

- `asciiverse/build.sh`: the build above; leaves `./unangband`.
- `asciiverse/stage.sh`: puts the program, `lib/{edit,file,help,info,pref}`
  without the build files, `LICENSE`, our README and this file in
  `stage/`, the av archive's contents. No fonts, tiles, sounds or music
  (`lib/xtra`) are shipped; they stay in the tree as upstream has them.
- `asciiverse/README.md`: the README in each archive.
- `asciiverse/record-preview.py` and `asciiverse/unangband.cast`: the
  catalog preview, a scripted Dwarf Warrior who travels from Hobbiton to
  Farmer Maggot's farm and climbs down into its cellars (best of several
  takes).
- `asciiverse/unangband.toml`, `asciiverse/unangband.md`: the catalog
  manifest and store page, as drafts for hub.
- `.github/workflows/asciiverse-release.yml`: builds the Linux and macOS
  archives on a `*-av.*` tag.
- `CLAUDE.md`, this file; `.gitignore` leaves out `stage/` and the
  built program.

## Not built

- Windows: upstream builds a GUI frontend (`main-win.c`) with
  `Makefile.cyg`. A Windows console build would need PDCurses and a
  Windows branch of the path change, and has not been tried.
- X11, GTK, SDL and sound.

