import os, sys, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# ---- common.vpp_pc 的 fnt_chinese.vf3_pc ----
vc = Vpp(os.path.join(G,"common.vpp_pc"))
vf3 = bytes(vc.read(vc.find("fnt_chinese","vf3_pc")))
N = struct.unpack_from("<i", vf3, 0x08)[0]
W,H,CS = struct.unpack_from("<HHh", vf3, 0x10)
print("common vf3: N=%d Width=%d Height=%d CharSpacing=%d, %d 字节" % (N, W, H, CS, len(vf3)))
U0 = 0xD0 + N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
nV = (len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4)) + [0]*(N-nV)
print("  U 范围 %d..%d, V 范围 %d..%d, V 项数 %d" % (min(U),max(U),min(V),max(V),nV))
print()

# ---- textures.vpp_pc 的 fnt_chinese（无扩展名）----
# 用轻量方式：只读 entry 表
def hdr(path):
    f = open(path,"rb")
    d = f.read(0x1000)
    import struct as st
    off_at = 0x800; ent_at = 0x800
    names_at = ((0x800 + st.unpack_from("<I",d,0x14)[0]) & 0xFFFFF800) + 0x800
    return f, d
TP = os.path.join(G,"textures.vpp_pc")
print("textures.vpp_pc 大小: %.1f MB" % (os.path.getsize(TP)/1048576))
# 用文档给的偏移
BODY_OFF = 85407184
f = open(TP,"rb")
f.seek(BODY_OFF)
data = f.read(4194304)
print("  读到 %d 字节 @0x%X" % (len(data), BODY_OFF))
_, al = dxt3_decode(data, 2048, 2048)
print()

# 用 common 的 U/V 抠图
targets_idx = [1035, 422, 332, 2667, 2296, 371, 1836, 391, 1190]
tiles = []
for i in targets_idx:
    x, y = U[i], V[i]
    g = al[y:y+28, x:x+31]
    if g.shape != (28,31):
        pad = np.zeros((28,31),np.uint8); pad[:g.shape[0],:g.shape[1]] = g; g = pad
    tiles.append(g); tiles.append(np.full((28,2),255,np.uint8))
s = np.concatenate(tiles, axis=1)
Image.fromarray(255-s).resize((s.shape[1]*7, s.shape[0]*7), Image.NEAREST).save(r"F:\sr2-cn\_juice_fix\common_glyphs.png")
print("写出 common_glyphs.png")
cn = [int(l) for l in Vpp(os.path.join(G,"patch.vpp_pc")).read(Vpp(os.path.join(G,"patch.vpp_pc")).find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
print("  索引: %s" % targets_idx)
print("  字表: %s" % "".join(chr(cn[i]) for i in targets_idx))
print("  期望: 弟兄们需要你的保护")
print("  用户看到: 任璨偶巧位雄衡")
