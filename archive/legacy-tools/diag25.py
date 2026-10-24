"""diag25.py -- 枚举文件里所有 static 量级的 le_strings 块, 解码目标 hash, 看哪份还读成原始乱码"""
import sys, struct, os, hashlib
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp

P = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
data = open(P, 'rb').read()
print('file size =', len(data))

vpp = Vpp(P)
clbuf = vpp.read(vpp.find('charlist_CH', 'txt'))
text = clbuf.decode('ascii', 'replace'); end = text.find('//ENDOFFILE')
CPS = [int(x) for x in text[:end].split() if x.isdigit()]

TARGETS = {0x84F287ED, 0x10AF1E62}
MAGIC = struct.pack('<I', 0xA84C7F73)

occ = []
i = 0
while True:
    j = data.find(MAGIC, i)
    if j < 0: break
    occ.append(j); i = j + 1
print('magic occurrences:', len(occ))

def parse(base):
    if base + 12 > len(data): return None
    magic, ver, nb, count = struct.unpack_from('<IHHI', data, base)
    if magic != 0xA84C7F73: return None
    if not (1 <= nb <= 8192 and 1 <= count <= 13000): return None   # static/voice 量级
    A0 = 12 + nb * 8
    if A0 + count * 4 > len(data) - base: return None
    ptrs = [struct.unpack_from('<I', data, base + A0 + k * 4)[0] for k in range(count)]
    return (nb, count, A0, ptrs)

def decode(rec_abs):
    o = rec_abs + 4; s = ''; g = 0
    while o + 2 <= len(data) and g < 4000:
        u = struct.unpack_from('>H', data, o)[0]; o += 2; g += 1
        if u == 0: break
        s += chr(u) if u < 0x80 else chr(CPS[u - 0x20]) if 0 <= u - 0x20 < len(CPS) else '?'
    return s

# 1) entry 指向的块
ent = vpp.find('static_CH', 'le_strings')
ebody_abs = vpp.data_start + ent['body']
print('\n[ENTRY static_CH] body rel=%d abs=%d size=%d' % (ent['body'], ebody_abs, ent['size']))
r = parse(ebody_abs)
if r:
    nb, count, A0, ptrs = r
    for p in ptrs:
        ra = ebody_abs + p
        id1, id2 = struct.unpack_from('<HH', data, ra)
        h = (id1 << 16) | id2
        if h in TARGETS:
            print('   %08X -> %r' % (h, decode(ra)))
else:
    print('   ENTRY block NOT parseable as le_strings!')

print('\n[ALL static-sized blobs]')
for base in occ:
    r = parse(base)
    if not r: continue
    nb, count, A0, ptrs = r
    hits = {}
    for p in ptrs:
        ra = base + p
        if ra + 4 > len(data): continue
        id1, id2 = struct.unpack_from('<HH', data, ra)
        h = (id1 << 16) | id2
        if h in TARGETS:
            hits[h] = decode(ra)
    if hits:
        print('blob@%d nb=%d count=%d ->' % (base, nb, count), {hex(k): v for k, v in hits.items()})
