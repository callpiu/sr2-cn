# -*- coding: utf-8 -*-
"""槽位真实编码 = 高字节 (v>>8)，低字节恒 0。即每个字符占 2 字节，ASCII 直存。
对 >0x7F 的字符，用 charlist 查。（CL[0]=0x20，故 idx = c - 0x20）
"""
import struct, os, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
S = os.path.join(G, 'Mods', 'JUICED - Strings')
v = Vpp(os.path.join(G, 'patch.vpp_pc'))
raw = v.read(v.find('charlist_CH', 'txt'))
CL = [int(x) for x in raw.decode('utf-8').split('\n') if x.strip().isdigit()]
print('CL len=%d CL[0]=%d(0x%X)' % (len(CL), CL[0], CL[0]))

def decode_body(b, mode):
    out = []
    for c in b:
        if 0x20 <= c <= 0x7E:
            out.append(chr(c))
        else:
            i = c - 0x20
            out.append(chr(CL[i]) if 0 <= i < len(CL) else '{%d}' % c)
    return ''.join(out)

for fn in ['patch_us.le_strings', 'patch_ch.le_strings', 'juiced_CH.le_strings', 'juiced_US.le_strings']:
    raw = open(os.path.join(S, fn), 'rb').read()
    # 高字节序列
    hi = bytes(raw[i] for i in range(1, len(raw), 2))
    lo = bytes(raw[i] for i in range(0, len(raw), 2))
    print('=' * 70)
    print(fn, 'size=%d  hi非零占比=%.2f lo全零? %s' % (len(raw), sum(1 for x in hi if x) / len(hi), all(x == 0 for x in lo)))
    print('  hi[0:120]:', decode_body(hi[:120], None))
