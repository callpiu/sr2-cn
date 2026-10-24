import sys, os, struct
import numpy as np
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
W = r"F:\sr2-cn"
for tag, p in (("第三方", os.path.join(W,"_juice_fix","patch.vpp_pc")),
               ("原厂繁中", os.path.join(W,"pristine","patch.vpp_pc"))):
    v = Vpp(p)
    _, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
    vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
    N = struct.unpack_from("<i",vf3,0x08)[0]
    U0 = 0xD0+N*16
    U = list(struct.unpack_from("<%di"%N, vf3, U0))
    CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
    print("=== %s ===" % tag)
    # ASCII 区 (索引 0..94) 与 CJK 区 (索引 95+) 的字形墨迹宽度
    for label, rng in (("ASCII", range(1,95)), ("CJK", range(95, min(N, 300)))):
        ws=[]; gaps=[]
        for i in rng:
            u = U[i]; nxt = U[i+1] if i+1 < N else u+31
            seg = al[1:29, u:min(u+31,2048)] > 32
            cols = np.nonzero(seg.any(axis=0))[0]
            if len(cols):
                ws.append(int(cols.max()-cols.min()+1))
        if ws:
            print("  %s 字形墨迹宽度: 中位数 %d  均值 %.1f  范围 %d..%d  (n=%d)" % (
                label, int(np.median(ws)), float(np.mean(ws)), min(ws), max(ws), len(ws)))
    # 记录里的 width 值
    import collections
    for label, rng in (("ASCII", range(0,95)), ("CJK", range(95, min(N,300)))):
        c = collections.Counter(struct.unpack_from("<h", vf3, 0xD0+i*16)[0] for i in rng)
        print("  %s 记录里的 width: %s" % (label, dict(c.most_common(6))))
    print()
