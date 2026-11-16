# Unangband

**The Unnamed Angband: all of Middle-earth, from Hobbiton to Orodruin.**

You wake in Hobbiton with a hundred gold pieces and a road in front of
you. Farmer Maggot has lost his dogs, Grip, Fang and Wolf, and the trap
doors to his famous cellars stand open. Beyond the Shire lie the Old
Forest and Tom Bombadil's house, the Barrow-downs, Bree and Weathertop,
Rivendell, the mines of Moria, Mirkwood and the Lonely Mountain,
Isengard, Edoras, Minas Tirith, and at the end of everything the Plains
of Gorgoroth and the fire of Orodruin. Somewhere out there is the One
Ring. If Sauron gets it first, Middle-earth is doomed.

Unangband is the Angband variant that tried to put everything in. Press
`<` in a town or at the edge of the wild and choose where to travel;
every place is its own dungeon, wood or ruin, with its own monsters and
its own guardian at the bottom.

- **More than twenty races**: Hobbits, Dwarves, Wood- and High-Elves,
  Dúnedain and the Men of Bree, Dale, Rohan, Gondor and Harad, Ents,
  Beornings, giants of fire, frost and the forge, and Orcs, Goblins,
  Werewolves and Vampires for the bold
- **Thirteen classes**, from Warrior, Archer and Thief to Bard, Shaman,
  Artisan and Istari, each with a style to specialise in: a Dwarf who
  only trusts a hammer, an Archer devoted to the bow, a Warrior with a
  weapon in each hand
- **Terrain that matters**: water, ice, lava, mud and chasms, rooms that
  describe themselves as you light them, and monsters that use all of it
- **Things that interact**: set potions in traps, coat your arrows with
  them, throw them as grenades and watch the smoke roll
- **Quests**, from Farmer Maggot's lost dogs all the way to the Crack of
  Doom

## Playing

Run `unangband` from this folder, with its `lib` folder beside it. It
needs a terminal of at least 80x24; a bigger one shows more of the map.

- **Arrow keys** or **1** to **9**: move; walk into a monster to attack
- **<**: travel from a town, or from the edge of a wilderness place
- **>** and **<**: stairs down and up in a dungeon
- **g** pick up, **i** inventory, **e** equipment, **w** wear or wield
- **q** quaff, **r** read, **E** eat, **a** aim, **u** use a staff,
  **z** zap a rod, **f** fire, **v** throw
- **m**: cast a spell; **b**: browse a book
- **y**: apply a rune or potion to something; **j**: set a trap
- **|**: light or douse your light; **Ctrl-Q**: your current quest
- **C**: character sheet, **l**: look, **M**: map, **~**: knowledge
- **=**: options (a roguelike keyset is there too); **?**: help
- **Ctrl-S**: save; **Ctrl-X**: save and quit

Your game, options, scores and character dumps are kept in the state
folder, `$XDG_STATE_HOME/unangband` (else `~/.local/state/unangband`),
and Unangband carries on from your save the next time you start it.

## Credits

- Unangband: Andrew Doull (0.1 to 0.6.4c), with Mikolaj Konarski,
  Mogami, Andrew Sidwell and others; carried on by Duncan Lowther
  (DGoldDragon28, the Gold Dragon) from 0.6.5 and dennis-roof for 0.7.0,
  https://github.com/DGoldDragon28/Unangband
- Built on Angband (Alex Cutler, Andy Astrand, Ben Harrison, Robert
  Ruehlmann and many more), with code from Oangband, Sangband and
  NPPAngband; Moria by Robert Alan Koeneke and Umoria by James E. Wilson
- Licence: GNU GPL version 2 (`LICENSE`)
- This package: Asciiverse, for the av launcher and the catalog at
  https://asciiverse.sh. What we changed is in PATCHES.md.

## Building

`sh asciiverse/build.sh` builds `./unangband` with the curses frontend
only, from upstream's `src/Makefile.std` (statically in Alpine for the
release, against the system curses on macOS), and
`sh asciiverse/stage.sh` gathers the program, its `lib` and these files
into `stage/`. The release workflow
(`.github/workflows/asciiverse-release.yml`) builds the Linux and macOS
archives. Upstream's own `readme.txt` and `compile.txt` cover the rest.
