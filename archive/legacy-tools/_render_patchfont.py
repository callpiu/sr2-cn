# -*- coding: utf-8 -*-
"""用 patch vf3 + patch 图集 渲染 REC1"""
import sys, struct
sys.path.insert(0,'.')
from sr2lib import Vpp, dxt3_decode
from PIL import Image, ImageDraw
import numpy as np
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
vp=Vpp(G+'/patch.vpp_pc')
CL=[int(s) for s in vp.read(vp.find('charlist_CH','txt')).decode('utf-8','ignore').replace('\r','\n').split('\n')
    if s.split('//')[0].strip().isdigit()]

e=vp.find('fnt_chinese','vf3_pc'); co=vp.data_start+e['body']
N=struct.unpack_from('<I',vp.data,co+8)[0]; hdr=0xBC
u_off=co+hdr+N*16; v_off=u_off+N*4
U=[struct.unpack_from('<i',vp.data,u_off+i*4)[0] for i in range(N)]
V=[struct.unpack_from('<i',vp.data,v_off+i*4)[0] for i in range(N)]

g=vp.find('fnt_chinese','g_peg_pc'); gb=vp.data_start+g['body']
raw=vp.data[gb:gb+g['size']]
print('patch atlas size',len(raw))

AT=None
for (w,h) in [(2048,2048),(1024,1024)]:
    try:
        rgb,al=dxt3_decode(raw,w,h)
        AT=Image.fromarray(np.dstack([np.asarray(rgb),np.asarray(al)]).astype('uint8'),'RGBA')
        print('decoded',w,h); break
    except Exception as ex:
        print(w,h,'fail',ex)

# 也试 common atlas (textures)
vt=Vpp(G+'/textures.vpp_pc')
te=[x for x in vt.entries() if x['name']=='fnt_chinese'][0]
raw2=vt.data[vt.data_start+te['body']:vt.data_start+te['body']+te['size']]
try:
    rgb2,al2=dxt3_decode(raw2,2048,2048)
    AT2=Image.fromarray(np.dstack([np.asarray(rgb2),np.asarray(al2)]).astype('uint8'),'RGBA')
    print('common atlas decoded')
except Exception as ex:
    AT2=None; print('common atlas fail',ex)

REC1=[403,1868,1067,454,364,2699,2328,403,1868,423,1222]
CELL=31
def strip(AT,offsets,label,out):
    if AT is None: print('no atlas'); return
    im=Image.new('RGBA',(len(REC1)*50+40, len(offsets)*50+8),(20,20,28,255))
    d=ImageDraw.Draw(im)
    for r,off in enumerate(offsets):
        d.text((2,r*50+20),str(off),fill=(255,255,0))
        for c,s in enumerate(REC1):
            idx=s-0x20+off
            if 0<=idx<N:
                x,y=U[idx],V[idx]
                tile=AT.crop((x,y,x+CELL,y+CELL)).resize((46,46),Image.NEAREST)
                im.alpha_composite(tile,(c*50+40, r*50+2))
    im.save(out); print('saved',out)

# charlist 目标
print('目标字:', ''.join(chr(CL[s-0x20]) for s in REC1))
for AT,nm in [(AT,'patch'),(AT2,'commonTex')]:
    strip(AT,[0],f'{nm}_idx=slot-0x20',f'F:/sr2-cn/_J_{nm}_0.png')
    strip(AT,[-32],f'{nm}_idx=slot-0x40',f'F:/sr2-cn/_J_{nm}_m32.png')
