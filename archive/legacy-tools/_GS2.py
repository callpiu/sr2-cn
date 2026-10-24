import sys, os
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G, "common.vpp_pc"))
for e in v.entries():
    nm = (e['name'] + ('.' + e['ext'] if e['ext'] else '')).lower()
    if nm == 'sr2.vint_proj':
        lines = v.read(e).decode('latin-1').split('\n')
        for i in range(25, 75):
            print(f"{i:4d}| {lines[i].rstrip()}")
        break
