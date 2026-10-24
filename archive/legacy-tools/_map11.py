import sys,struct
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G='G:/SteamLibrary/steamapps/common/Saints Row 2/'
v=Vpp(G+'patch.vpp_pc')
blob=v.read(v.find('static_CH','le_strings'))
for base in (0x6AB3C,0x1EFC6,0x43C5E):
    print('--- %08X'%base)
    seg=blob[base-16:base+24]
    print(' '.join('%04X'%struct.unpack_from('>H',seg,i)[0] for i in range(0,len(seg),2)))
    print(repr(blob[base-16:base+24]))
