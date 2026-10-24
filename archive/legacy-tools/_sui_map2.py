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

def A(sl):
    return ''.join(chr(x) if 32 <= x < 0x7f else '' for x in sl)

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

T = {'A935FCF3', '7AB46909', '474361DB', '7898FE46', '699F72DA',
     '922DDF58', '39C7759B', '12012AE5', '3CAB6F69'}

print('=== CH 表 ===')
for off, o in scan(blob):
    if len(o) < 3:
        continue
    h = '%08X' % ((o[0] << 16) | o[1])
    if h in T:
        print('  %s  %r' % (h, D(o[2:])))

print()
print('=== US 表（同一 ID） ===')
v2 = Vpp('F:/sr2-cn/_ref_第三方补丁/原始基准/patch_第三方原版.vpp_pc')
b2 = v2.read(v2.find('static_US', 'le_strings'))
for off, o in scan(b2):
    if len(o) < 3:
        continue
    h = '%08X' % ((o[0] << 16) | o[1])
    if h in T:
        print('  %s  %r' % (h, A(o[2:])[:80]))

print()
print('=== US 表里所有 Notice / Notice 类短 label ===')
for off, o in scan(b2):
    if len(o) < 3:
        continue
    t = A(o[2:]).strip()
    if t in ('Notice', 'NOTICE'):
        print('  ID=%08X  %r' % ((o[0] << 16) | o[1], t))