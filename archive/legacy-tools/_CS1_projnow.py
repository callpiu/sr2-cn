import sys, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from _vpp import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\common.vpp_pc")
e = v.find("sr2", "vint_proj")
b = v.read(e)
print("当前游戏内 sr2.vint_proj: size=%d md5=%s" % (len(b), hashlib.md5(b).hexdigest()))
open(r"F:\sr2-cn\_sr2.vint_proj.NOW", "wb").write(b)

import re
txt = b.decode("latin-1")
print("\n--- 全部 font_info ---")
for m in re.finditer(r"<font_info>(.*?)</font_info>", txt, re.S):
    seg = m.group(1)
    fn = re.search(r"<filename>(.*?)</filename>", seg)
    al = re.search(r"<alias>(.*?)</alias>", seg)
    ov = re.search(r"<filename_overlay>(.*?)</filename_overlay>", seg)
    print("  filename=%-14s alias=%-20s overlay=%s" % (fn.group(1) if fn else "?", al.group(1) if al else "?", ov.group(1) if ov else "?"))

print("\n--- 与工程里旧提取 _sr2.vint_proj 对比 ---")
old = open(r"F:\sr2-cn\_sr2.vint_proj", "rb").read()
print("旧 size=%d md5=%s  相同=%s" % (len(old), hashlib.md5(old).hexdigest(), old == b))

# 顺便检查其它 vpp 里是否有 vint_proj 备份
for f in ("patch.vpp_pc",):
    v2 = Vpp(G + "\\" + f)
    for x in v2.entries():
        if x["ext"] == "vint_proj":
            print("  %s 内也有 %s.%s" % (f, x["name"], x["ext"]))
