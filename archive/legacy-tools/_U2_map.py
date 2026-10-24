# -*- coding: utf-8 -*-
import sys, struct, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(GAME + r"\patch.vpp_pc")
rawcl = pv.read(pv.find("charlist_CH", "txt"))
m = re.search(rb'count=(\d+)\r?\n', rawcl)
cl = [int(x) for x in re.findall(rb'\d+', rawcl[m.end():])]
idx = {}
for i, cp in enumerate(cl):
    idx.setdefault(cp, i)

SRC = "你的弟兄们需要你的保护"
GAR = "任璨偶巧位雄衡任璨伪该"
print("源文字 -> charlist索引 -> static_CH slot:")
SUB = {'你':403,'的':1868,'弟':1067,'兄':454,'们':364,'需':2699,'要':2328,'保':423,'护':1222}
for ch in SRC:
    cp = ord(ch)
    print("  %s U+%04X cl_idx=%s slot=%s" % (ch, cp, idx.get(cp), SUB.get(ch)))
print("乱码字 -> charlist索引:")
GARB = {'任':336,'璨':1784,'偶':410,'巧':967,'位':362,'雄':2656,'衡':2268,'伪':354,'该':2342}
for ch in GAR:
    cp = ord(ch)
    print("  %s U+%04X cl_idx=%s  assumed=%s" % (ch, cp, idx.get(cp), GARB.get(ch)))
