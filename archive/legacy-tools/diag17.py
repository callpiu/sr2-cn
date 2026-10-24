"""diag17: compare US vs CH raw units for the two homies hashes (esp. format
tags), and census how static_CH uses [format]/[/format]/[color:...] tags.
Hypothesis: CH translation injected non-standard format tags that push the
engine into a broken rendering path (stateful), explaining per-record garble."""
import sys, struct, re, collections
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp

PATCH = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
patch = Vpp(PATCH)

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

stUS = parse_le(patch.read(patch.find('static_US', 'le_strings')))
stCH = parse_le(patch.read(patch.find('static_CH', 'le_strings')))

def to_text_units(units):
    # render units as a readable string; ASCII as-is, CJK slot as <idx:c>
    out = []
    for u in units:
        if u < 0x80:
            out.append(chr(u))
        else:
            idx = u - 0x20
            cp = CPS[idx] if 0 <= idx < len(CPS) else None
            out.append(chr(cp) if cp else ('<idx%d>' % idx))
    return ''.join(out)

def raw_ascii(units):
    # only the ASCII (format tag) characters, to compare tags cleanly
    return ''.join(chr(u) for u in units if u < 0x80)

for h in (0x84F287ED, 0x10AF1E62):
    print('\n=== %s ===' % hex(h))
    print('US full :', repr(to_text_units(stUS[h])))
    print('CH full :', repr(to_text_units(stCH[h])))
    print('US tags :', repr(raw_ascii(stUS[h])))
    print('CH tags :', repr(raw_ascii(stCH[h])))

# census of tag usage across static_CH vs static_US
def tag_census(recs, label):
    fmt = collections.Counter()
    colors = collections.Counter()
    n_with = 0
    for h, units in recs.items():
        s = raw_ascii(units)
        if '[' in s:
            n_with += 1
        for m in re.findall(r'\[/?[a-zA-Z]+\]', s):
            fmt[m] += 1
        for m in re.findall(r'\[color:[^\]]*\]', s):
            # classify: word vs hex
            inner = m[len('[color:'):-1]
            if re.fullmatch(r'[0-9A-Fa-f]{6}', inner):
                colors['hex:' + inner.upper()] += 1
            else:
                colors['word:' + inner] += 1
    print('\n[%s] records with [ : %d / %d' % (label, n_with, len(recs)))
    print('  tags:', fmt.most_common(20))
    print('  color formats (top):', colors.most_common(20))

tag_census(stUS, 'static_US')
tag_census(stCH, 'static_CH')
