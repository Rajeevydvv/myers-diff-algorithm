# DESIGN.md: algorithm ka design

## Big idea

Diff = **LCS (longest common subsequence)** dhundhna. Jo lines LCS mein nahi hain wo delete (A se) ya insert (B se). Minimal diff matlab LCS maximum.

Isliye program do alag stages mein bata hai:

1. **Matching nikalo**: kaun si line A ki kaun si line B se match hui (Myers).
2. **Output banao**: matches ke beech ke gaps ko change block maan ke pehle `-` phir `+` print karo.

Is split ka fayda: *delete-first rule* algorithm pe depend nahi karta. Chahe Myers kisi bhi tarah path chune, output stage hamesha `-` pehle likhta hai.

## Myers' algorithm (short mein)

- Edit graph: x = A mein position, y = B mein position. Right = delete, down = insert, diagonal = match (free).
- `D` = edits ki sankhya. Har `d` ke liye har diagonal `k = x - y` par sabse door pahunchne wala `x` rakhte hain: array `V[k]`.
- **Snake** = diagonal pe jitna chal sako (jab `a[x] == b[y]`).
- Time `O(ND)`.

## Linear space (middle snake)

Normal Myers har `d` ka `V` store karta hai (`O(D^2)` memory). Bade D pe memory phat jati hai. Isliye:

- Forward search (start se) aur reverse search (end se) **ek saath** chalate hain, `D/2` steps tak.
- Jab dono overlap karein => **middle snake** mil gaya.
- Phir left half aur right half pe recursion (divide and conquer).
- Memory `O(N)`, time `O(ND)`, recursion depth ~ `log D`.

## Speed tricks (Python ke liye zaroori)

| Trick | Kyun safe hai |
|---|---|
| Lines ko integer ids mein badlo (dict interning) | int compare bytes compare se fast |
| Common prefix/suffix trim | Unme koi edit kabhi LCS nahi todta |
| Wo lines hata do jo dusre file mein hain hi nahi | Aisi line kabhi match nahi ho sakti, LCS same rehta hai |
| Har recursion mein bhi prefix/suffix trim | Chhote subproblem jaldi khatam |

## Part B

Har change block mein k-th `-` ko k-th `+` se pair karo. Dono lines ko Unicode code points mein todo, **wahi diff function** characters pe chalao. Jo characters match nahi hue unki ranges (`start-end`, end exclusive) banao. Unmatched characters ki sankhya LCS se minimum hoti hai, aur adjacent ranges apne aap merge ho jati hain.

## Files

```
src/main.py       sab kuch (reader, diff, output, CLI)
tools/            brute-force checker, test generator, timing
docs/             ye md files
```
