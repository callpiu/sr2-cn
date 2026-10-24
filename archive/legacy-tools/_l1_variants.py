# -*- coding: utf-8 -*-
"""★ 关键: 用 v422 common 的 vf3 + common图集 渲染 REC1 的 9 个 slot,
   对比 官方 common / v422 common 是否不同"""
import sys, struct
sys.path.insert(0,'.')
from sr2lib import Vpp, dxt3_decode
from PIL import Image, ImageDraw
import numpy as np
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'

def load_vf3(p):
    v=Vpp(p); e=v.find('fnt_chinese','vf3_pc'); b=v.data_start+e['body']
    N=struct.unpack_from('<I',v.data,b+8)[0]; hdr=0xBC
    u=b+hdr+N*16; vv=u+N*4
    U=[struct.unpack_from('<i',v.data,u+i*4)[0] for i in range(N)]
    V=[struct.unpack_from('<i',v.data,vv+i*4)[0] for i in range(N)]
    return U,V,N

# atlas from textures (官方)
vt=Vpp(G+'/textures.vpp_pc')
te=[x for x in vt.entries() if x['name']=='fnt_chinese'][0]
raw=vt.data[vt.data_start+te['body']:vt.data_start+te['body']+te['size']]
rgb,al=dxt3_decode(raw,2048,2048)
AT=Image.fromarray(np.dstack([np.asarray(rgb),np.asarray(al)]).astype('uint8'),'RGBA')

REC1=[403,1868,1067,454,364,2699,2328,423,1222]
vp=Vpp(G+'/patch.vpp_pc')
CL=[int(s) for s in vp.read(vp.find('charlist_CH','txt')).decode('utf-8','ignore').replace('\r','\n').split('\n')
    if s.split('//')[0].strip().isdigit()]
print('目标:', ''.join(chr(CL[s-0x20]) for s in REC1))

variants=[('官方common',G+'/common.vpp_pc'),
          ('v421',  '_fix_candidates/common_v421.vpp_pc'),
          ('v422',  '_fix_candidates/common_v422.vpp_pc'),
          ('exp',   '_fix_candidates/exp_common.vpp_pc')]
CELL=31
im=Image.new('RGBA',(len(REC1)*50+90, len(variants)*52+8),(20,20,28,255))
d=ImageDraw.Draw(im)
for r,(nm,p) in enumerate(variants):
    U,V,N=load_vf3(p)
    d.text((2,r*52+20),nm,fill=(255,255,0))
    for c,s in enumerate(REC1):
        for off,tag in [(0,'')]:
            idx=s-0x20
            if 0<=idx<N:
                x,y=U[idx],V[idx]
                t=AT.crop((x,y,x+CELL,y+CELL)).resize((46,46),Image.NEAREST)
                im.alpha_composite(t,(c*50+88, r*52+2))
im.save('F:/sr2-cn/_L1_variants_slot.png'); print('saved')
# 也渲染 slot-0x40
im2=Image.new('RGBA',(len(REC1)*50+90, len(variants)*52+8),(20,20,28,255))
d2=ImageDraw.Draw(im2)
for r,(nm,p) in enumerate(variants):
    U,V,N=load_vf3(p)
    d2.text((2,r*52+20),nm+'-32',fill=(255,255,0))
    for c,s in enumerate(REC1):
        idx=s-0x40
        if 0<=idx<N:
            x,y=U[idx],V[idx]
            t=AT.crop((x,y,x+CELL,y+CELL)).resize((46,46),Image.NEAREST)
            im2.alpha_composite(t,(c*50+88, r*52+2))
im2.save('F:/sr2-cn/_L2_variants_slotm32.png'); print('saved')
