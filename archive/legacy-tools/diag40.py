# -*- coding: utf-8 -*-
# diag40: 从 v532 备份取原始 slots -> 完整映射对; ASCII-art 目视比对 B@g vs A@候选
import sys, struct, re
sys.path.insert(0, 'F:/sr2-cn')
import numpy as np
from PIL import Image
import sr2lib

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
vp = sr2lib.Vpp(GAME + r'\patch.vpp_pc')
tx = sr2lib.Vpp(GAME + r'\textures.vpp_pc')
cm = sr2lib.Vpp(GAME + r'\common.vpp_pc')

CPS = [int(l) for l in vp.read(vp.find('charlist_CH', 'txt'))
       .decode('utf-8').split('\n') if l.strip().isdigit()]
IDX = {c: i for i, c in enumerate(CPS)}
N = len(CPS)
CHR = ''.join(chr(c) for c in CPS)

# ---- original REC slots from v532 backup ----
bak = open(GAME + r'\patch.vpp_pc.v532_before_exp.bak', 'rb').read()
ent = vp.find('static_CH', 'le_strings')
blob = bak[ent['body'] + 0x800 + vp.data_start - 0x800:]  # placeholder; use proper read below
# safer: read via Vpp on a temp copy
import shutil
tmp = r'F:/sr2-cn/_tmp_v532.vpp_pc'
shutil.copy(GAME + r'\patch.vpp_pc.v532_before_exp.bak', tmp)
vb = sr2lib.Vpp(tmp)
blob = vb.read(vb.find('static_CH', 'le_strings'))
print('v532 static_CH blob:', len(blob), 'bytes')

def units(h):
    id1, id2 = h >> 16, h & 0xFFFF
    p = struct.pack('<HH', id1, id2)
    i = blob.find(p)
    if i < 0:
        return None
    off = i + 4
    us = []
    while off + 2 <= len(blob):
        v = struct.unpack_from('>H', blob, off)[0]
        off += 2
        if v == 0:
            break
        us.append(v)
    return us

u1 = [v for v in units(0x84F287ED) if v >= 0x100]
u2 = [v for v in units(0x10AF1E62) if v >= 0x100]
T1 = '你的弟兄们需要你的保护'
T2 = '你的弟兄们要出去谈几笔生意，保护他们免遭袭击'
G1 = '任璨偶巧位雄衡任璨伪该'
G2 = '任璨偶巧位校衡勾远藐乱携伪该亡位通像匪冰挺拮'
print('REC1 orig slots n=', len(u1), ' true n=', len(T1))
print('REC2 orig slots n=', len(u2), ' true n=', len(T2))

pairs = {}
ok = True
for slots, true_s, garb in ((u1, T1, G1), (u2, T2, G2)):
    if len(slots) != len(true_s) or len(slots) != len(garb):
        print('LEN MISMATCH', len(slots), len(true_s), len(garb), repr(true_s), repr(garb))
        ok = False
        continue
    for s, t, g in zip(slots, true_s, garb):
        gi = s - 0x20
        r = IDX.get(ord(g))
        pairs.setdefault((gi, r), t)
print('\n=== full mapping (glyphidx -> screen char, rank) ===')
for (gi, r), t in sorted(pairs.items()):
    print(f'{t} g={gi:5d} -> {CHR[r] if r is not None else "?"} r={r}')
