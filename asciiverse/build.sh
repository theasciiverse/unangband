#!/bin/sh
# Builds Unangband with its curses (GCU) frontend only: no X11, GTK, SDL
# or sound. Linux: run inside alpine:3.22 for a fully static binary (musl,
# static ncurses); macOS: run on the runner, with CC_ARCH set to x86_64
# or arm64, linking the system curses. Elsewhere it links the host's
# ncursesw.
#   docker run --rm -v "$PWD":/src -w /src alpine:3.22 sh asciiverse/build.sh
# Uses upstream's src/Makefile.std with the X11 module switched off.
# Leaves the program as ./unangband in the repository root. It reads its
# game data from the lib folder beside it, and keeps the player's files
# (options, saves, scores, bones and the compiled data files) in
# $XDG_STATE_HOME/unangband (PATCHES.md).
set -eu
if [ -f /etc/alpine-release ]; then
  apk add --no-cache build-base ncurses-dev ncurses-static >/dev/null
  ldflags="-static"
  curses="-lncursesw"
elif [ "$(uname -s)" = Darwin ]; then
  ldflags=""
  curses="-lncurses"
else
  ldflags=""
  curses="-lncursesw"
fi
cc="cc${CC_ARCH:+ -arch $CC_ARCH}"
# PRIVATE_USER_PATHS: scores, bones, data and saves in the player's own
# folder instead of lib/ (src/init2.c). It goes in INCLUDES because the
# makefile adds the modules to its own CFLAGS, which a CFLAGS given here
# would replace.
make -C src -f Makefile.std clean >/dev/null 2>&1 || true
make -C src -f Makefile.std -j"${JOBS:-$(getconf _NPROCESSORS_ONLN)}" \
  CC="$cc" SYS_x11= "SYS_gcu=-DUSE_GCU -DUSE_NCURSES $curses" \
  "INCLUDES=-I. -DPRIVATE_USER_PATHS" \
  LDFLAGS="$ldflags" unangband >/dev/null
cp src/unangband unangband
strip unangband
