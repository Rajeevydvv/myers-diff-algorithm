# PLAN.md: Myers diff assignment ka plan

Language: **Python 3.12+** (grader Python 3.14). Sirf standard library.
Deadline: **Tuesday 6 Oct 2026, 20:00 IST**. Abhi: Monday 5 Oct, ~14:00 IST.

## Kya banana hai

Ek program `src/main.py`, do commands ke saath:

| Command | Kaam | Marks |
|---|---|---|
| `main.py lines A B` | Minimal line diff (` `, `-`, `+` prefix) | 40 |
| `main.py highlight A B` | Same diff + har paired line ke baad `? old \| new` ranges | 20 |
| Code exam (in person) | Apne code ke baare mein sawaal | 40 |

## Hard rules (assignment se)

- File **bytes** mein padhna (`open(path, "rb")`), `\n` pe split, last khali piece drop, `\r` line ka hissa.
- Unreadable file => stdout pe kuch nahi, stderr pe error, **exit code 2**.
- Har change block mein **saare `-` pehle, phir saare `+`**.
- Diff **minimal** hona chahiye (fewest deletions + insertions).
- Performance: ~500,000 lines tak, Python limit **5 s**, memory **768 MiB**.
- Blocked: `difflib`, `subprocess`, `ctypes`, `importlib`, `__import__`, `os.system`, `os.popen`, `os.exec*`, `os.spawn*`. (Comments mein bhi in naamo se bachna, safe side ke liye.)
- Output deterministic ho.

## Steps (ek ek karke)

1. [x] Plan + design docs (`PLAN.md`, `DESIGN.md`)
2. [x] Part A: line diff (linear-space Myers + speed tricks)
3. [x] Part B: character diff + range banana
4. [x] Testing: brute-force DP checker se random tests, bade files pe timing
5. [x] Docs final: `PROGRESS.md`, `TESTING.md`, `SUBMIT.md`, `EXPLAINER.md`
6. [ ] User ke laptop pe: `cpsdiff init`, files copy, `cpsdiff test`, push, `cpsdiff submit`
7. [ ] Repo public karna + link platform pe submit (code exam se pehle)

## Risks

- Python slow hai => unique-line removal + common prefix/suffix trim zaroori.
- Recursion depth: middle-snake recursion ki depth ~ log(D), safe.
- `\r\n` vs `\n` alag lines hain, kabhi normalize nahi karna.
