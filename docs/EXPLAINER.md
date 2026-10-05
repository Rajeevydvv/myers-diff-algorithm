# EXPLAINER.md: ye sab kaise kaam karta hai

Code exam mein tumhare **apne code** ke baare mein poochha jayega. Ye file `src/main.py` ko function-by-function samjhati hai.

## 1. Poori tasveer

```
main()
 ├─ read_lines()          bytes padho, \n pe split, last khali piece hatao
 ├─ run_lines()           Part A
 │   └─ build_blocks()
 │       └─ match_lines()     lines -> ints, trim, filter
 │           └─ myers_snakes()  -> _solve() -> middle_snake()
 └─ run_highlight()       Part B
     ├─ build_blocks()    (wahi Part A wala)
     └─ highlight_pair()  chars pe myers_snakes() dubara
```

Ek hi diff engine (`myers_snakes`) dono jagah use hota hai: lines pe aur characters pe. Wo kisi bhi sequence pe chalta hai jahan `==` kaam kare.

## 2. Edit graph aur snake

A = `abcabba` (x-axis), B = `cbabac` (y-axis).

- Right step = A ki line delete
- Down step = B ki line insert
- Diagonal step = `a[x] == b[y]`, free (keep)
- **Snake** = ek ke baad ek diagonal steps ka chain
- Diagonal number `k = x - y`

Lakshya: `(0,0)` se `(N,M)` tak ka sabse kam non-diagonal steps wala raasta. Wo kam-se-kam `D` edits.

## 3. V array ka trace (exam ke liye yaad rakho)

`V[k]` = diagonal `k` par sabse door ka `x`, `d` edits ke baad. Classic (forward-only) Myers paper wale example pe (`abcabba` vs `cbabac`):

| d | V[k] (k: x) |
|---|---|
| 0 | 0: 0 |
| 1 | -1: 0, 1: 1 |
| 2 | -2: 2, 0: 2, 2: 3 |
| 3 | -3: 3, -1: 4, 1: 5, 3: 5 |
| 4 | -4: 3, -2: 4, 0: 5, 2: 7, 4: 7 |
| 5 | -5: 3, -3: 4, -1: 5, 1: **7**, 3: 8, 5: 8 |

`d = 5`, `k = 1`: `x = 7 = N` aur `y = x - k = 6 = M`. Kinara mil gaya, to **D = 5**.

Har `d` pe har `k` ke liye (code mein `middle_snake` ke andar):

1. Pichle `d` se do raaste: `k-1` se right (x+1) ya `k+1` se down (x wahi). Jo zyada door ho wo lo: `x = right if left < right else left + 1` (yahan `left = V[k-1]`, `right = V[k+1]`).
2. `y = x - k`.
3. **Snake chalo**: `while a[x] == b[y]: x += 1; y += 1`. (Ye wahi line hai jo exam mein "snake ke baad wali line" ke liye poochi ja sakti hai: `vf[i] = x`.)
4. `V[k] = x` store karo.

## 4. Linear space: middle snake

Upar wala version har `d` ka `V` yaad rakhta to memory `O(D^2)`. Mera code:

- `vf` forward se, `vb` reverse se (dono ek ek array, size ~ `N+M`).
- Dono `d = 0, 1, 2, ...` ke saath badhte hain. Reverse ke liye sequences ulti (`ra`, `rb`) rakhi hain.
- `delta = N - M`. Agar `delta` **odd** hai to overlap forward pass mein pakda jata hai (check: `x + vb[delta-k] >= N`), warna reverse pass mein. Isse `D = 2d-1` ya `2d`.
- Overlap = **middle snake**. Wo `(x1,y1)` se `(x2,y2)` tak.
- Phir `_solve` left part `a[:x1], b[:y1]` aur right part `a[x2:], b[y2:]` pe khud ko call karta hai. Beech ki snake seedhi match list mein.

Recursion ki depth ~ `log D` hai, kyunki har level pe `D` aadha. Time `O(ND)`, memory `O(N)`.

`_solve` pehle common prefix aur suffix hata deta hai. Uske baad pakka `D >= 2` hota hai (dono pehli lines alag, dono aakhri lines alag), isliye recursion rukti hai.

`-1` ka matlab "is diagonal pe abhi koi nahi pahuncha". Ye sentinel edge diagonals ko khud sahi neighbour chunwa deta hai.

## 5. Part A ke speed tricks (`match_lines`)

1. `table.setdefault(line, len(table))`: har alag line ko ek int id. Bytes ki jagah ints compare hote hain.
2. Common prefix/suffix trim.
3. `in_a`, `in_b`: jo line sirf ek hi file mein hai wo kabhi match nahi ho sakti, to use Myers ko dena hi nahi. LCS wahi rehta hai, `N` bahut chhota ho jata hai. Baad mein `ia`/`ib` se original indices wapas.

Result: matched pairs `(i, j)`.

## 6. Delete-first rule kaise guarantee hota hai

`build_blocks` matched pairs ke beech ke gaps ko ek `change` block bana deta hai (`A[i0:i1]`, `B[j0:j1]`). `run_lines` pehle saari `-`, phir saari `+` likhta hai. Myers ka raasta kuch bhi ho, order yahin tay hota hai. **Behaviour badalna ho** (jaise `+` pehle) to sirf `run_lines` ke do `for` loops swap karne hain.

## 7. Part B: highlight

`run_highlight` har change block mein:

- `-` lines likhta hai.
- `+` lines likhta hai, aur agar us index ki `-` line bhi hai (`i0 + t < i1`) to turant uske baad `? ...` line.

`highlight_pair`:

1. UTF-8 decode, to code points milte hain (emoji = 1 character).
2. Common prefix `p` aur suffix `s` string pe hi nikaalo.
3. Agar beech ka hissa ek taraf khali hai to seedhi range. Warna `myers_snakes` beech wale characters pe.
4. `unmatched_ranges`: snakes ke beech ke gaps = changed ranges. Adjacent gaps khud ek ho jaate hain (isliye `3-7`, `3-5,5-7` nahi).
5. `format_ranges`: `.` agar khali, warna `s-e,s-e`.

Highlighted count = `N + M - 2*LCS`, jo minimum hai kyunki LCS maximum hai.

## 8. Edge cases jo handle hain

| Case | Kaise |
|---|---|
| Empty file | `split` se `[b""]`, last khali hata do, `[]` |
| `a\n` vs `a` | Dono `["a"]`, same |
| `\r\n` | `\r` line ka hissa, `a\r` aur `a` alag lines |
| Invalid UTF-8 (lines) | Kabhi decode nahi hota, bytes compare |
| File na khule | stderr message, stdout khali, `return 2` |
| Identical files | Sab prefix trim ho jata hai, sirf keep lines |

## 9. Exam ke possible sawaal

- *V array trace karo chhote input pe*: section 3 ki table jaisa, `d` ke saath `k` range `-d..d` step 2.
- *Snake ke baad kaunsi line?*: `vf[i] = x` (aur uske baad overlap check).
- *Overlap kab check hota hai?*: `delta` odd to forward pass mein, even to reverse mein.
- *Behaviour badalna*: delete-first ko insert-first (`run_lines`), ya highlight pairing badalna (`run_highlight`), ya prefix/suffix trim hatana.
- *Linear space kyun?*: `O(D^2)` memory se bachne ke liye.
- *Unique line hatane se minimality kyun nahi tootti?*: wo line kabhi LCS mein aa hi nahi sakti.

## 10. Limits (sach mein)

Myers `O(ND)` hai. Agar files mein bahut repeated lines hon aur `D` bahut bada (hazaaron) ho to Python mein dheema ho sakta hai. Mere sandbox pe: 100k lines, 20 distinct values, 5000 edits = ~7 s (limit 5 s). Public tests ke performance groups `cpsdiff test` mein dekho.
