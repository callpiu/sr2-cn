import struct, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

v = Vpp('F:/sr2-cn/_ref_第三方补丁/原始基准/patch_第三方原版.vpp_pc')
blob = v.read(v.find('static_US', 'le_strings'))

res = []
i = 0
while i + 2 <= len(blob):
    j = i
    out = []
    while j + 2 <= len(blob):
        x = struct.unpack_from('>H', blob, j)[0]
        if x == 0:
            break
        out.append(x)
        j += 2
        if len(out) > 600:
            break
    if out:
        res.append((i, out))
        i = j + 2
    else:
        i += 2

def A(sl):
    return ''.join(chr(x) if 32 <= x < 0x7f else '' for x in sl)

print('=== US: 含 SPLASH 的记录 ===')
c = 0
for off, o in res:
    t = A(o[2:] if len(o) > 2 else o)
    if 'SPLASH' in t.upper():
        c += 1
        print('%08X  ID=%08X  slots=%d  %r' % (off, (o[0] << 16) | o[1], len(o), t[:110]))
print('total', c)

print()
print('=== US: 含 LAN 的记录（短） ===')
c = 0
for off, o in res:
    t = A(o[2:] if len(o) > 2 else o)
    if len(t) < 50 and 'LAN' in t.upper():
        c += 1
        if c <= 30:
            print('%08X  ID=%08X  %r' % (off, (o[0] << 16) | o[1], t))
print('total', c)

print()
print('=== 中文表里含「 cooperation / 合作 / 联机 / 说明」的记录（找对应译文） ===')
G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
v2 = Vpp(G + 'patch.vpp_pc')
blob2 = v2.read(v2.find('static_CH', 'le_strings'))
CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))

def D(sl):
    return ''.join(chr(CL[x - 0x20]) if 0x20 <= x - 0x20 < len(CL) else '^%02X' % x for x in sl)

res2 = []
i = 0
while i + 2 <= len(blob2):
    j = i
    out = []
    while j + 2 <= len(blob2):
        x = struct.unpack_from('>H', blob2, j)[0]
        if x == 0:
            break
        out.append(x)
        j += 2
        if len(out) > 600:
            break
    if out:
        res2.append((i, out))
        i = j + 2
    else:
        i += 2

print('CH records', len(res2))
for kw in ['合作', '联机', '说明', '小队', '玩家须知']:
    hits = [(o, D(x[2:] if len(x) > 2 else x)) for o, x in res2 if kw in D(x[2:] if len(x) > 2 else x)]
    print('  %s -> %d' % (kw, len(hits)))
    for o, t in hits[:6]:
        print('     %08X ID=%08X %s' % (o, (x[0] << 16) | x[1] if False else 0, t[:90]))