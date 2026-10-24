"""diag16: dump exact unit stream of the two homies records with positions,
so we can cross-check the user's screen transcription without alignment guesses.
Also cross-check REC1 vs REC2 shared-char mappings precisely."""
import sys, struct
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp

PATCH = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
patch = Vpp(PATCH)

# charlist
clbuf = patch.read(patch.find('charlist_CH', 'txt'))
text = clbuf.decode('ascii', 'replace')
end = text.find('//ENDOFFILE')
CPS = [int(x) for x in text[:end].split() if x.isdigit()]

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
            u = struct.unpack_from('>H', blob, o)[0]; o += 2
            if u == 0: break
            units.append(u)
        recs[h] = units
    return recs

recs = parse_le(patch.read(patch.find('static_CH', 'le_strings')))

def decode(units):
    out = []
    for u in units:
        if u < 0x80:
            out.append(('a', u, chr(u)))
        else:
            idx = u - 0x20
            cp = CPS[idx] if 0 <= idx < len(CPS) else None
            out.append(('c', idx, chr(cp) if cp else '?'))
    return out

for h in (0x84F287ED, 0x10AF1E62):
    units = recs[h]
    d = decode(units)
    print('\n=== %s  nunits=%d' % (hex(h), len(units)))
    line = []
    for k, (kind, v, ch) in enumerate(d):
        if kind == 'c':
            line.append('[%02d]%s(idx%d)' % (k, ch, v))
        else:
            line.append('<%s>' % ch)
    print('  '.join(line))

# Build per-char maps for each record from the CJK positions and the user's
# screen transcription (corrected alignment: REC2 space dropped).
REC1_scr = '任璨偶巧位雄衡任璨伪该'
REC2_scr = '任璨偶巧位校衡勾远藐乱携伪该亡位通像匪冰挺拮'  # space dropped

def charmap(h, scr):
    d = decode(recs[h])
    cjk = [(v, ch) for (kind, v, ch) in d if kind == 'c']
    assert len(cjk) == len(scr), (len(cjk), len(scr))
    m = {}
    for (idx, true_ch), s in zip(cjk, scr):
        m.setdefault(true_ch, []).append((idx, s))
    return m

m1 = charmap(0x84F287ED, REC1_scr)
m2 = charmap(0x10AF1E62, REC2_scr)
print('\nshared-char cross-check (true_char: REC1_screen / REC2_screen):')
for ch in m1:
    s1 = m1[ch][0][1]
    s2 = m2[ch][0][1] if ch in m2 else '(absent)'
    flag = '' if s1 == s2 else '   <<< DIFFERS'
    print('  %s : %s / %s%s' % (ch, s1, s2, flag))
