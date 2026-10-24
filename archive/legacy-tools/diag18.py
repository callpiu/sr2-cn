"""diag18: the center SUBTITLE garbles but the objective PANEL (reads static_CH
0x84F287ED) now renders my change correctly. So the subtitle reads a DIFFERENT
source. Find EVERY record (all le_strings tables + loose Mods/DLC files) whose
slot-decoded text contains the homies wording, to locate the subtitle's source."""
import sys, struct, glob, os
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
PATCH = os.path.join(GAME, 'patch.vpp_pc')
patch = Vpp(PATCH)

clbuf = patch.read(patch.find('charlist_CH', 'txt'))
text = clbuf.decode('ascii', 'replace')
end = text.find('//ENDOFFILE')
CPS = [int(x) for x in text[:end].split() if x.isdigit()]

def dec_units(units):
    out = []
    for u in units:
        if u < 0x80:
            out.append(chr(u))
        else:
            idx = u - 0x20
            out.append(chr(CPS[idx]) if 0 <= idx < len(CPS) else '?')
    return ''.join(out)

def parse_le(blob):
    magic, ver, nb, count = struct.unpack_from('<IHHI', blob, 0)
    if magic != 0xA84C7F73:
        return None
    A0 = 12 + nb * 8
    ptrs = [struct.unpack_from('<I', blob, A0 + i * 4)[0] for i in range(count)]
    recs = []
    for off in ptrs:
        if not (0 < off <= len(blob) - 6):
            continue
        id1, id2 = struct.unpack_from('<HH', blob, off)
        h = (id1 << 16) | id2
        units = []
        o = off + 4
        while o + 2 <= len(blob):
            u = struct.unpack_from('>H', blob, o)[0]; o += 2
            if u == 0: break
            units.append(u)
        recs.append((h, dec_units(units)))
    return recs

NEEDLES = ['弟兄们', '需要你的保护', '谈几笔生意', '免遭袭击']

# 1) all le_strings inside patch.vpp_pc
sources = []
for e in patch.entries():
    if e['ext'].lower() == 'le_strings':
        sources.append(('patch:' + e['name'], patch.read(e)))

# 2) loose Mods + DLC le_strings
for pat in [os.path.join(GAME, 'Mods', '**', '*.le_strings'),
            os.path.join(GAME, 'DLC', '**', '*.le_strings')]:
    for f in glob.glob(pat, recursive=True):
        sources.append(('file:' + os.path.relpath(f, GAME), open(f, 'rb').read()))

print('scanning %d sources for needles %s' % (len(sources), NEEDLES))
for label, blob in sources:
    recs = parse_le(blob)
    if recs is None:
        continue
    for h, s in recs:
        if any(n in s for n in NEEDLES):
            # flag the two target hashes
            tag = ''
            if h in (0x84F287ED, 0x10AF1E62):
                tag = '  <<< TARGET HASH'
            print('%-42s %08X  %r%s' % (label, h, s, tag))
