# -*- coding: utf-8 -*-
"""分析 static_CH 中2404 条「不可解码」记录。
   不可解码 = 出现越界 slot（>= 0x20+2795=2815），游戏会渲染成资源ID数字。
   目标：在这批里找出「三王」类的条目。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(l) for l in
       v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n")
       if l.strip().isdigit()]
LIM = 0x20 + len(cps)
print("CH 字表 %d 项 -> 合法 slot 范围 [0x20, 0x%X)" % (len(cps), LIM))

d = bytes(v.read(v.find("static_CH", "le_strings")))
b, c, off_at, offs = file_offsets(d)
print("static_CH %d 字节  buckets=%d count=%d\n" % (len(d), b, c))

bad, good = [], []
for off in offs:
    r = read_units(d, off + 8)
    if not r or not r[0]:
        continue
    slots = [x for x, _ in r[0]]
    rid = struct.unpack_from("<HH", d, off)
    if all(0x20 <= s < LIM for s in slots):
        good.append((off, rid, "".join(chr(cps[s - 0x20]) for s in slots)))
    else:
        oob = [s for s in slots if not (0x20 <= s < LIM)]
        bad.append((off, rid, oob, slots))

print("可解码 %d / 不可解码 %d" % (len(good), len(bad)))

# 不可解码记录的结构特征
print("\n### 不可解码记录的长度分布")
from collections import Counter
print("  ", Counter(len(s) for _, _, _, s in bad).most_common(10))

print("\n### 不可解码记录样例（前 20）")
for off, rid, oob, slots in bad[:20]:
    print("  @%-8d resID=(%5d,%5d) len=%-3d slots=%s" % (off, rid[0], rid[1], len(slots), slots[:14]))

# 关键：这些记录的 slot 是否可能是【原厂 2838 表】的编码？
print("\n### 假设检验：不可解码记录若用【原厂 2838 表】解码，能否解出有意义中文？")
vo = Vpp(r"F:\sr2-cn\pristine\patch.vpp_pc")
cps_o = [int(l) for l in
         vo.read(vo.find("charlist_CH", "txt")).decode("utf-8").split("\n")
         if l.strip().isdigit()]
print("  原厂表 %d 项 -> 合法 slot [0x20, 0x%X)" % (len(cps_o), 0x20 + len(cps_o)))
LIM_O = 0x20 + len(cps_o)
ok_o = sum(1 for _, _, _, s in bad if all(0x20 <= x < LIM_O for x in s))
print("  %d / %d 条在原厂表下可解码" % (ok_o, len(bad)))

for off, rid, oob, slots in bad[:15]:
    if all(0x20 <= x < LIM_O for x in slots):
        print("   @%-8d -> %r" % (off, "".join(chr(cps_o[x - 0x20]) for x in slots)))
    else:
        print("   @%-8d -> 越界 %s" % (off, [x for x in slots if not (0x20 <= x < LIM_O)][:6]))