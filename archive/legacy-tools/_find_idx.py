# -*- coding: utf-8 -*-
"""穷举: 在 common vf3 里找能渲染出实测乱码字的索引"""
import sys, struct
sys.path.insert(0,'.')
from sr2lib import Vpp, dxt3_decode
from PIL import Image
import numpy as np
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'

# 实测乱码 (正确字 -> 显示字)
GARBLE={0x4F60:0x4EFB,0x7684:0x74A8,0x5F1F:0x5076,0x5144:0x5DE7,0x4EEC:0x4F4D,
        0x9700:0x96C4,0x8981:0x8861,0x4FDD:0x4F2A,0x62A4:0x8BE5}
# 反向: 显示字码点
WANT=[(chr(k),chr(v)) for k,v in GARBLE.items()]
print('正确->显示:',WANT)

def load_vf3(p):
    v=Vpp(p); e=v.find('fnt_chinese','vf3_pc'); b=v.data_start+e['body']
    N=struct.unpack_from('<I',v.data,b+8)[0]; hdr=0xBC
    u=b+hdr+N*16; vv=u+N*4
    U=[struct.unpack_from('<i',v.data,u+i*4)[0] for i in range(N)]
    V=[struct.unpack_from('<i',v.data,vv+i*4)[0] for i in range(N)]
    return U,V,N

vt=Vpp(G+'/textures.vpp_pc')
te=[x for x in vt.entries() if x['name']=='fnt_chinese'][0]
raw=vt.data[vt.data_start+te['body']:vt.data_start+te['body']+te['size']]
rgb,al=dxt3_decode(raw,2048,2048)
AT=Image.fromarray(np.dstack([np.asarray(rgb),np.asarray(al)]).astype('uint8'),'RGBA')

U,V,N=load_vf3(G+'/common.vpp_pc')
vp=Vpp(G+'/patch.vpp_pc')
CL=[int(s) for s in vp.read(vp.find('charlist_CH','txt')).decode('utf-8','ignore').replace('\r','\n').split('\n')
    if s.split('//')[0].strip().isdigit()]
SP={c:i for i,c in enumerate(CL)}   # 码点 -> charlist idx

# 实测显示字的 charlist idx (即"引擎取到的索引")
print('\n显示字的 charlist 索引:')
for k,v in GARBLE.items():
    print(f'  {chr(k)}->{chr(v)}: 显示字idx={SP.get(v)}  源字idx={SP.get(k)}  差={SP.get(v)-SP.get(k) if v in SP and k in SP else "-"}')

# 渲染显示字在 common 里的位置，验证
CELL=31
idxs=[]
for k,v in GARBLE.items():
    id_=SP.get(v)
    if id_ is not None: idxs.append(id_)
print('\n显示字idx:',idxs)
im=Image.new('RGBA',(len(idxs)*50+8,56),(20,20,28,255))
for c,i in enumerate(idxs):
    x,y=U[i],V[i]
    t=AT.crop((x,y,x+CELL,y+CELL)).resize((46,46),Image.NEAREST)
    im.alpha_composite(t,(c*50+4,4))
im.save('F:/sr2-cn/_M1_showidx_common.png'); print('saved _M1_showidx_common.png')
