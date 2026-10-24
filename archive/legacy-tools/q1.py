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
cpslot = {v: k for k, v in slot_of.items()}

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

def scan_us(blob):
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

us = vp.read(vp.find("static_US"))
usd = {}
for st, sl in scan_us(us):
    if len(sl) >= 4:
        usd.setdefault(tuple(sl[:2]), "".join(chr(s) for s in sl[4:]))

blob = vp.read(vp.find("static_CH"))
recs = [(st, tuple(sl[:2]), sl[2:]) for st, sl in scan(blob) if len(sl) >= 2]

TARGETS = ["有货弗达", "潘龄", "邓区", "酒店码头区", "萨默塞特", "有货"]
print("=== 精确搜索 ===")
for t in TARGETS:
    hits = [(st, rid, dec(b)) for st, rid, b in recs if t in dec(b)]
    print("\n【%s】%d 条" % (t, len(hits)))
    for st, rid, txt in hits[:20]:
        en = usd.get(rid, "<无US对照>")
        print("   @%-7d resID=%-16s %-22r  US=%r" % (st, str(rid), txt, en))
