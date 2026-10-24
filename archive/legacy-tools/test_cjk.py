import os, re, sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
W = r"F:\sr2-cn"
J = os.path.join(G,"Mods","JUICED - Strings")
OUT = os.path.join(W,"_juice_fix","test_cjk"); os.makedirs(OUT, exist_ok=True)

v = Vpp(G + r"\patch.vpp_pc")
CPS = set(int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit())

s = open(os.path.join(W,"_juice_fix","out7","juiced_CH.cxt"), encoding="utf-8").read()
# 测试1: 给 J_UNCFPS（当前显示 "Vanilla FX Plus"）加中文
# 测试2: 给 J_NOVIGN_R（当前显示 "Remove Vignette (R)"）加中文
TESTS = {
 "J_UNCFPS":    "Uncap FPS 帧率 中文测试",
 "J_NOVIGN_R":  "移除暗角 (R)",
}
for k, val in TESTS.items():
    miss = [c for c in val if ord(c)>0x100 and ord(c) not in CPS]
    print("[%s] -> %r" % (k, val))
    print("    缺字: %s" % ("".join(miss) if miss else "无"))
new = s
for k, val in TESTS.items():
    new = re.sub(r'(\[%s\]\r\n)[^\r\n]*' % k, lambda m: m.group(1)+val, new, count=1)
open(os.path.join(OUT,"juiced_CH.cxt"),"wb").write(new.encode("utf-8"))
print()
print("测试版 .cxt 写出 %d 字节" % len(new.encode("utf-8")))
for k in TESTS:
    m = re.search(r'\[%s\]\r\n([^\r\n]*)' % k, new)
    print("   [%s] = %r" % (k, m.group(1) if m else "?"))
