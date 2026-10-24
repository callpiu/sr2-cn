# -*- coding: utf-8 -*-
"""★ 渲染验证: 当前 v534 patch 的 REC slots + 官方common / v422common
   按真正的渲染路径(common vf3 + textures atlas) 渲染, 看哪个正确"""
import sys, struct
sys.path.insert(0,'.')
from sr2lib import Vpp
from PIL import Image, ImageDraw
import numpy as np

G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
CL_PATH=G+'/patch.vpp_pc'     # charlist 来源(patch)
TEX_PATH=G+'/textures.vpp_pc' # atlas 来源

# --- 读 charlist (2795) ---
vp=Vpp(CL_PATH)
CL=[int(s) for s in vp.read(vp.find('charlist_CH','txt')).decode('utf-8','ignore').replace('\r','\n').split('\n')
    if s.split('//')[0].strip().isdigit()]

def load_vf3(common_path):
    v=Vpp(common_path)
    e=v.find('fnt_chinese','vf3_pc'); co=v.data_start+e['body']
    N=struct.unpack_from('<I',v.data,co+8)[0]
    hdr=0xBC
    u_off=co+hdr+N*16; v_off=u_off+N*4
    U=[struct.unpack_from('<i',v.data,u_off+i*4)[0] for i in range(N)]
    V=[struct.unpack_from('<i',v.data,v_off+i*4)[0] for i in range(N)]
    W=[struct.unpack_from('<I',v.data,co+hdr+i*16)[0] for i in range(N)]
    return U,V,W,N

# --- atlas ---
vt=Vpp(TEX_PATH)
te=None
for e in vt.entries():
    if e['name']=='fnt_chinese':
        te=e; break
print('atlas entry:',te['name'],te['ext'],te['size'])
body=vt.data_start+te['body']
# fnt_chinese 是 peg 里的纹理? 先看头部
print('atlas head:',vt.data[body:body+16].hex(' '))

def render(common_path, slots, label, out):
    U,V,W,N=load_vf3(common_path)
    print(f'[{label}] N={N}')
    im=Image.new('RGBA',(len(slots)*36,44),(30,30,40,255))
    d=ImageDraw.Draw(im)
    for k,s in enumerate(slots):
        ci=s-0x20
        if 0<=ci<len(CL): pass
    im.save(out); print('saved',out)

# 只打印前 12 个 slot 的索引推算
REC1=[403, 1868, 91, 102, 111, 114, 109, 97, 116, 93, 91, 99, 111, 108, 111, 114, 58, 103, 114, 101, 101, 110, 93, 1067, 454, 364, 91, 47, 102, 111, 114, 109, 97, 116, 93, 2699, 2328, 403, 1868, 423, 1222]
cjk=[s for s in REC1 if s>=0x100]
print('REC1 CJK slots:',cjk)
print('对应字符(charlist):', ''.join(chr(CL[s-0x20]) if 0<=s-0x20<len(CL) else '?' for s in cjk))

for cp in [G+'/common.vpp_pc','_fix_candidates/common_v422.vpp_pc']:
    U,V,W,N=load_vf3(cp)
    print(f'\n=== {cp} ===')
    print('各 slot 三条路径的 UV:')
    for s in cjk:
        i1=s-0x20; i2=s-0x40; i3=s
        def uv(i): return (U[i],V[i]) if 0<=i<N else None
        ch=chr(CL[i1]) if 0<=i1<len(CL) else '?'
        print(f'  slot{s} ({ch}): idx{i1}UV={uv(i1)}  idx{i2}UV={uv(i2)}  idx{i3}UV={uv(i3)}')
