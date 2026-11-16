#!/usr/bin/env python3
"""Records asciiverse/unangband.cast, Unangband's catalog preview, at
100x30 (hub/RECORDING.md). A Dwarf Warrior with a taste for hafted
weapons, called Gimrin, is made at the birth screens in Hobbiton, takes
the road to Farmer Maggot's farm, explores the farm, then climbs down
into its cellars: he walks to the nearest unexplored
edge, fights what is next to him, picks things up and takes the stairs
down he comes across. Several takes are made and the liveliest one is
kept.

Usage, from the repo root after asciiverse/build.sh and
asciiverse/stage.sh, with tmux and asciinema 3 installed:
    python3 asciiverse/record-preview.py

The game runs by name from a copy of stage/ on PATH, with a throwaway
home and state folder, so the cast holds no local path or login name.
It runs in a tmux of its own, which the script reads the screen from;
asciinema records a client attached to it."""
import fcntl, json, os, pty, random, select, shutil, struct, sys, tempfile, termios, time
from collections import deque

import subprocess

SOCK = "unangband-rec"


class TmuxScreen:
    """What the game shows, read from its tmux pane. tmux is the terminal
    the game draws on; asciinema records a client attached to it."""

    @property
    def display(self):
        try:
            out = subprocess.run(["tmux", "-L", SOCK, "capture-pane", "-p", "-t", "rec"],
                                 capture_output=True, text=True, timeout=5).stdout.split("\n")
        except subprocess.TimeoutExpired:
            out = []
        rows = [line.ljust(COLS)[:COLS] for line in out[:ROWS]]
        return rows + [" " * COLS] * (ROWS - len(rows))


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAST = os.path.join(ROOT, "asciiverse", "unangband.cast")
COLS, ROWS = 100, 30
# the map starts after the 13-column sidebar, under the message line, and
# ends above the two status lines
X0, Y0, Y1 = 13, 1, ROWS - 2

# the original keyset's number keys, which need no keypad
DIRS = {(-1, 1): "1", (0, 1): "2", (1, 1): "3", (-1, 0): "4",
        (1, 0): "6", (-1, -1): "7", (0, -1): "8", (1, -1): "9"}
FLOOR = set(".'<>:;,^")
ITEMS = set("!?_-=\"$~|/\\()[]{},&")
DOORS = set("+")
WALLS = set("#%*")


class Game:
    def __init__(self, stage, home):
        env = {"PATH": f"{stage}:/usr/bin:/bin:/snap/bin", "HOME": home, "USER": "player",
               "XDG_STATE_HOME": os.path.join(home, "state"),
               "LOGNAME": "player", "TERM": "xterm-256color", "COLORTERM": "truecolor",
               "LANG": "C.UTF-8"}
        self.screen = TmuxScreen()
        # the game runs in a tmux of its own (no status line, no bell, no
        # user config), stderr (its data checks) dropped
        subprocess.run(["tmux", "-L", SOCK, "kill-server"], capture_output=True, timeout=10)
        subprocess.run(["tmux", "-L", SOCK, "-f", "/dev/null", "new-session", "-d",
                        "-s", "rec", "-x", str(COLS), "-y", str(ROWS), "-c", home,
                        "unangband -uGimrin 2>/dev/null", ";",
                        "set", "-g", "status", "off", ";",
                        "set", "-g", "bell-action", "none"], env=env, check=True)
        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            os.chdir(home)
            os.execvpe("asciinema", ["asciinema", "rec", "--overwrite", "-q",
                "--idle-time-limit", "2", "--window-size", f"{COLS}x{ROWS}",
                "--capture-env", "TERM,COLORTERM,LANG", "--title", "Unangband",
                "--command", f"tmux -L {SOCK} attach -t rec", CAST], env)
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))
        self.start = time.time()

    def pump(self, t):
        end = time.time() + t
        while True:
            left = end - time.time()
            r, _, _ = select.select([self.fd], [], [], max(0.0, min(0.02, left)))
            if r:
                try:
                    data = os.read(self.fd, 65536)
                except OSError:
                    return False
                if not data:
                    return False
            if left <= 0:
                return True

    def key(self, k, wait=0.2):
        os.write(self.fd, k.encode() if isinstance(k, str) else k)
        return self.pump(wait)

    def text(self):
        return "\n".join(self.screen.display)

    def wait_for(self, s, timeout=6.0):
        end = time.time() + timeout
        while time.time() < end:
            if s in self.text():
                return True
            self.pump(0.05)
        return False

    def elapsed(self):
        return time.time() - self.start

    def grid(self):
        return [row[X0:] for row in self.screen.display[Y0:Y1]]

    def finish(self):
        end = time.time() + 6
        while time.time() < end:
            if not self.pump(0.1):
                break
            if os.waitpid(self.pid, os.WNOHANG)[0]:
                break
        else:
            print("game did not exit; stopping the recording", file=sys.stderr)
            os.kill(self.pid, 15)
        try:
            os.waitpid(self.pid, 0)
        except ChildProcessError:
            pass
        subprocess.run(["tmux", "-L", SOCK, "kill-server"], capture_output=True, timeout=10)


def find(grid, chars):
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch in chars:
                return (x, y)
    return None


def is_monster(ch):
    return ch.isalpha() and ch.isascii()


def bfs(grid, me, want, passable):
    """First step from me toward the nearest cell want() likes."""
    h, w = len(grid), len(grid[0])
    seen = {me: None}
    q = deque([me])
    while q:
        cur = q.popleft()
        if cur != me and want(cur):
            while seen[cur] != me:
                cur = seen[cur]
            return (cur[0] - me[0], cur[1] - me[1])
        for (dx, dy) in DIRS:
            x, y = cur[0] + dx, cur[1] + dy
            if 0 <= y < h and 0 <= x < w and (x, y) not in seen and \
                    (passable(grid[y][x]) or want((x, y))):
                seen[(x, y)] = cur
                q.append((x, y))
    return None


def take(stage):
    home = tempfile.mkdtemp(prefix="unangband-rec-")
    g = Game(stage, home)
    g.wait_for("Press any key", 10)
    g.pump(1.5)
    g.key("\r", 1.0)
    # birth: desktop keys, has played Unangband before (no hint pages),
    # male, Dwarf, Warrior, hafted weapons, rolled stats, the name from
    # -u, accept
    for k, wait in (("a", 0.6), ("d", 0.6), ("b", 0.6), ("e", 0.6), ("a", 0.6),
                    ("g", 0.6), ("a", 1.2), ("\r", 1.0)):
        g.key(k, wait)
    end = time.time() + 12
    while time.time() < end and "You have entered" not in g.screen.display[0]:
        t = g.text()
        if "accept" in t or "continue" in t or "Return" in t or "Enter a name" in t:
            g.key("\r", 0.8)
        else:
            g.pump(0.3)
    g.pump(4.0)            # the welcome to Hobbiton, on screen
    g.key("\x1b", 0.3)
    g.key("\x12", 0.5)

    phase = "farm"           # the road to the farm, then "cellar", "dungeon"
    on_down = False          # just stepped onto a '>'
    visited = set()
    depth = 0
    stuck = 0
    last = None
    while g.elapsed() < 56:
        t = g.text()
        top = "\n".join(g.screen.display[:6])
        if "-more-" in top or "-end-" in top:
            # dismiss the message, then redraw: a long one leaves its
            # last line over the sidebar until the screen is redrawn
            g.key("\x1b", 0.2)
            g.key("\x12", 0.3)
            continue
        if "Info file" in g.screen.display[0]:
            # a hint page, or Mr Maggot's note: a moment to read, then on
            g.pump(2.5 if "dungeon" in g.screen.display[0] else 0.5)
            g.key("\x1b", 0.3)
            continue
        if g.screen.display[0].startswith("Command:"):
            g.key("\x1b", 0.2)
            continue
        if "Command Summary" in t or "ESC to exit" in t or "exit.]" in t:
            g.key("\x1b", 0.3)
            continue
        if "[y/n]" in t or "(y/n)" in t:
            g.key("n", 0.2)
            continue
        if phase == "store" and ("Gold Remaining" in t or "Item Description" in t):
            g.pump(2.0)
            g.key("\x1b", 0.8)
            phase = "farm"
            continue
        if phase == "store" and g.elapsed() > 16:
            phase = "farm"
        if phase == "farm":
            # the road to Farmer Maggot's farm
            g.key("<", 1.0)
            if "Travel to where" in g.screen.display[0]:
                g.key("b", 2.5)
            g.pump(3.5)        # the farm's own welcome, on screen
            g.key("\x1b", 0.3)
            g.key("\x12", 0.5)
            phase = "cellar"
            continue
        grid = g.grid()
        me = find(grid, "@")
        if me is None:
            g.key("\x1b", 0.3)
            continue
        visited.add((depth, me))

        # out of town, everything next to him is fought
        target = None
        for (dx, dy) in DIRS:
            x, y = me[0] + dx, me[1] + dy
            # Farmer Maggot and other folk ('h', 'p') are left in peace
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]) and \
                    is_monster(grid[y][x]) and grid[y][x] not in "hp":
                target = (dx, dy)
                break
        if target and phase in ("cellar", "dungeon"):
            g.key(DIRS[target], 0.25)
            continue

        if on_down and ((phase == "cellar" and g.elapsed() > 47) or
                        (phase == "dungeon" and g.elapsed() > 46)):
            g.key(">", 1.5)
            on_down = False
            depth += 1
            phase = "dungeon"
            visited.clear()
            continue
        if "You see" in g.screen.display[0] and phase == "dungeon":
            g.key("g", 0.35)
            continue

        def passable(ch):
            if is_monster(ch) and (phase != "dungeon" or ch in "hp"):
                return False   # walk round Farmer Maggot and the townsfolk
            return ch not in WALLS and ch != " " and ch not in "+"

        def want(c):
            ch = grid[c[1]][c[0]]
            if phase == "store":
                return ch in "1234567"
            if phase == "cellar" and g.elapsed() > 47:
                return ch == ">"   # down into the cellars
            if phase == "cellar" and ch == ">":
                return False
            if ch in ITEMS:
                return True
            if ch == ">" and g.elapsed() > 30 + 12 * depth:
                return True
            if (depth, c) in visited or not passable(ch):
                return False
            for (dx, dy) in DIRS:
                x, y = c[0] + dx, c[1] + dy
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]) and grid[y][x] == " ":
                    return True
            return False

        step = bfs(grid, me, lambda c: want(c) or False, lambda ch: passable(ch) or ch in DOORS)
        if step is None or stuck >= 3:
            # a random step, but never into Farmer Maggot or his folk
            free = [d for d in DIRS
                    if 0 <= me[1] + d[1] < len(grid) and 0 <= me[0] + d[0] < len(grid[0])
                    and grid[me[1] + d[1]][me[0] + d[0]] not in "hp"]
            step = random.choice(free or list(DIRS))
            stuck = 0
        nx, ny = me[0] + step[0], me[1] + step[1]
        on_down = grid[ny][nx] == ">"
        g.key(DIRS[step], 0.15 if phase != "dungeon" else 0.12)
        now = g.grid()
        stuck = stuck + 1 if now == last else 0
        last = now

    # save and quit: Ctrl-X saves, then the score list, then out
    g.key("\x18", 1.5)
    g.key("\r", 2.5)
    g.key("\x1b", 0.5)
    g.finish()
    shutil.rmtree(home, ignore_errors=True)


def score(cast):
    """How good a take is to watch: it must last 30 seconds; fights,
    kills and levels gone down count."""
    lines = open(cast).read().splitlines()
    idle = json.loads(lines[0]).get("idle_time_limit") or 2
    events = [json.loads(l) for l in lines[1:]]
    length = sum(min(e[0], idle) for e in events)
    if length < 30 or length > 60:
        return -1
    text = "".join(e[2] for e in events if e[1] == "o")
    if "You die" in text or "Killed by" in text and "nobody" not in text:
        return -1
    return (text.count("You hit") + 4 * text.count("You have slain")
            + 4 * text.count("You have killed") + 6 * text.count("You enter a maze")
            + 3 * text.count("You have no more") + text.count("You have "))


def main():
    src = os.path.join(ROOT, "stage")
    if not os.path.exists(os.path.join(src, "unangband")):
        sys.exit("run asciiverse/build.sh and asciiverse/stage.sh first")
    stage = tempfile.mkdtemp(prefix="unangband-stage-")
    shutil.copytree(src, stage, dirs_exist_ok=True)
    best = None
    for attempt in range(int(os.environ.get("TAKES", "5"))):
        take(stage)
        sc = score(CAST)
        print(f"take {attempt + 1}: score {sc}", file=sys.stderr)
        if best is None or sc > best[0]:
            best = (sc, open(CAST).read())
    with open(CAST, "w") as f:
        f.write(best[1])
    shutil.rmtree(stage, ignore_errors=True)


if __name__ == "__main__":
    main()
