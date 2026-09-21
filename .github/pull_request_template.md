## Week 2 submission

Title: `Week 2 — <your-github-username>`

- [ ] My script is at `submissions/<my-github-username>/report.sh`
- [ ] I changed only files inside my own folder
- [ ] `chmod +x` — it is executable (the marker checks, and says so if not)
- [ ] I ran it against at least two different seeds before pushing

---

**Red check?** Click **Details**. The marker prints which of the four sections
failed, why, and the seed it used. Reproduce it exactly:

```bash
python3 scripts/make_fixture.py --seed <seed from the log> --out /tmp/t
./report.sh /tmp/t
```

Fix, commit, push. The check re-runs by itself. A red check costs you nothing.
