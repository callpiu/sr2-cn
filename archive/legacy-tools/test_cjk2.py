import os, re, sys, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
W = r"F:\sr2-cn"
OUT = os.path.join(W,"_juice_fix","test_cjk"); os.makedirs(OUT, exist_ok=True)

v = Vpp(G + r"\patch.vpp_pc")
CPS = set(int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit())

src = os.path.join(W,"_juice_fix","out7","juiced_CH.cxt")
raw = open(src, encoding="utf-8").read()
print("源 .cxt %d 字节" % len(raw.encode()))
# 解析成 (key, value) 列表，保序
hits = list(re.finditer(r'\[([A-Za-z0-9_,]+)\]', raw))
items = []
for i, m in enumerate(hits):
    end = hits[i+1].start() if i+1 < len(hits) else len(raw)
    items.append([m.group(1), raw[m.end():end].strip("\r\n")])
print("解析出 %d 个条目" % len(items))
print("前 3 个: %s" % [(k, v[:20]) for k, v in items[:3]])
print()
# 改两个
TESTS = {"J_UNCFPS": "Uncap FPS 帧率 中文测试", "J_NOVIGN_R": "移除暗角 (R)"}
for it in items:
    if it[0] in TESTS:
        newv = TESTS[it[0]]
        miss = [c for c in newv if ord(c)>0x100 and ord(c) not in CPS]
        print("[%s] %r -> %r  缺字:%s" % (it[0], it[1], newv, "".join(miss) if miss else "无"))
        it[1] = newv
out = "".join("[%s]\r\n%s\r\n\r\n" % (k, v) for k, v in items).rstrip("\r\n") + "\r\n"
open(os.path.join(OUT,"juiced_CH.cxt"),"wb").write(out.encode("utf-8"))
print()
print("测试版写出 %d 字节" % len(out.encode("utf-8")))
for k, val in items:
    if k in TESTS: print("   [%s] = %r" % (k, val))
