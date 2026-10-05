# PROGRESS.md: build ka log

| Step | Status | Notes |
|---|---|---|
| Plan + design docs | Done | `PLAN.md`, `DESIGN.md` |
| Part A: `lines` | Done | Linear-space Myers + prefix/suffix trim + unique-line removal |
| Part B: `highlight` | Done | Wahi Myers, characters pe; fast path for prefix/suffix |
| Random testing vs DP | Done | 400 lines tests + 400 highlight tests, sab pass |
| Assignment examples | Done | Paper example (5 edits), delete-first, port example, pure insertion, emoji, empty, CRLF, missing file (exit 2) |
| Big-file timing | Done | Neeche table |
| Blocked-construct scan | Done | `src/` mein koi blocked naam nahi |
| `cpsdiff test` (public tests) | **Tumhare laptop pe karna hai** | Mere paas tool/login nahi hai |
| `cpsdiff submit` | **Tumhare laptop pe karna hai** | Code tumhare login se hi jata hai |
| Repo public + link platform pe | **Baaki** | Code exam se pehle |

## Timing (is sandbox pe, Python 3.13; grader alag machine hai)

| Case | lines | highlight |
|---|---|---|
| 500k unique lines, 2000 edits | 0.8 s | 0.8 s |
| 500k identical | 0.5 s | 0.5 s |
| 500k all different | 0.6 s | 10.3 s (500k paired lines, har pair ka alag diff) |
| 500k lines, 20 distinct values, 300 edits | 1.0 s | 1.0 s |
| 4k lines, 20 distinct, fully random (D bahut bada) | 3.2 s | 3.3 s |
| 100k lines, 20 distinct, 5000 edits | 7.2 s | 6.9 s |

Python limit 5 s hai. Last do rows (bahut zyada repeated lines + bahut zyada edits) heavy hain: Myers `O(ND)` hai aur Python slow. Agar `cpsdiff test` ya submit mein koi performance test time-out dikhaye to naya optimisation karenge (ye docs update honge).

## Optimisations jo lagin

1. Lines ko int ids banaya.
2. Common prefix/suffix trim (top level aur har recursion pe).
3. Jo line dusre file mein hai hi nahi use hata diya (LCS nahi badalta).
4. `-1` sentinel se edge-diagonal checks hatayin, reverse sequences ek baar reverse karke rakhi.
5. Highlight mein: string-level prefix/suffix, aur agar ek taraf kuch bacha nahi to Myers chalaya hi nahi.
