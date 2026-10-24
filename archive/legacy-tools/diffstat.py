import sys, os
sys.path.insert(0, r"F:/sr2-cn/pylibs"); sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
cur = bytes(v.read(v.find("static_CH","le_strings")))
print("patch.vpp_pc 内 static_CH :", len(cur), "字节")
M = os.path.join(G,"Mods")
for f in ("static_CH.le_strings.v44bak","static_CH.le_strings.v45bak",
          "static_CH.le_strings.\u6211\u7684v103.\u5df2\u8ba9\u4f4d.bak"):
    p=os.path.join(M,f)
    d=open(p,"rb").read()
    same = (d==cur)
    diff = sum(1 for a,b in zip(d,cur) if a!=b) if len(d)==len(cur) else -1
    print("%-42s %d 字节  与vpp相同=%s  差异字节=%s" % (f, len(d), same, diff))
