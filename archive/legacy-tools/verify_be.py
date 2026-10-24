import sys, struct, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp
P = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
vpp = Vpp(P)
cl = vpp.find('charlist_CH','txt'); clb=vpp.read(cl)
end=clb.find(b'//ENDOFFILE'); body=clb[:end if end>0 else len(clb)]
CPS=[int(x) for x in re.findall(rb'\d+', body)]
ent=vpp.find('static_CH','le_strings'); blob=vpp.read(ent)
m,ver,nb,count=struct.unpack_from('<IHHI',blob,0); A0=12+nb*8
def dec(off):
    j=off+4; u=[]
    while j+2<=len(blob):
        v=struct.unpack_from('>H',blob,j)[0]   # BE
        if v==0: break
        u.append(v); j+=2
    return ''.join(chr(CPS[v-0x20]) if 0<=v-0x20<len(CPS) else '?' for v in u)
expect={0x84F287ED:'面包车耐久测试文本',0x10AF1E62:'测试一二三四五六七八九'}
ok=True
for i in range(count):
    off=struct.unpack_from('<I',blob,A0+i*4)[0]
    id1,id2=struct.unpack_from('<HH',blob,off)
    h=(id1<<16)|id2
    if h in expect:
        d=dec(off); g=(d==expect[h]); ok=ok and g
        print('%08X => %r (%s)'%(h,d,'OK' if g else 'MISMATCH'))
print('nb=%d count=%d  DEPLOYED OK:',nb,count,ok)
