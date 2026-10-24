import struct
p='F:/sr2-cn/_ref_第三方补丁/原始基准/patch_第三方原版.vpp_pc'
import sys; sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
v=Vpp(p)
e=v.find('static_US','le_strings')
blob=v.read(e)
h=0x3DC0CCDF
# 记录 = [id1 LE][id2 LE][u16 ASCII/BE chars][0000]
target=struct.pack('<HH',(h>>16)&0xFFFF,h&0xFFFF)
idx=blob.find(target)
while idx>=0:
    j=idx+4; out=[]
    while j+2<=len(blob):
        s=struct.unpack_from('>H',blob,j)[0]
        if s==0: break
        out.append(s); j+=2
    txt=''.join(chr(x) if 32<=x<0x7f else '<%04X>'%x for x in out)
    print('off %08X  %r'%(idx,txt))
    idx=blob.find(target,idx+1)
    if idx>0 and idx<0 and False: break
