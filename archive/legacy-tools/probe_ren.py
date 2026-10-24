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
print("字表 %d 项" % N)

for ch in "指定辩护人 3王":
    cp = ord(ch)
    s = slot_of.get(cp)
    ok = s is not None and 0 <= s - 0x20 < N
    print("  %r U+%04X slot=%-6s %s" % (ch, cp, s, "OK" if ok else "★不在字表★"))

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

blob = vp.read(vp.find("static_CH"))
recs = [(st, sl[2:]) for st, sl in scan(blob) if len(sl) >= 2]
print("\nstatic_CH 共 %d 条" % len(recs))

# 「人」的使用频次（旁证：该字位若无大量误报，视为字位完好）
from collections import Counter
cnt = Counter()
for st, body in recs:
    t = dec(body)
    for c in t:
        cnt[c] += 1
print("「人」出现在 %d 条中" % sum(1 for st, b in recs if "人" in dec(b)))
print("「指」出现在 %d 条中" % sum(1 for st, b in recs if "指" in dec(b)))
print("「定」出现在 %d 条中" % sum(1 for st, b in recs if "定" in dec(b)))

print("\n含「人」的样例（供核对字位是否可信）:")
n = 0
for st, body in recs:
    t = dec(body)
    if "人" in t and 2 <= len(t) <= 12 and t.strip() == t:
        print("   %-16r slots=%s" % (t, body[:10]))
        n += 1
        if n >= 8: break
