# -*- coding: utf-8 -*-
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

def parse(vf3):
    N = struct.unpack_from("<I", vf3, 8)[0]
    uoff = 0xD0 + N*16
    U = list(struct.unpack_from("<%di" % N, vf3, uoff))
    V = list(struct.unpack_from("<%di" % (N-5), vf3, uoff + N*4))
    return N, U, V

for fn, ex in (("patch.vpp_pc","vf3_pc"), ("common.vpp_pc","vf3_pc")):
    v = Vpp(os.path.join(G, fn))
    e = v.find("jap", ex)
    raw = v.read(e)
    N, U, V = parse(raw)
    su, sv = sorted(set(U)), sorted(set(V))
    print("[%s] jap.vf3_pc  %d B  N=%d" % (fn, len(raw), N))
    print("   U 唯一 %d 个: %s ... %s" % (len(su), su[:5], su[-3:]))
    print("   V 唯一 %d 个: %s ... %s" % (len(sv), sv[:5], sv[-3:]))
    print("   U 步长: %s   V 步长: %s" % (
        (su[1]-su[0]) if len(su)>1 else '?', (sv[1]-sv[0]) if len(sv)>1 else '?'))
    # 关键：槽位 2790 对应的索引 2758 是否越界
    print("   槽位2790 -> 索引2758  越界: %s" % (2758 >= N))
    print("   槽位403  -> 索引371   越界: %s" % (371 >= N))
    # U/V[371]
    if 371 < N:
        print("   U[371]=%d V[371]=%d" % (U[371], V[371] if 371 < len(V) else -1))
