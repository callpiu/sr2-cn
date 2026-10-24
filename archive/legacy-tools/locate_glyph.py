# -*- coding: utf-8 -*-
"""定位乱码字在'图集物理格'里的位置。
已知 atlas cell i = patch表[i+5]。所以"任"= patch@[?]; 其物理格 = that_idx - 5。
反过来: 屏幕上"你"位置显示"任"。若引擎查 UV[371] 得到物理格p, 而 p 画的是"任",
则 patch[p+5]='任' => p = idx(任)-5。
"""
import os, sys, struct, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"


def load_tbl(path):
    vv = Vpp(path)
    buf = vv.read(vv.find("charlist_CH", "txt"))
    end = buf.find(b'//ENDOFFILE')
    if end < 0:
        end = len(buf)
    return [int(x) for x in re.findall(rb'\d+', buf[:end])]


patch = load_tbl(os.path.join(G, "patch.vpp_pc"))
pris = load_tbl(r"F:/sr2-cn/pristine/patch.vpp_pc")
ps = "".join(chr(c) for c in patch)


def pidx(ch):
    return ps.find(ch)


# 乱码字 (显示出来的)
garb = "任璨偶巧位雄衡伪该"
targ = "你的弟兄们需要保护"
print("atlas cell i 画的是 patch[i+5]")
print("表idx i 查 UV[i] 取物理格 i -> 显示 patch[i+5]")
print()
print("%-4s %-6s %-10s %-12s %-10s" % ("正确字", "表idx", "物理格i", "应显示patch[i+5]", "实际"))
for c, g in zip(targ, garb):
    i = pidx(c)
    phys = i
    shown = ps[phys + 5] if phys + 5 < len(ps) else '?'
    print("%-4s %-6d %-10d %-14s %-10s" % (c, i, phys, shown, g))
print()
print("== 反查: 乱码字'任'在patch表idx=", pidx('任'), " 其物理格=", pidx('任') - 5)
print("== 反查: 乱码字'璨'在patch表idx=", pidx('璨'), " 其物理格=", pidx('璨') - 5)
print("== 反查: 乱码字'偶'在patch表idx=", pidx('偶'), " 其物理格=", pidx('偶') - 5)
print("== 反查: 乱码字'巧'在patch表idx=", pidx('巧'), " 其物理格=", pidx('巧') - 5)
