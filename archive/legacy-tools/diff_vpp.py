import sys, os, hashlib
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
W = r"F:\sr2-cn"; G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
src = os.path.join(W,"_juice_fix","patch.vpp_pc")     # 第三方原始
new = os.path.join(G,"patch.vpp_pc")                  # 修复后
vs, vn = Vpp(src), Vpp(new)
print("条目数: 原始 %d  修复后 %d" % (vs.num, vn.num))
print("文件大小: %d -> %d" % (len(vs.data), len(vn.data)))
print()
print("%-24s %-10s %-12s %-12s %s" % ("条目","ext","原始size","新size","是否相同"))
same = diff = 0
for es in vs.entries():
    en = vn.find(es["name"], es["ext"]) if es["ext"] else None
    if en is None:
        continue
    a = vs.read(es); b = vn.read(en)
    ok = (a == b)
    if ok: same += 1
    else: diff += 1
    if not ok:
        print("%-24s %-10s %-12d %-12d 不一致" % (es["name"], es["ext"] or "", len(a), len(b)))
print()
print("内容相同 %d 条，不同 %d 条" % (same, diff))
print()
# 确认文本表未被改动
for nm in ("static_CH","voice_script_CH","platform_pc_CH","charlist_CH"):
    for ex in ("le_strings","txt"):
        es = vs.find(nm, ex)
        if not es: continue
        a = vs.read(es); b = vn.read(vn.find(nm, ex))
        print("  %-18s.%-10s %s" % (nm, ex, "完全相同 OK" if a==b else "已改动"))
