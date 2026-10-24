import sys, os, struct
from collections import Counter
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
def recs(p,name,ext,tag):
    v=Vpp(p); b=v.read(v.find(name,ext)); N=struct.unpack_from('<I',b,8)[0]
    R=[struct.unpack_from('<IIII',b,0xBC+i*16) for i in range(N)]
    print("=== %s N=%d ==="%(tag,N))
    print("  w 分布:", Counter(r[0] for r in R).most_common(6))
    print("  h 分布:", Counter(r[1] for r in R).most_common(6))
    print("  第3字段分布:", Counter(r[2] for r in R).most_common(4))
    print("  第4字段分布:", Counter(r[3] for r in R).most_common(4))
    print("  前8条:", R[:8])
    return R
G=r"G:/SteamLibrary/steamapps/common/Saints Row 2"
ro = recs(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig","fnt_chinese","vf3_pc","官方")
rm = recs(os.path.join(G,"common.vpp_pc"),"fnt_chinese","vf3_pc","我的")
print("\n=== 逐位对比前60条 (官方 vs 我的) ===")
for i in range(60):
    if ro[i]!=rm[i]:
        print("  [%2d] 官方%s 我的%s" % (i, ro[i], rm[i]))
