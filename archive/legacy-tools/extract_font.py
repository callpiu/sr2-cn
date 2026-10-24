import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
W = r"F:\sr2-cn"
p = r"F:\sr2-cn\_juice_fix\patch.vpp_pc"
v = Vpp(p)
print("=== 修复版 patch.vpp_pc 里的字体相关条目 ===")
for e in v.entries():
    nm = e["name"] if isinstance(e, dict) else e[0]
    ex = e["ext"] if isinstance(e, dict) else e[1]
    sz = e.get("size") if isinstance(e, dict) else None
    if any(k in nm.lower() for k in ("charlist","fnt_","font")):
        print("  %-28s %-12s %s" % (nm, ex, sz))
print()
for target, out in (("charlist_CH","charlist_CH.txt"),
                    ("fnt_chinese","fnt_chinese.vf3_pc"),
                    ("fnt_chinese","fnt_chinese.g_peg_pc")):
    e = v.find(target, out.split(".")[-1])
    if not e:
        print("  %s 未找到" % out); continue
    d = bytes(v.read(e))
    op = os.path.join(W, "_juice_fix", out)
    open(op, "wb").write(d)
    print("  %-26s %8d 字节 -> %s" % (out, len(d), op))
