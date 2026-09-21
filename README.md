# INF 345 — Week 2 Practice

**Linux, and a script that a machine marks**

Deadline: **Sunday 27 September, 23:59** Almaty time. Your last commit before
then is what gets marked.

---

## Two halves

The first twenty minutes are drills in your own terminal. Nothing is marked and
nothing is submitted — the point is to get the commands under your fingers.

The rest is one script, `report.sh`, which is marked automatically.

**Your laptop does not have to be Linux.** The marking happens on an Ubuntu
machine in GitHub Actions. Windows, macOS and Linux all get the same marker.

---

# Part 1 — Drills (20 min, not marked)

Open a terminal. On Windows that means **Git Bash**, not PowerShell.

```bash
cd ~                      # go home
pwd                       # where am I, exactly
ls -la                    # everything here, including hidden files, with permissions
mkdir -p playground/sub   # make two levels at once
cd playground
```

Make some files and look at them:

```bash
echo "hello" > a.txt          # write a file
echo "world" >> a.txt         # add to it
cat a.txt                     # show it
wc -l a.txt                   # count its lines
cp a.txt sub/b.txt            # copy
ls -l sub/                    # look at the copy's permissions
```

Now the four ideas from the lecture, one at a time:

```bash
# 1. Everything is a file
cat /proc/self/status | head -5      # a file that is not on your disk
ls /etc | head                       # configuration, all of it text

# 2. Processes
ps aux | head -5                     # what is running
sleep 60 &                           # start something in the background
ps aux | grep sleep                  # find it
kill %1                              # stop it

# 3. Permissions
echo 'echo it ran' > hello.sh
./hello.sh                           # Permission denied - expected
chmod +x hello.sh
./hello.sh                           # now it runs
ls -l hello.sh                       # look at what changed

# 4. Pipes
ls /usr/bin | wc -l                  # how many programs are installed
ls /usr/bin | grep python            # which of them mention python
ls /usr/bin | sort | head -3         # first three alphabetically
```

If any of those produce something you did not expect, **say so in the chat now**
— that is what the session is for.

---

# Part 2 — `report.sh` (marked, 100 points)

## What it must do

Take one argument, a directory, and print a report about everything inside it,
at any depth.

```bash
./report.sh /some/directory
```

## Exact output format

```
FILES: 17
DIRS: 4
LARGEST:
8990 report/run/main.log
8113 report/data.txt
7417 report/run/readme.py
EXECUTABLE:
report/run/build.md
report/run/config/data.txt
report/run/config/delta.yml
run/NOTICE12
EXTENSIONS:
3 .csv
3 .md
3 .txt
2 .yml
1 .json
```

Five headings, spelled exactly like that. Under each:

| Section | 25 points for |
|---|---|
| `FILES` / `DIRS` | the number of regular files, and the number of directories *below* the one you were given — not counting that directory itself |
| `LARGEST` | the three largest files, biggest first, as `<bytes> <path>` |
| `EXECUTABLE` | every file the owner may run, one path per line, alphabetical |
| `EXTENSIONS` | the five commonest extensions as `<count> .<ext>`, commonest first |

Details that the marker checks:

- **Sizes are in bytes.** `du` reports disk blocks, which is a different number.
- **Paths are relative** to the directory you were given. A leading `./` is fine.
- **Files with no extension** are not counted in `EXTENSIONS`.
- **Ties are fine.** If four extensions all appear three times, any order among
  them is accepted, and any of them may take the last slot.

## Try it before you push

```bash
python3 scripts/make_fixture.py --seed 1 --out /tmp/tree
./report.sh /tmp/tree
```

Seed 1 produces exactly the output shown above, so you can compare directly.
To mark yourself the same way CI will:

```bash
python3 scripts/grade.py --script submissions/<your-username>/report.sh --seed 1
```

**Change the seed and try again.** CI uses a seed nobody can predict, so a
script that prints the right answer for seed 1 and nothing else will fail. That
is on purpose.

---

## Submitting

Same shape as week 1: fork, branch, commit, pull request.

```bash
git clone https://github.com/<your-username>/inf345-week2-lab.git
cd inf345-week2-lab
git checkout -b week2-<your-username>

cp -r submissions/EXAMPLE submissions/<your-username>
chmod +x submissions/<your-username>/report.sh
# ... write your script ...

git add submissions/<your-username>/report.sh
git commit -m "Week 2: report.sh"
git push origin week2-<your-username>
```

Then open a pull request against this repository and watch the check.

### Two things that catch Windows users

**The executable bit.** Git stores whether a file may be run, and on Windows
`chmod +x` sometimes does not make it into the commit. If the marker says your
script is not executable even though it runs fine at home:

```bash
git update-index --chmod=+x submissions/<your-username>/report.sh
git commit -m "Make report.sh executable"
git push
```

**Line endings.** Already handled — this repository has a `.gitattributes` that
forces Unix line endings on `.sh` files. Open it and read the comment; it
explains the error you would otherwise have spent an evening on.

---

## Marking

100 points, four sections of 25. You can push as many times as you like before
the deadline — a red check costs nothing. The marker prints exactly which
section failed and why, and gives you the seed so you can reproduce it:

```bash
python3 scripts/make_fixture.py --seed <the seed from the log> --out /tmp/t
./report.sh /tmp/t
```

You may read [`scripts/grade.py`](scripts/grade.py). It is the rubric; there is
nothing hidden in it. Reading the thing that marks you is a legitimate way to
understand what is being asked, and it is how you should treat every pipeline
you meet from now on.

---

## Stuck?

In the session: chat, immediately. Afterwards: email with `INF 345` and your
group in the subject, from your `@sdu.edu.kz` address, with the **link to your
pull request** and the error. Two working days.

Helping each other is encouraged. Sending someone your script is not.
