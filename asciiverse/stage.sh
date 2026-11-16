#!/bin/sh
# Gathers what ships into stage/, after asciiverse/build.sh: the program,
# the read-only game data it needs (lib/edit, file, help, info and pref,
# without their build files), the licence, our README and PATCHES.md.
# No fonts, tiles or sounds (lib/xtra): this build is curses only. The
# folders the game writes to (apex, bone, data, save, user) are in the
# player's state folder instead. The av archive is stage/ as it is.
set -eu
rm -rf stage
mkdir -p stage/lib
cp unangband stage/
for d in edit file help info pref; do
  cp -R "lib/$d" stage/lib/
done
find stage/lib -type f \( -name 'Makefile*' -o -name 'delete.me' -o -name '.*' \) -exec rm {} +
cp LICENSE PATCHES.md stage/
cp asciiverse/README.md stage/README.md
