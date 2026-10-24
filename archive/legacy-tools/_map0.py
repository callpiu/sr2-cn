import sys
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G='G:/SteamLibrary/steamapps/common/Saints Row 2/'
v=Vpp(G+'patch.vpp_pc')
e=v.find('charlist_CH','txt')
raw=v.read(e)
print('len',len(raw), 'head', raw[:40])
open('F:/sr2-cn/_cl_now.txt','wb').write(raw)
