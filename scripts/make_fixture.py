#!/usr/bin/env python3
"""
Build a directory tree to test report.sh against.

The same seed always builds the same tree, so you can reproduce any failure
you see in CI on your own machine:

    python3 scripts/make_fixture.py --seed 12345 --out /tmp/t
    ./report.sh /tmp/t

CI uses a seed that changes every run. That is deliberate: a script that
hardcodes the answers for the sample tree will pass at home and fail when it
is marked. Write something that actually looks at the directory.
"""

import argparse
import os
import random
import shutil
from pathlib import Path

EXTS = [".txt", ".py", ".log", ".md", ".sh", ".json", ".csv", ".yml"]
WORDS = ["alpha", "beta", "gamma", "delta", "report", "notes", "data", "run",
         "build", "index", "main", "utils", "config", "readme", "output"]


def build(seed: int, out: Path) -> None:
    rng = random.Random(seed)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    # A handful of directories, some nested.
    dirs = [out]
    for _ in range(rng.randint(3, 6)):
        parent = rng.choice(dirs)
        d = parent / rng.choice(WORDS)
        if d.exists():
            continue
        d.mkdir()
        dirs.append(d)

    # Distinct sizes, so "the three largest" has one unambiguous answer.
    sizes = rng.sample(range(120, 9000), rng.randint(12, 20))
    made = []
    for size in sizes:
        d = rng.choice(dirs)
        name = rng.choice(WORDS) + rng.choice(EXTS)
        p = d / name
        n = 1
        while p.exists():
            p = d / (rng.choice(WORDS) + str(n) + rng.choice(EXTS))
            n += 1
        p.write_bytes(b"x" * size)
        made.append(p)

    # A few files with no extension at all - these are excluded from the
    # extension count, and catching that is part of the exercise.
    for _ in range(rng.randint(1, 3)):
        d = rng.choice(dirs)
        p = d / ("NOTICE" + str(rng.randint(1, 99)))
        p.write_bytes(b"y" * rng.randint(50, 400))
        made.append(p)

    # Make some of them executable.
    for p in rng.sample(made, rng.randint(2, 4)):
        os.chmod(p, 0o755)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    build(args.seed, Path(args.out))
    print(f"fixture built at {args.out} (seed {args.seed})")


if __name__ == "__main__":
    main()
