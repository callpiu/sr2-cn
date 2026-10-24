import os, re, sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
W = r"F:\sr2-cn"
OUT = os.path.join(W,"_juice_fix","test_blankline"); os.makedirs(OUT, exist_ok=True)
v = Vpp(G + r"\patch.vpp_pc")
CPS = set(int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit())

raw = open(os.path.join(W,"_juice_fix","out7","juiced_CH.cxt"), encoding="utf-8").read()
hits = list(re.finditer(r'\[([A-Za-z0-9_,]+)\]', raw))
items = []
for i, m in enumerate(hits):
    end = hits[i+1].start() if i+1 < len(hits) else len(raw)
    items.append([m.group(1), raw[m.end():end].strip("\r\n")])
# 测试：给 J_UNCFPS 一个【纯中文、无 ASCII】的值
T = {"J_UNCFPS": "帧率测试", "J_NOVIGN_R": "移除暗角"}
for it in items:
    if it[0] in T:
        val = T[it[0]]
        miss = [c for c in val if ord(c)>0x100 and ord(c) not in CPS]
        print("[%s] -> %r 缺字:%s" % (it[0], val, "".join(miss) if miss else "无"))
        it[1] = val
out = "".join("[%s]\r\n%s\r\n\r\n" % (k, v) for k, v in items).rstrip("\r\n") + "\r\n"
open(os.path.join(OUT,"juiced_CH.cxt"),"wb").write(out.encode("utf-8"))
print("纯中文测试版写出 %d 字节 -> %s" % (len(out.encode()), os.path.join(OUT,"juiced_CH.cxt")))
