"""diag13: decode the two homies records + 面包车耐久, compute true->screen
charlist-index deltas from the user's authoritative garble transcription,
and inspect the format-code structure of each record.
"""
import sys, struct, re
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp

PATCH = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'

patch = Vpp(PATCH)

# ---- charlist (newline-separated codepoints, //ENDOFFILE terminator) ----
cl = patch.find('charlist_CH', 'txt')
clbuf = patch.read(cl)
text = clbuf.decode('ascii', 'replace')
end = text.find('//ENDOFFILE')
if end < 0:
    end = len(text)
CPS = [int(x) for x in text[:end].split() if x.isdigit()]
CP2IDX = {cp: i for i, cp in enumerate(CPS)}
print('charlist_CH entries:', len(CPS), 'first', CPS[:5], 'max', max(CPS))

def slot_to_cp(v):
    if v < 0x80:
        return v
    idx = v - 0x20
    if 0 <= idx < len(CPS):
        return CPS[idx]
    return None

# ---- le_strings parser ----
def parse_le(blob):
    magic, ver, nb, count = struct.unpack_from('<IHHI', blob, 0)
    A0 = 12 + nb * 8
    ptrs = [struct.unpack_from('<I', blob, A0 + i * 4)[0] for i in range(count)]
    recs = {}
    for p in ptrs:
        id1, id2 = struct.unpack_from('<HH', blob, p)
        h = (id1 << 16) | id2
        units = []
        o = p + 4
        while True:
            u = struct.unpack_from('>H', blob, o)[0]
            o += 2
            if u == 0:
                break
            units.append(u)
        recs[h] = units
    return recs, nb, count

st = patch.find('static_CH', 'le_strings')
stblob = patch.read(st)
recs, nb, count = parse_le(stblob)
print('static_CH nb=%d count=%d' % (nb, count))

# find 面包车耐久 record
def find_text(recs, needle):
    out = []
    for h, units in recs.items():
        txt = []
        for u in units:
            cp = slot_to_cp(u)
            txt.append(chr(cp) if cp is not None else '?')
        s = ''.join(txt)
        if needle in s:
            out.append((h, s))
    return out

print('面包车耐久 occurrences:', [(hex(h), s) for h, s in find_text(recs, '面包车耐久')])

# ---- decode target records ----
targets = {
    0x84F287ED: '任璨偶巧位雄衡任璨伪该',
    0x10AF1E62: '任璨偶巧位校衡勾远藐乱携 伪该亡位通像匪冰挺拮',
}

for h, screen in targets.items():
    units = recs.get(h)
    if units is None:
        print('MISSING', hex(h)); continue
    print('\n=== hash', hex(h), 'nunits', len(units))
    # build true text + flag ascii (format codes)
    true_chars = []
    segs = []  # (kind, text) kind: 'cjk' or 'ascii'
    for u in units:
        cp = slot_to_cp(u)
        if cp is None:
            true_chars.append('?'); continue
        if cp < 0x80:
            true_chars.append(chr(cp))
        else:
            true_chars.append(chr(cp))
    truetext = ''.join(true_chars)
    print('TRUE :', truetext)
    print('SCREEN:', screen)
    # positional mapping, ignoring ascii-only positions for the cjk mapping
    # walk both: align by consuming ascii runs identically
    # Build decoded list with kind
    decoded = []
    for u in units:
        cp = slot_to_cp(u)
        if cp is None:
            decoded.append(('?', u)); continue
        if cp < 0x80:
            decoded.append(('a', chr(cp)))   # ascii
        else:
            decoded.append(('c', chr(cp)))   # cjk
    # extract cjk-only true sequence and cjk-only screen sequence
    true_cjk = [d[1] for d in decoded if d[0] == 'c']
    # screen has spaces; treat non-space as cjk-ish garble
    screen_cjk = [c for c in screen if c != ' ']
    print('true_cjk len', len(true_cjk), 'screen_cjk len', len(screen_cjk))
    # compute deltas for cjk positions
    deltas = []
    for tc, sc in zip(true_cjk, screen_cjk):
        ti = CP2IDX.get(ord(tc))
        si = CP2IDX.get(ord(sc))
        if ti is None:
            deltas.append((tc, sc, 'TRUE_NOT_IN_CL', si)); continue
        if si is None:
            deltas.append((tc, sc, ti, 'SCR_NOT_IN_CL')); continue
        deltas.append((tc, sc, ti, si, si - ti))
    for d in deltas:
        print('  %s->%s  true_idx=%s scr_idx=%s delta=%s' % (d[0], d[1], d[2], d[3], d[4] if len(d) == 5 else d[4]))
    # also show raw ascii structure (format codes)
    ascii_runs = []
    cur = ''
    for k, d in enumerate(decoded):
        if d[0] == 'a':
            cur += d[1]
        else:
            if cur:
                ascii_runs.append(cur); cur = ''
    if cur:
        ascii_runs.append(cur)
    print('  ascii runs (format codes):', ascii_runs)
