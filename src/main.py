"""Myers diff: minimal line diff (Part A) and character highlights (Part B).

Usage:
    python main.py lines A B
    python main.py highlight A B
"""
import sys


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------

def read_lines(path):
    """Read a file as raw bytes and split it into lines (as bytes)."""
    with open(path, "rb") as f:
        data = f.read()
    parts = data.split(b"\n")
    if parts and parts[-1] == b"":
        parts.pop()
    return parts


# ---------------------------------------------------------------------------
# Myers core (works on any two sequences with == comparison)
# ---------------------------------------------------------------------------

def middle_snake(a, b):
    """Find the middle snake of the edit graph of a and b.

    Returns (x1, y1, x2, y2): the snake runs from (x1, y1) to (x2, y2) in
    forward coordinates (it may have length zero). Both a and b must be
    non-empty and must differ in their first and last element, so D >= 2.
    """
    n = len(a)
    m = len(b)
    delta = n - m
    odd = delta & 1
    max_d = (n + m + 1) // 2
    off = max_d + 1
    size = 2 * max_d + 3
    # vf[off + k]: furthest x on diagonal k going forward.
    # vb[off + k]: same, but for the reverse search (reversed coordinates).
    # -1 marks "not reached yet"; it makes the edge diagonals pick the
    # right neighbour without extra checks.
    vf = [-1] * size
    vb = [-1] * size
    vf[off + 1] = 0
    vb[off + 1] = 0
    ra = a[::-1]
    rb = b[::-1]

    for d in range(max_d + 1):
        # ---- forward pass ----
        lo_chk = delta - (d - 1)
        hi_chk = delta + (d - 1)
        i = off - d
        for k in range(-d, d + 1, 2):
            left = vf[i - 1]
            right = vf[i + 1]
            x = right if left < right else left + 1
            y = x - k
            sx = x
            sy = y
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1
            vf[i] = x
            if odd and lo_chk <= k <= hi_chk:
                if x + vb[off + delta - k] >= n:
                    return sx, sy, x, y
            i += 2
        # ---- reverse pass ----
        i = off - d
        for k in range(-d, d + 1, 2):
            left = vb[i - 1]
            right = vb[i + 1]
            x = right if left < right else left + 1
            y = x - k
            sx = x
            sy = y
            while x < n and y < m and ra[x] == rb[y]:
                x += 1
                y += 1
            vb[i] = x
            if not odd and -d <= delta - k <= d:
                if x + vf[off + delta - k] >= n:
                    return n - x, m - y, n - sx, m - sy
            i += 2
    raise RuntimeError("middle snake not found")  # cannot happen


def _solve(a, b, ao, bo, out):
    """Append matching snakes (a_index, b_index, length) for a vs b to out.

    ao, bo are the offsets of a and b inside the original sequences.
    Snakes are appended in increasing order.
    """
    n = len(a)
    m = len(b)
    # common prefix
    p = 0
    lim = n if n < m else m
    while p < lim and a[p] == b[p]:
        p += 1
    if p:
        out.append((ao, bo, p))
        a = a[p:]
        b = b[p:]
        ao += p
        bo += p
        n -= p
        m -= p
    # common suffix
    s = 0
    lim = n if n < m else m
    while s < lim and a[n - 1 - s] == b[m - 1 - s]:
        s += 1
    if s:
        a = a[:n - s]
        b = b[:m - s]
        n -= s
        m -= s
    if n and m:
        x1, y1, x2, y2 = middle_snake(a, b)
        _solve(a[:x1], b[:y1], ao, bo, out)
        if x2 > x1:
            out.append((ao + x1, bo + y1, x2 - x1))
        _solve(a[x2:], b[y2:], ao + x2, bo + y2, out)
    if s:
        out.append((ao + n, bo + m, s))


def myers_snakes(a, b):
    """Return a list of (a_index, b_index, length) matching blocks (an LCS)."""
    out = []
    _solve(a, b, 0, 0, out)
    return out


# ---------------------------------------------------------------------------
# Part A: line diff
# ---------------------------------------------------------------------------

def match_lines(a_lines, b_lines):
    """Return a list of matched index pairs (i, j) of a minimal diff."""
    table = {}
    a = [table.setdefault(line, len(table)) for line in a_lines]
    b = [table.setdefault(line, len(table)) for line in b_lines]
    na = len(a)
    nb = len(b)

    pairs = []
    # common prefix
    p = 0
    lim = na if na < nb else nb
    while p < lim and a[p] == b[p]:
        p += 1
    for t in range(p):
        pairs.append((t, t))
    # common suffix
    s = 0
    lim = (na if na < nb else nb) - p
    while s < lim and a[na - 1 - s] == b[nb - 1 - s]:
        s += 1

    a_mid = range(p, na - s)
    b_mid = range(p, nb - s)
    in_a = set(a[p:na - s])
    in_b = set(b[p:nb - s])
    # drop lines that cannot match anything on the other side
    ia = [i for i in a_mid if a[i] in in_b]
    ib = [j for j in b_mid if b[j] in in_a]
    ra = [a[i] for i in ia]
    rb = [b[j] for j in ib]

    for (x, y, length) in myers_snakes(ra, rb):
        for t in range(length):
            pairs.append((ia[x + t], ib[y + t]))

    for t in range(s):
        pairs.append((na - s + t, nb - s + t))
    return pairs


def build_blocks(a_lines, b_lines):
    """Yield ('keep', i, j) or ('change', i0, i1, j0, j1) items in order."""
    pairs = match_lines(a_lines, b_lines)
    items = []
    i = 0
    j = 0
    for (mi, mj) in pairs:
        if mi > i or mj > j:
            items.append(("change", i, mi, j, mj))
        items.append(("keep", mi, mj))
        i = mi + 1
        j = mj + 1
    na = len(a_lines)
    nb = len(b_lines)
    if i < na or j < nb:
        items.append(("change", i, na, j, nb))
    return items


def run_lines(a_lines, b_lines):
    out = []
    for item in build_blocks(a_lines, b_lines):
        if item[0] == "keep":
            out.append(b" " + a_lines[item[1]] + b"\n")
        else:
            _, i0, i1, j0, j1 = item
            for i in range(i0, i1):
                out.append(b"-" + a_lines[i] + b"\n")
            for j in range(j0, j1):
                out.append(b"+" + b_lines[j] + b"\n")
    return b"".join(out)


# ---------------------------------------------------------------------------
# Part B: highlight
# ---------------------------------------------------------------------------

def unmatched_ranges(length, matched_blocks, side):
    """Ranges [start, end) of positions not covered by matching blocks.

    side is 0 for the old line, 1 for the new line.
    """
    ranges = []
    pos = 0
    for blk in matched_blocks:
        start = blk[side]
        if start > pos:
            ranges.append((pos, start))
        pos = start + blk[2]
    if pos < length:
        ranges.append((pos, length))
    return ranges


def format_ranges(ranges):
    if not ranges:
        return "."
    parts = []
    for (s, e) in ranges:
        parts.append("%d-%d" % (s, e))
    return ",".join(parts)


def highlight_pair(old_bytes, new_bytes):
    old = old_bytes.decode("utf-8", errors="replace")
    new = new_bytes.decode("utf-8", errors="replace")
    n = len(old)
    m = len(new)
    # common prefix / suffix on the strings themselves (cheap)
    p = 0
    lim = n if n < m else m
    while p < lim and old[p] == new[p]:
        p += 1
    s = 0
    lim -= p
    while s < lim and old[n - 1 - s] == new[m - 1 - s]:
        s += 1
    mid_n = n - p - s
    mid_m = m - p - s
    if mid_n == 0 or mid_m == 0:
        # one side has nothing left in the middle: whole middle is changed
        r_old = [(p, p + mid_n)] if mid_n else []
        r_new = [(p, p + mid_m)] if mid_m else []
    else:
        blocks = myers_snakes(list(old[p:n - s]), list(new[p:m - s]))
        r_old = [(p + x, p + y) for (x, y) in unmatched_ranges(mid_n, blocks, 0)]
        r_new = [(p + x, p + y) for (x, y) in unmatched_ranges(mid_m, blocks, 1)]
    return "? " + format_ranges(r_old) + " | " + format_ranges(r_new) + "\n"


def run_highlight(a_lines, b_lines):
    out = []
    for item in build_blocks(a_lines, b_lines):
        if item[0] == "keep":
            out.append(b" " + a_lines[item[1]] + b"\n")
        else:
            _, i0, i1, j0, j1 = item
            for i in range(i0, i1):
                out.append(b"-" + a_lines[i] + b"\n")
            for t, j in enumerate(range(j0, j1)):
                out.append(b"+" + b_lines[j] + b"\n")
                if i0 + t < i1:
                    out.append(highlight_pair(a_lines[i0 + t], b_lines[j]).encode("ascii"))
    return b"".join(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv):
    if len(argv) != 4 or argv[1] not in ("lines", "highlight"):
        sys.stderr.write("usage: main.py lines|highlight A B\n")
        return 2
    mode, path_a, path_b = argv[1], argv[2], argv[3]
    try:
        a_lines = read_lines(path_a)
        b_lines = read_lines(path_b)
    except OSError as err:
        sys.stderr.write("error: cannot read file: %s\n" % err)
        return 2
    if mode == "lines":
        data = run_lines(a_lines, b_lines)
    else:
        data = run_highlight(a_lines, b_lines)
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    sys.exit(main(sys.argv))
