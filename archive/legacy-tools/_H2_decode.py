# -*- coding: utf-8 -*-
"""按 le_strings 真实结构解码：
u16[0..3] = magic_lo, magic_hi, ver, count
记录区从 byte 8 开始：每条 <u32 hash> <u32 n_slots> <u16 slot> * n_slots <u16 0> <u32 FFFFFFFF>
（先用暴力变体探测哪套可行）
输出 hash -> slot列表，并用 charlist 解码成文字。
"""
import struct, os, json, sys

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
sys.path.insert(0, 'F:/sr2-cn')

# 载入 charlist
CL2759 = None
import sr2lib  # noqa
try:
    v = sr2lib.Vpp(os.path.join(G, 'patch.vpp_pc'))
    ent = v.find('charlist_CH', 'txt')
    print('charlist_CH in patch.vpp_pc:', ent)
except Exception as e:
    print('vpp err', e)

# 直接读磁盘上的 charlist 文本
cands = [
    r'F:\sr2-cn\_day_2026-10-07\04_规则与数据\_expected_charlist.json',
    r'F:\sr2-cn\fontwork\charlist_final.bin',
]
print('expected json exists:', os.path.exists(cands[0]))
obj = json.load(open(cands[0], encoding='utf-8'))
print('expected type:', type(obj), (len(obj) if hasattr(obj, "__len__") else ''))
if isinstance(obj, dict):
    print('keys:', list(obj.keys())[:10])
