import sys
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G='G:/SteamLibrary/steamapps/common/Saints Row 2/'
v=Vpp(G+'city_load.vpp_pc')
for e in v.entries():
    print(e['name'], e['ext'], e['size'])
