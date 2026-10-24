# -*- coding: utf-8 -*-
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
import sr2lib
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
vp = sr2lib.Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(x) for x in vp.read(vp.find("charlist_CH")).decode("utf-8").split("\n")
       if x.strip().isdigit()]
N = len(cps)
slot_of = {}
for i, cp in enumerate(cps):
    slot_of.setdefault(cp, i + 0x20)

def scan(blob):
    bk = struct.unpack_from("<I", blob, 8)[0]
    ct = struct.unpack_from("<I", blob, 12)[0]
    o, e2, out = 16 + bk*8 + ct*4 + 4, len(blob), []
    while o < e2 - 1:
        st = o; sl = []
        while True:
            if o >= e2: return out
            s = struct.unpack_from(">H", blob, o)[0]; o += 2
            if s == 0: break
            sl.append(s)
        if sl: out.append((st, sl))
    return out

def dec(sl):
    return "".join(chr(cps[s-0x20]) if 0 <= s-0x20 < N
                   else ("\n" if s == 10 else "<%d>" % s) for s in sl)

ent = vp.find("static_CH")
blob = vp.read(ent)
recs = []
for st, sl in scan(blob):
    if len(sl) >= 2:
        recs.append((st, tuple(sl[:2]), sl[2:]))

print("static_CH %d 字节 / %d 条" % (len(blob), len(recs)))

# ---- 自检：解码器必须在已知正样本上工作 ----
print("\n=== 自检：搜索已知正确地名 '萨默塞特' ===")
hit = [(st, rid, dec(b)) for st, rid, b in recs if dec(b) == "萨默塞特"]
print("  命中 %d 条" % len(hit))
for h in hit[:5]:
    print("   resID=%s slots=%s" % (h[1], h[2][:8]))
if not hit:
    print("  ★★ 自检失败，解码器不可信，中止")
    raise SystemExit(1)
