import sys
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v=Vpp(G+'/patch.vpp_pc')
print("patch.vpp_pc 条目数 =", v.num)
for e in v.entries():
    n=(e['name']+'.'+e['ext']).lower()
    if 'charlist' in n or 'le_strings' in n or 'cxt' in n:
        print("  %-40s size=%d" % (e['name']+'.'+e['ext'], e['size']))
