import struct, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
v = Vpp(G + 'patch.vpp_pc')

CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))
IDX = {}
for i, cp in enumerate(CL):
    IDX.setdefault(cp, i)

def S(w):
    return struct.pack('>H', IDX[ord(w)] + 0x20)

def scan(name):
    blob = v.read(v.find(name, 'le_strings'))
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
    return blob, res

def dec(sl):
    return ''.join(chr(CL[x - 0x20]) if 0x20 <= x - 0x20 < len(CL) else '^%02X' % x for x in sl)

for nm in ['static_CH', 'voice_script_CH', 'platform_pc_CH']:
    blob, res = scan(nm)
    print('===', nm, len(res), 'records')
    for kw in ['等待玩家', '离开游戏', '单人游戏', '等待']:
        pat = b''.join(S(c) for c in kw)
        hits = [(off, o) for off, o in res if pat in struct.pack('>' + 'H' * len(o), *o)]
        print('  %s -> %d' % (kw, len(hits)))
        for off, o in hits[:8]:
            print('     %08X %s' % (off, dec(o[2:] if len(o) > 2 else o)[:110]))