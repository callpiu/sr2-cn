# -*- coding: utf-8 -*-
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp, dxt3_decode
from PIL import Image
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

def get_tex(name, w, h):
    v = Vpp(os.path.join(G, "textures.vpp_pc"))
    raw = v.read(v.find(name, ""))
    rgb, a = dxt3_decode(raw, w, h)
    return a

def get_vf3(name, src="common.vpp_pc"):
    v = Vpp(os.path.join(G, src))
    raw = v.read(v.find(name, "vf3_pc"))
    N = struct.unpack_from("<I", raw, 8)[0]
    uoff = 0xD0 + N*16
    U = list(struct.unpack_from("<%di" % N, raw, uoff))
    V = list(struct.unpack_from("<%di" % (N-5), raw, uoff + N*4))
    recs = [struct.unpack_from("<HHHH", raw, 0xD0 + i*16) for i in range(N)]
    return N, U, V, recs

IDX = [371, 1836, 1035, 422, 332, 2667, 2296, 391, 1190]
EXP = "你的弟兄们需要保护"

for nm, tw, th in (("fnt_korea", 2048, 1024), ("fnt_cz", 1024, 512), ("ige_regular", 256, 128)):
    try:
        alpha = get_tex(nm, tw, th)
        N, U, V, recs = get_vf3(nm)
        print("\n=== %s  N=%d  图集 %dx%d ===" % (nm, N, tw, th))
        out = Image.new("L", (32*len(IDX), 40), 0)
        for i, idx in enumerate(IDX):
            if idx >= N:
                print("   idx %-5d (%s) 越界" % (idx, EXP[i])); continue
            x, y = U[idx], V[idx]
            x0, y0 = max(0, x), max(0, y)
            x1, y1 = min(tw, x0+32), min(th, y0+32)
            sub = alpha[y0:y1, x0:x1]
            out.paste(Image.fromarray(sub).resize((32, 32)), (i*32, 4))
            print("   idx %-5d (%s) U=%d V=%d" % (idx, EXP[i], x, y))
        out = out.resize((out.width*4, out.height*4), Image.NEAREST)
        out.save(r"F:/sr2-cn/_CELLS_%s.png" % nm)
        print("   -> _CELLS_%s.png" % nm)
    except Exception as ex:
        print("\n=== %s 失败: %s ===" % (nm, ex))
