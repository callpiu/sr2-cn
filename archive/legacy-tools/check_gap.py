# -*- coding: utf-8 -*-
"""查看目标记录周围的字节，找可安全借用的空位"""
import struct, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))
IDX = {}
for i, cp in enumerate(CL):
    IDX.setdefault(cp, i)

def D(sl):
    return ''.join(chr(CL[x - 0x20]) if 0x20 <= x - 0x20 < len(CL) else '^%02X' % x for x in sl)

def scan(b):
    res = []; i = 0; n = len(b)
    while i + 2 <= n:
        j = i; out = []
        while j + 2 <= n:
            x = struct.unpack_from('>H', b, j)[0]
            if x == 0: break
            out.append(x); j += 2
            if len(out) > 600: break
        if out: res.append((i, out)); i = j + 2
        else: i += 2
    return res

v = Vpp(G + 'patch.vpp_pc')
blob = v.read(v.find('static_CH', 'le_strings'))
CH = scan(blob)
idx = {off: k for k, (off, o) in enumerate(CH)}

TARGETS = [0x306F0, 0x50260, 0x5A3D8, 0x56740]

for t in TARGETS:
    k = idx[t]
    o = CH[k][1]
    n = len(o) - 2
    text_at = t + 4
    term = text_at + n * 2
    print('=== %08X slot=%d %r ===' % (t, n, D(o[2:])))
    print('   前2字节(应0000): %04X' % struct.unpack_from('>H', blob, t - 2)[0])
    print('   终止符 %04X%04X' % struct.unpack_from('>HH', blob, term))
    # 后一条记录
    nxt = CH[k + 1]
    nd = (nxt[1][0] << 16) | nxt[1][1]
    print('   下一条 @%08X ID=%08X slot=%d %r'
          % (nxt[0], nd, len(nxt[1]) - 2, D(nxt[1][2:])[:24]))
    # 下一条文本起点与本条终止符之间的空隙
    nxt_text = nxt[0] + 4
    gap = nxt_text - (term + 2)
    print('   本条终止符后 -> 下条文本起点 空隙 = %d 字节 (%d slot)' % (gap, gap // 2))
    if gap >= 2:
        mid = blob[term + 2:nxt_text]
        print('   空隙内容: %s' % ' '.join('%04X' % struct.unpack_from('>H', mid, i)[0]
                                          for i in range(0, len(mid) - 1, 2)))
    print()