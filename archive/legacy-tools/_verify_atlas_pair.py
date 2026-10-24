# -*- coding: utf-8 -*-
"""验证 common vf3 UV 与 common/textures 图集是否配套: 渲染 ASCII 与已知字"""
import sys, struct
sys.path.insert(0,'.')
from sr2lib import Vpp, dxt3_decode
from PIL import Image, ImageDraw
import numpy as np
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'

def load(path,name,ext):
    v=Vpp(path)
    e=v.find(name,ext); b=v.data_start+e['body']
    return v,e,b

# common vf3
v,e,b=load(G+'/common.vpp_pc','fnt_chinese','vf3_pc')
N=struct.unpack_from('<I',v.data,b+8)[0]; hdr=0xBC
u_off=b+hdr+N*16; v_off=u_off+N*4
U=[struct.unpack_from('<i',v.data,u_off+i*4)[0] for i in range(N)]
V=[struct.unpack_from('<i',v.data,v_off+i*4)[0] for i in range(N)]
print('common vf3 N',N)
print('U[0..12]',U[:12]); print('V[0..12]',V[:12])
print('U[300..312]',U[300:312]); print('V[300..312]',V[300:312])

# common 图集
v2,e2,b2=load(G+'/textures.vpp_pc','fnt_chinese','')
raw=v2.data[b2:b2+e2['size']]
rgb,al=dxt3_decode(raw,2048,2048)
AT=Image.fromarray(np.dstack([np.asarray(rgb),np.asarray(al)]).astype('uint8'),'RGBA')

# patch 图集
vp=Vpp(G+'/patch.vpp_pc')
ep=vp.find('fnt_chinese','g_peg_pc'); bp=vp.data_start+ep['body']
rawp=vp.data[bp:bp+ep['size']]
rgbp,alp=dxt3_decode(rawp,2048,2048)
ATP=Image.fromarray(np.dstack([np.asarray(rgbp),np.asarray(alp)]).astype('uint8'),'RGBA')

# patch vf3
ep2=vp.find('fnt_chinese','vf3_pc'); bp2=vp.data_start+ep2['body']
Np=struct.unpack_from('<I',vp.data,bp2+8)[0]
up=bp2+hdr+Np*16; vp_=up+Np*4
UP=[struct.unpack_from('<i',vp.data,up+i*4)[0] for i in range(Np)]
VP=[struct.unpack_from('<i',vp.data,vp_+i*4)[0] for i in range(Np)]
print('patch vf3 N',Np,'U[0..12]',UP[:12])

# 渲染: common vf3 idx (0..24) 用 common 图集 和 patch 图集
def grid(UV,AT,idxs,cell,out,title):
    im=Image.new('RGBA',(len(idxs)*cell+4, 2*cell+24),(20,20,28,255))
    d=ImageDraw.Draw(im); d.text((2,2),title,fill=(255,255,0))
    for c,i in enumerate(idxs):
        x,y=UV[0][i],UV[1][i]
        t=AT.crop((x,y,x+cell-2,y+cell-2)).resize((cell-4,cell-4),Image.NEAREST)
        im.alpha_composite(t,(c*cell+2,20))
    im.save(out); print('saved',out)

idxs=list(range(0,26))
grid((U,V),AT,idxs,44,'F:/sr2-cn/_K1_commonvf3_commonAT.png','commonvf3+commonAT idx0-25')
grid((U,V),ATP,idxs,44,'F:/sr2-cn/_K2_commonvf3_patchAT.png','commonvf3+patchAT idx0-25')
grid((UP,VP),ATP,idxs,44,'F:/sr2-cn/_K3_patchvf3_patchAT.png','patchvf3+patchAT idx0-25 (应=ABCDEFG...)')
