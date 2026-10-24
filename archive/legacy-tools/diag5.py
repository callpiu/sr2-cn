# -*- coding: utf-8 -*-
# 假设检验：引擎若用 common 的 vf3(N=2838) 配 charlist_CH(2795)，idx 371 会显示哪个字？
import struct, sys
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# 找出所有 vf3 / fnt 容器项
for fn in ("patch.vpp_pc", "common.vpp_pc", "textures.vpp_pc", "maps.vpp_pc"):
    try:
        vp = Vpp(G + "\\" + fn)
    except Exception as ex:
        print(fn, "跳过", ex); continue
    for e in vp.entries():
        if "vf3" in e['ext'].lower() or "vf3" in e['name'].lower() or "fnt" in e['name'].lower():
            print(f"{fn}: {e['name']}.{e['ext']}  size={e['size']}")

# patch 的 fnt_chinese.vf3_pc: N=2795, U@0xAF6C V@0xDB18
vp = Vpp(G + r"\patch.vpp_pc")
vf_patch = bytes(vp.read(vp.find("fnt_chinese", "vf3_pc")))
CPS = [int(l) for l in vp.read(vp.find("charlist_CH", "txt"))
       .decode("utf-8").split("\n") if l.strip().isdigit()]
N = len(CPS)
Up = list(struct.unpack_from("<%di" % N, vf_patch, 0xAF6C))
Vp_ = list(struct.unpack_from("<%di" % N, vf_patch, 0xDB18))

# charlist 解析完整性检查
raw_lines = vp.read(vp.find("charlist_CH", "txt")).decode("utf-8", "ignore").split("\n")
print(f"\ncharlist_CH.txt 总行数={len(raw_lines)} 解析出={N} 首行={raw_lines[0]!r} 末行={raw_lines[-1]!r}")
bad = [l for l in raw_lines if l.strip() and not l.strip().isdigit()]
print(f"非纯数字非空行: {len(bad)} 例: {bad[:5]}")
print(f"傅(U+5085) 在 charlist_CH? {0x5085 in CPS}")
