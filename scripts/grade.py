#!/usr/bin/env python3
"""
INF 345 Week 2 - marks report.sh.

Four sections, 25 points each. The truth is computed here in Python, directly
from the directory; nothing is read from a stored answer file. So the only way
to score is to actually inspect the directory you were given.

    python3 scripts/grade.py --script submissions/<you>/report.sh --seed 42

Exit code 0 if the score is 100, 1 otherwise. That exit code is what GitHub
Actions turns into the tick or the cross.
"""

import argparse
import os
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from make_fixture import build  # noqa: E402

SECTIONS = ("FILES", "DIRS", "LARGEST", "EXECUTABLE", "EXTENSIONS")


# ---------- the truth ----------

def truth(root: Path) -> dict:
    files, dirs = [], []
    for dirpath, dirnames, filenames in os.walk(root):
        for d in dirnames:
            dirs.append(Path(dirpath) / d)
        for f in filenames:
            files.append(Path(dirpath) / f)

    sized = sorted(((p.stat().st_size, str(p.relative_to(root))) for p in files),
                   key=lambda t: (-t[0], t[1]))
    execs = sorted(str(p.relative_to(root)) for p in files if p.stat().st_mode & 0o100)

    counts = Counter()
    for p in files:
        if p.suffix and p.name != p.suffix:
            counts[p.suffix] += 1
    exts = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]

    return {"FILES": len(files), "DIRS": len(dirs),
            "LARGEST": sized[:3], "LARGEST_ALL": sized,
            "EXECUTABLE": execs,
            "EXTENSIONS": exts, "EXTENSIONS_ALL": [(c, x) for x, c in
                sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]}


# ---------- reading what the student printed ----------

def norm(path: str) -> str:
    p = path.strip()
    while p.startswith("./"):
        p = p[2:]
    return p.rstrip("/")


def parse(out: str) -> dict:
    got = {k: [] for k in SECTIONS}
    current = None
    for raw in out.splitlines():
        line = raw.strip()
        if not line:
            continue
        head = line.split(":", 1)
        key = head[0].strip().upper()
        if key in SECTIONS:
            current = key
            rest = head[1].strip() if len(head) > 1 else ""
            if rest:
                got[key].append(rest)
            continue
        if current:
            got[current].append(line)
    return got


def as_int(values: list):
    if not values:
        return None
    try:
        return int(values[0].split()[0])
    except (ValueError, IndexError):
        return None


def pairs(values: list):
    """['4096 docs/big.log', ...] -> [(4096, 'docs/big.log'), ...]"""
    out = []
    for v in values:
        parts = v.split(None, 1)
        if len(parts) != 2:
            return None
        try:
            out.append((int(parts[0]), norm(parts[1])))
        except ValueError:
            return None
    return out


def check_topk(got, full, k):
    """Is `got` a valid "top k" of the ranked list `full`?

    `full` is every (rank, name) pair, highest rank first. Ties matter: if four
    extensions all appear three times and only five slots exist, any of them may
    legitimately take the last slot, and several correct scripts will disagree
    about which. Accept every valid answer, not just the one this file happens
    to compute.
    """
    if got is None:
        return False
    want_n = min(k, len(full))
    if len(got) != want_n:
        return False
    if any(got[i][0] < got[i + 1][0] for i in range(len(got) - 1)):
        return False            # must be ordered by rank, highest first
    if len({n for _, n in got}) != len(got):
        return False            # no repeats

    ranks = dict((n, r) for r, n in full)
    if any(n not in ranks or ranks[n] != r for r, n in got):
        return False            # a name that is not there, or the wrong number

    cutoff = full[want_n - 1][0]
    must_have = {n for r, n in full if r > cutoff}
    return must_have <= {n for _, n in got}


# ---------- marking ----------

def mark(want: dict, got: dict) -> tuple:
    score, notes = 0, []

    n = as_int(got["FILES"])
    d = as_int(got["DIRS"])
    if n == want["FILES"] and d == want["DIRS"]:
        score += 25
        notes.append(("pass", "counts", f"{n} files, {d} directories"))
    else:
        shown = lambda v: "(nothing)" if v is None else v
        notes.append(("fail", "counts",
                      f"expected FILES: {want['FILES']} and DIRS: {want['DIRS']}, "
                      f"you printed FILES: {shown(n)} and DIRS: {shown(d)}. "
                      "Count regular files anywhere under the directory, and every "
                      "directory below it - but not the directory you were given."))

    p = pairs(got["LARGEST"])
    if check_topk(p, want["LARGEST_ALL"], 3):
        score += 25
        notes.append(("pass", "largest", "three largest files, biggest first"))
    else:
        exp = ", ".join(f"{s} {n_}" for s, n_ in want["LARGEST"])
        hint = ""
        if p:
            # Block counts are small and round; byte counts are neither.
            if all(s % 4 == 0 and s < 1000 for s, _ in p):
                hint = (" Those look like disk blocks rather than bytes - that is "
                        "what du reports. You want the size in bytes.")
            elif any(name in ("", ".") for _, name in p):
                hint = " One of your lines names a directory rather than a file."
        else:
            hint = (" Each line must be a number, a space, then a path - nothing else "
                    "on the line.")
        notes.append(("fail", "largest",
                      f"expected exactly three lines, '<bytes> <path>', biggest first: {exp}. "
                      f"You printed: {got['LARGEST'] or '(nothing)'}.{hint}"))

    mine = sorted(norm(x) for x in got["EXECUTABLE"])
    if mine == want["EXECUTABLE"]:
        score += 25
        notes.append(("pass", "executable", f"{len(mine)} executable file(s)"))
    else:
        notes.append(("fail", "executable",
                      f"expected {want['EXECUTABLE']}, you printed {mine}. "
                      "A file is executable here if its owner may run it."))

    e = pairs(got["EXTENSIONS"])
    if check_topk(e, want["EXTENSIONS_ALL"], 5):
        score += 25
        notes.append(("pass", "extensions", "five commonest extensions, counted"))
    else:
        exp = ", ".join(f"{c} {x}" for x, c in want["EXTENSIONS"])
        notes.append(("fail", "extensions",
                      f"expected '<count> <extension>', commonest first: {exp}. "
                      f"You printed: {got['EXTENSIONS'] or '(nothing)'}. "
                      "Files with no extension at all are not counted."))

    return score, notes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--seed", type=int, required=True)
    args = ap.parse_args()

    script = Path(args.script)
    if not script.exists():
        print(f"::error::No script at {script}. It must be at "
              f"submissions/<your-github-username>/report.sh")
        return 1
    if not os.access(script, os.X_OK):
        print(f"::error file={script}::{script} is not executable. Run "
              f"'chmod +x {script}', commit the change, and push again. "
              "Git records the executable bit - this is the lecture slide you "
              "photographed.")
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "tree"
        build(args.seed, root)
        want = truth(root)

        try:
            proc = subprocess.run([str(script.resolve()), str(root)],
                                  capture_output=True, text=True, timeout=30)
        except subprocess.TimeoutExpired:
            print("::error::Your script did not finish within 30 seconds. "
                  "Most likely it is waiting for input that will never come.")
            return 1
        except OSError as exc:
            print(f"::error::Could not run your script: {exc}. "
                  "Check the first line is '#!/usr/bin/env bash'.")
            return 1

    if proc.returncode != 0:
        print(f"::error::Your script exited with code {proc.returncode}.")
    if proc.stderr.strip():
        print("--- your script's error output ---")
        print(proc.stderr.strip()[:2000])
        print("--- end ---")

    score, notes = mark(want, parse(proc.stdout))

    print(f"\nFixture seed: {args.seed}  (reproduce with: "
          f"python3 scripts/make_fixture.py --seed {args.seed} --out /tmp/t)\n")
    print("--- what your script printed ---")
    print(proc.stdout.strip()[:3000] or "(nothing)")
    print("--- end ---\n")

    for status, name, detail in notes:
        if status == "pass":
            print(f"  [ 25/25 ] {name}: {detail}")
        else:
            print(f"  [  0/25 ] {name}")
            print(f"            {detail}")

    print(f"\nSCORE: {score}/100")
    return 0 if score == 100 else 1


if __name__ == "__main__":
    sys.exit(main())
