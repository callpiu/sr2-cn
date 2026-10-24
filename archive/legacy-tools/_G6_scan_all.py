# -*- coding: utf-8 -*-
"""★★★ 关键验证：patch 的 vf3 与 charlist_CH 是否真的配套？

推理链：
  · 若 patch vf3[i] 的 (U,V) 指向的字形 == charlist_CH[i] 的字
    => vf3 与 charlist 配套
  · 真机乱码 = 任璨偶巧位... 而正确 = 你的弟兄们...
  · 我在离线渲染 [patch vf3 + 索引] 时得到的却是正确的

⇒ 唯一可能：**真机加载的 vf3 不是我部署的那个**！
  也许是 patch.vpp_pc 里还有另一份？或者是从别处加载？

检验：扫描游戏目录所有 VPP，找所有含 "fnt" 的条目，确认引擎到底从哪读。
"""
import sys, os, struct, hashlib, glob
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
vpps = glob.glob(os.path.join(G, "*.vpp_pc"))
print("游戏目录 VPP:", [os.path.basename(p) for p in vpps])

for p in vpps:
    try:
        v = Vpp(p)
    except Exception as e:
        print(" ", os.path.basename(p), "读取失败", e); continue
    hits = [x for x in v.entries() if 'fnt' in x['name'].lower()]
    if hits:
        print("\n== %s ==" % os.path.basename(p))
        for x in hits:
            d = v.read(x)
            print("   %-20s | %-10s %8d  md5 %s" % (
                x['name'], x['ext'], x['size'], hashlib.md5(d).hexdigest()[:16]))

# loose 文件
print("\n== 松散文件 ==")
for pat in ("*.vf3*", "*.g_peg*", "fnt*"):
    for f in glob.glob(os.path.join(G, "**", pat), recursive=True):
        if os.path.isfile(f):
            print("   ", f, os.path.getsize(f))
