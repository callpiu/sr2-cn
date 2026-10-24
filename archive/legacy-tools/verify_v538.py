import struct,hashlib,sys,pickle
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G='G:/SteamLibrary/steamapps/common/Saints Row 2/'
P=G+'patch.vpp_pc'
old=G+'patch.vpp_pc.before_v538.bak'
b=open(P,'rb').read(); ob=open(old,'rb').read()
print('md5 now',hashlib.md5(b).hexdigest(),'size',len(b),'size old',len(ob))
assert len(b)==len(ob),'size changed!'
diff=[i for i in range(len(b)) if b[i]!=ob[i]]
print('diff bytes',len(diff), 'at',[hex(x) for x in diff])
v=Vpp(P)
blob=v.read(v.find('static_CH','le_strings'))
CL=[]
for l in open('F:/sr2-cn/_cl_now.txt','rb').read().decode('latin1').split('\n'):
    s=l.strip()
    if s.isdigit(): CL.append(int(s))
def T(s): return''.join('^%02X'%x if x<0x20 else (chr(CL[x-0x20]) if x-0x20<len(CL) else '?') for x in s)
# 重扫记录
res=[];i=0;n=len(blob)
while i+2<=n:
    j=i;slots=[];ok=False
    while j+2<=n:
        s=struct.unpack_from('>H',blob,j)[0]
        if s==0: ok=True;break
        slots.append(s);j+=2
        if len(slots)>500: break
    if ok and slots: res.append((i,slots)); i=j+2
    else: i+=2
print('records scanned',len(res))
for off,s in res:
    if len(s)>=3 and s[0]==0x3DC0 and s[1]==0xDFCC:
        print('  0x%08X  text=%r'%(off,T(s[2:])))
# 回归校验 v537 成果
allt=[T(s) for off,s in res]
allt='\n'.join(allt)
for kw in ['指定辩护律师','霰弹枪','弹药','市郊','三街圣徒','兄弟会','主城区','市郊区']:
    print('  %-8s %d'%(kw,allt.count(kw)))
for kw in ['散筒枪','火料','填料','指定辩护律','兄弟帮','城郊','城区']:
    print('  BAD %-8s %d'%(kw,allt.count(kw)))
