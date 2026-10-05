# SUBMIT.md: Windows pe step-by-step

Deadline: **Tuesday 6 Oct 2026, 20:00 IST**. Allowance: 10 submissions, har 30 min mein 1 naya, do submits ke beech 10 s ka gap. Pehle `cpsdiff test` (free) chalao.

## A. Ek baar ka setup (PowerShell)

```powershell
irm https://f33759e3f7c9c273d83e7c1287d2e0fd.up.railway.app/install.ps1 | iex
cpsdiff --version          # naya terminal kholke
cpsdiff login su-xxxxx     # student id + email wala 8-char code
```

## B. Project banao

1. GitHub pe **private** repo, naam bilkul `myers-diff-algorithm`, khali (README nahi).
2. PowerShell:

```powershell
mkdir myers-diff-algorithm
cd myers-diff-algorithm
cpsdiff init --lang python
```

3. Meri files copy karo:
   - `src/main.py` ko `myers-diff-algorithm\src\main.py` pe **overwrite** karo (starter file replace hogi)
   - `docs\` aur `tools\` folders project ke andar rakh do
   - `myers.toml` **mat chhedo/delete karo**

## C. Test, commit, push

```powershell
cpsdiff test
git add .
git commit -m "Implement Myers diff with linear-space middle snake"
git remote add origin https://github.com/<your-github-username>/myers-diff-algorithm.git
git push -u origin main
```

(Pehle commit se pehle `git add . && git commit -m "Add starter files for the Myers diff assignment"` bhi theek hai, guide ke hisaab se.)

## D. Submit

```powershell
cpsdiff submit      # files list dikhegi, y type karo
cpsdiff status
```

- **Pehli baar**: box mein naam/roll number/email/repo dikhega aur "CANNOT BE CHANGED LATER" likha hoga. Dhyan se check karo.
- Commit message imperative subject line ho ("Fix ...", "Speed up ...").
- Result mein sirf PASS/FAIL aur timing dikhti hai, marks nahi.
- Best submission count hoti hai.

## E. Submit ke baad (code exam ke liye)

1. Repo **public** karo: GitHub, Settings, General, Danger zone, Change visibility. Deadline ke baad hi, kyunki tab tak private rakhna hai.
2. Repo ka link university assessment platform pe submit karo.
3. `docs\EXPLAINER.md` padh ke exam ki taiyari karo (V array trace, snake ke baad ki line, behaviour badalna).

## Checklist

- [ ] `cpsdiff test` sab PASS
- [ ] `git status` clean, `git push` ho gaya
- [ ] `cpsdiff submit` accepted (20:00 IST se pehle)
- [ ] `cpsdiff status` mein result dekha
- [ ] Repo public + link platform pe
