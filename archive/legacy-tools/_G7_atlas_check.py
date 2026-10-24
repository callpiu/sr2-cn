# -*- coding: utf-8 -*-
"""★★★ 决定性检验：引擎把 slot 当【码点】送进 0x7F4F20 (codepoint->slot)，
   而 codepoint->slot 用【线性扫描 charlist 的 low16】。

若 charlist 表里 low16 存的是【码点】，则 slot→码点 是恒等，
但真机乱码说明并非如此。

★ 换一个角度：真机乱码字 = 正确字在 charlist 里的【相邻位置】的字？
  你 idx371 -> 任 idx336  (差 -35)
  的 idx1836 -> 璨 idx1784 (差 -52)
  ...
  若引擎用 slot 直接索引 vf3，且 vf3[i] 的 (U,V) 指向图集第 j 格，
  而图集第 j 格画的是字 X —— 则显示 X。

真正要做的是：用【真机实际加载的图集】+【真机实际加载的 vf3】
              渲染 slot 序列，看是否复现乱码。
我们已经知道：
  - 离线用 patch vf3 + patch 图集 + idx → 正确
  - 但真机乱码

⇒ 差异只可能在【真机加载的内容 ≠ 我改的内容】
  可能：patch.vpp_pc 被游戏优先加载，但 common.vpp_pc 的 vf3 才是引擎用的，
        而两者我现在都改成了 patch 版。

★ 现在唯一没验证的：真机是否用了 textures.vpp_pc 的图集，
  而该图集 = patch 图集 = 与 patch vf3 配套。
  那应该对啊……

除非：图集替换【没有生效】。检查图集在 VPP 里的实际存储是否被我改对了。
"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
import numpy as np
from sr2lib import dxt3_decode
from PIL import Image

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# 直接对比 patch 图集 与 texts 图集（当前部署）
vp = Vpp(os.path.join(G, "patch.vpp_pc"))
AH = vp.read(vp.find("fnt_chinese", "g_peg_pc"))
vt = Vpp(os.path.join(G, "textures.vpp_pc"))
AT = vt.read(next(x for x in vt.entries() if x['name'] == 'fnt_chinese'))
print("patch 图集 md5", hashlib.md5(AH).hexdigest())
print("texts 图集 md5", hashlib.md5(AT).hexdigest())
print("相同?", AH == AT)

# 检查 VPP entry 的 body/size 是否指向正确位置（可能我只改了副本）
et = next(x for x in vt.entries() if x['name'] == 'fnt_chinese')
print("\ntexts fnt_chinese entry:", et)
bo = vt.data_start + et['body']
print("data_start=%d body=%d => 绝对偏移 %d" % (vt.data_start, et['body'], bo))
raw = bytes(vt.data[bo:bo+16])
print("该位置前 16 字节:", raw.hex())
print("与 read() 结果一致?", raw == AT[:16])
