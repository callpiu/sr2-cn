# -*- coding: utf-8 -*-
"""定案：引擎用 common.vpp 的 fnt_chinese.vf3_pc，索引 = slot - 0x20 (= patch charlist index)。
验证：common.vf3[idx] 的 UV 是否 == patch.vf3[乱码目标字 idx] 的 UV（同一格=同一字形）。
然后给出修复映射：对每个 charlist idx i，common 字体第 i 格画的是哪个字。
"""
import sys, os, struct
sys.path.insert(0, 'F:/sr2-cn')
import numpy as np
import sr2lib as S

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'

# patch charlist
vp = S.Vpp(os.path.join(G, 'patch.vpp_pc'))
CPS = [int(l) for l in vp.read(vp.find('charlist_CH', 'txt')).decode('utf-8').split('\n') if l.strip().isdigit()]
NP_ = len(CPS)
vf3p = bytes(vp.read(vp.find('fnt_chinese', 'vf3_pc')))
Np = struct.unpack_from('<I', vf3p, 8)[0]
UP = np.array(struct.unpack_from('<%di' % Np, vf3p, 0xD0 + Np * 16), dtype=np.int64)
VP = np.array(struct.unpack_from('<%di' % (Np - 5), vf3p, 0xD0 + Np * 16 + Np * 4), dtype=np.int64)

# common vf3
vc = S.Vpp(os.path.join(G, 'common.vpp_pc'))
vf3c = bytes(vc.read(vc.find('fnt_chinese', 'vf3_pc')))
Nc = struct.unpack_from('<I', vf3c, 8)[0]
UOFF = 0xD0 + Nc * 16
UC = np.array(struct.unpack_from('<%di' % Nc, vf3c, UOFF), dtype=np.int64)
VC = np.array(struct.unpack_from('<%di' % (Nc - 5), vf3c, UOFF + Nc * 4), dtype=np.int64)
print('patch vf3 N=%d U[0:6]=%s' % (Np, UP[:6]))
print('common vf3 N=%d U[0:6]=%s' % (Nc, UC[:6]))

# 关键：UV 坐标是否为「同一图集」的坐标？若两表 UV 值域相同，则同图集
print('patch U 范围 %d..%d  V 范围 %d..%d' % (UP.min(), UP.max(), VP.min(), VP.max()))
print('common U 范围 %d..%d  V 范围 %d..%d' % (UC.min(), UC.max(), VC.min(), VC.max()))

# 用 UV 唯一性：common[i] 的 (U,V) 是否 == patch[j] 的 (U,V)（同格判定）
puv = {}
for i in range(Np):
    puv.setdefault((int(UP[i]), int(VP[i]) if i < len(VP) else -1), []).append(i)
print('\n=== common[i] 的 UV 在 patch 表中的相同 UV 项 ===')
IDX = {cp: i for i, cp in enumerate(CPS)}
for slot in [332, 359, 371, 390, 1003, 1158, 1804, 2264, 2635]:
    if slot >= Nc:
        print('  slot %d 越界' % slot); continue
    key = (int(UC[slot]), int(VC[slot]) if slot < len(VC) else -1)
    same = puv.get(key, [])
    lab = '  charlist[%d]=%s' % (slot, chr(CPS[slot]) if slot < NP_ else '?')
    print('  common[%d] UV=%s -> patch 同UV项 %s %s' % (slot, key,
          [(k, chr(CPS[k])) for k in same], lab))
