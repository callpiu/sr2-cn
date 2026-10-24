import struct,sys
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G='G:/SteamLibrary/steamapps/common/Saints Row 2/'
v=Vpp(G+'patch.vpp_pc')
e=v.find('static_CH','le_strings')
blob=v.read(e)
CL=[]
for l in open('F:/sr2-cn/_cl_now.txt','rb').read().decode('latin1').split('\n'):
    s=l.strip()
    if s.isdigit(): CL.append(int(s))
print('CL',len(CL))
def S(ch): return CL[ord(ch)-32]+0x20
def dec(slots):
    out=[]
    for s in slots:
        if s==0: break
        if s<0x20: out.append('^%02X'%s); continue
        i=s-0x20
        out.append(chr(CL[i]) if 0<=i<len(CL) else '?')
    return ''.join(out)
res=[];i=0;n=len(blob)
while i+2<=n:
    j=i;slots=[];ok=False
    while j+2<=n:
        s=struct.unpack_from('>H',blob,j)[0]
        if s==0: ok=True;break
        slots.append(s);j+=2
        if len(slots)>500: break
    if ok and slots:
        res.append((i,slots)); i=j+2
    else: i+=2
print('scanned',len(res))
import pickle
pickle.dump(res,open('F:/sr2-cn/_st_ch_recs.pkl','wb'))
for off,slots in res:
    t=dec(slots)
    if '城区' in t or '市郊' in t or '城郊' in t:
        print('%08X'%off,len(slots),repr(t))
