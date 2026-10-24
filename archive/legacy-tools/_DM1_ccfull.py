import sys, os, struct
import numpy as np
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
raw = open(r"F:/sr2-cn/_cc_list.bin","rb").read()
n = len(raw)//4
uni = [struct.unpack_from('<H', raw, i*4)[0] for i in range(n)]
comp= [struct.unpack_from('<H', raw, i*4+2)[0] for i in range(n)]
print("cc_list 项数 =", n)
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
t = v.read(v.find("charlist_CH","txt")).decode('utf-8','replace').replace('\r','').split('\n')
nums = [int(s) for s in t if s.strip().isdigit()]
print("磁盘 charlist 项数 =", len(nums))
bad = [(i, uni[i], nums[i]) for i in range(min(n,len(nums))) if uni[i] != nums[i]]
print("unicode 不一致的项数:", len(bad))
for r in bad[:15]: print("   idx=%d 引擎U+%04X vs 磁盘%d(U+%04X)" % (r[0], r[1], r[2], r[2]))
offs = [comp[i]-i for i in range(n)]
from collections import Counter
print("compressed-index 分布:", Counter(offs).most_common(5))
print("compressed 范围: %d .. %d" % (min(comp), max(comp)))
