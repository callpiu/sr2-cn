import struct, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
v = Vpp(G + 'patch.vpp_pc')
blob = v.read(v.find('static_CH', 'le_strings'))
CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))

def D(sl):
    return ''.join(chr(CL[x - 0x20]) if 0x20 <= x - 0x20 < len(CL) else '^%02X' % x for x in sl)

def scan(b):
    res = []
    i = 0
    while i + 2 <= len(b):
        j = i
        out = []
        while j + 2 <= len(b):
            x = struct.unpack_from('>H', b, j)[0]
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
    return res

CH = scan(blob)

# NOTICE 在 CH 表里对应什么
print('=== ID 304150F3 / F72DF00A 在 CH 表里 ===')
for off, o in CH:
    if len(o) < 3:
        continue
    h = '%08X' % ((o[0] << 16) | o[1])
    if h in ('304150F3', 'F72DF00A'):
        print('  %s  %r' % (h, D(o[2:])))

print()
print('=== CH 表里 2-6 字、像界面提示语的短 label（含"提示"）===')
n = 0
for off, o in CH:
    if len(o) < 3:
        continue
    t = D(o[2:]).strip()
    if 2 <= len(t) <= 4 and ('提示' in t or '注意' in t or '告知' in t):
        n += 1
        print('  %08X ID=%08X  %r' % (off, (o[0] << 16) | o[1], t))
print('total', n)

print()
print('=== CH 表里 "等待" 开头的短 label（可作 body 候选）===')
for off, o in CH:
    if len(o) < 3:
        continue
    t = D(o[2:]).strip()
    if t.startswith('等待') and len(t) <= 12:
        print('  %08X ID=%08X  %r' % (off, (o[0] << 16) | o[1], t))