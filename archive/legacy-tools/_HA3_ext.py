import os, sys
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
from collections import Counter
c = Counter()
for e in v.entries():
    c[e['ext']] += 1
print(c.most_common(20))
print("--- 含 CH 的条目 ---")
for e in v.entries():
    if 'CH' in e['name'] or 'ch' == e['ext'].lower():
        print(f"  name={e['name']!r} ext={e['ext']!r} size={e['size']}")
