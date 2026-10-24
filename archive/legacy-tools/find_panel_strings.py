# -*- coding: utf-8 -*-
"""诊断：面板文字 vs 字幕文字 —— 谁受 static_CH 影响？

背景
    - 我改了 static_CH 的 REC1/REC2 槽位（连续索引测试串）-> 字幕【没变】
    - 但面板「直升機攻擊」中的「攻」是错字（应为「突」）

任务
    找一条【只在面板显示】的字符串（例如活动名），改成 ASCII 测试串，
    看面板是否变化。这样能确定：
        - 面板走 static_CH -> 我改错地方
        - 面板也不变     -> 整个 CJK 文本路径都不来自 static_CH
"""
import os, sys, struct, shutil, datetime, hashlib, glob

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp
sys.path.insert(0, r"F:\sr2-cn\pylibs")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
PATH = os.path.join(G, "patch.vpp_pc")
BACKUP = r"F:\sr2-cn\_fontfix_backup"

v = Vpp(PATH)
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}
IDX = {chr(cp): i for i, cp in enumerate(cn)}

d = bytes(v.read(v.find("static_CH", "le_strings")))
b, c, oa, offs = file_offsets(d)

# 找活动名相关记录（含「直升機」或「直昇機」或单独「直升」）
print("=== static_CH 里含「直升」的记录 ===")
hits = []
for off in [o for o in dict.fromkeys(offs) if 0 < o <= len(d) - 10]:
    u, _ = read_units(d, off + 8)
    if u is None:
        continue
    vals = [x for x, _ in u]
    t = "".join(S.get(x, "·") for x in vals)
    if "直升" in t or "直昇" in t:
        id1, id2 = struct.unpack_from("<HH", d, off)
        h = (id1 << 16) | id2
        hits.append((off, h, len(vals), t))
        print("  @%-8d hash 0x%08X len=%-4d %s" % (off, h, len(vals), t))
print()
print("共 %d 条" % len(hits))

# 也找「突擊」「攻擊」
for kw in ("突擊", "攻擊", "停靠", "耐久"):
    print("=== 含「%s」的记录 ===" % kw)
    n = 0
    for off in [o for o in dict.fromkeys(offs) if 0 < o <= len(d) - 10]:
        u, _ = read_units(d, off + 8)
        if u is None:
            continue
        t = "".join(S.get(x, "·") for x, _ in u)
        if kw in t:
            id1, id2 = struct.unpack_from("<HH", d, off)
            print("  @%-8d hash 0x%08X len=%-4d %s" % (off, (id1 << 16) | id2, len(t), t[:70]))
            n += 1
            if n >= 5:
                break
    print()
