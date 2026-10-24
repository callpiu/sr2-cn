import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
W = r"F:\sr2-cn"
v = Vpp(os.path.join(W,"_juice_fix","patch.vpp_pc"))
rgb, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
N = struct.unpack_from("<i",vf3,0x08)[0]
CH0 = 0xD0
print("vf3 头部参数:")
for o,nm in ((0x10,"Width"),(0x14,"Height"),(0x16,"RenderHeight"),(0x1C,"CharSpacing"),(0x24,"VerticalOffset")):
    print("  %-14s = %d" % (nm, struct.unpack_from("<i",vf3,o)[0]))
U0 = CH0+N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
nV=(len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4))
WID=[struct.unpack_from("<h",vf3,CH0+i*16)[0] for i in range(N)]
idx={}
for i,cp in enumerate(CPS):
    if 0x20<=cp<=0x7E: idx.setdefault(cp,i)

def render_line(s):
    """按「步进 = width + CharSpacing」模拟引擎排版。"""
    SP = struct.unpack_from("<i",vf3,0x1C)[0]
    out = np.zeros((28, 1400), np.uint8)
    x = 0
    for ch in s:
        i = idx.get(ord(ch))
        if i is None: continue
        if ch == ' ':
            x += 6; continue
        u, v = U[i], V[i]
        g = al[v:v+28, u:u+WID[i]]
        if g.shape[0] < 28:
            p = np.zeros((28, g.shape[1]), np.uint8); p[:g.shape[0]] = g; g = p
        w = g.shape[1]
        if 0 <= x and x+w <= out.shape[1]:
            out[:, x:x+w] = np.maximum(out[:, x:x+w], g)
        x += w + SP
    return out

for s in ("JUICED", "Display & Audio Options", "Uncap FPS", "DynamicRenderDistance"):
    o = render_line(s)
    Image.fromarray(255-o).resize((o.shape[1]*2, o.shape[0]*4), Image.NEAREST).save(
        os.path.join(W,"_juice_fix","line_%s.png" % s.replace(" ","_").replace("&","and")[:20]))
    print("排出 %-26s -> line_%s.png" % (s, s.replace(" ","_").replace("&","and")[:20]))
