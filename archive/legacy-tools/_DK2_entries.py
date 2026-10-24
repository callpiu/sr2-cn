import sys, os, hashlib
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
def ents(p):
    v=Vpp(p); out=[]
    for e in v.entries():
        b=v.read(e)
        out.append((e['name'], e.get('ext',''), e['size'], hashlib.md5(b).hexdigest()[:10]))
    return out
a = ents(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig")
b = ents(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")
print("原始 %d 条, 当前 %d 条" % (len(a), len(b)))
sa = set((n,e) for n,e,s,h in a)
sb = set((n,e) for n,e,s,h in b)
print("\n--- 原始有、当前缺失 ---")
for n,e in sorted(sa-sb): print("   %-24s .%s" % (n,e))
print("--- 当前有、原始没有 ---")
for n,e in sorted(sb-sa): print("   %-24s .%s" % (n,e))
print("\n--- 共有但内容不同 ---")
da = {(n,e):(s,h) for n,e,s,h in a}
db = {(n,e):(s,h) for n,e,s,h in b}
for k in sorted(set(da)&set(db)):
    if da[k]!=db[k]: print("   %-24s .%s  原始%s  当前%s" % (k[0],k[1],da[k],db[k]))
