# -*- coding: utf-8 -*-
"""渲染 common vf3 指定索引的字形, 以及 charlist 对应字, 找出正确索引公式"""
import sys, struct
sys.path.insert(0,'.')
from sr2lib import Vpp
from PIL import Image, ImageDraw
import numpy as np

G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
vp=Vpp(G+'/patch.vpp_pc')
CL=[int(s) for s in vp.read(vp.find('charlist_CH','txt')).decode('utf-8','ignore').replace('\r','\n').split('\n')
    if s.split('//')[0].strip().isdigit()]

v=Vpp(G+'/common.vpp_pc')
e=v.find('fnt_chinese','vf3_pc'); co=v.data_start+e['body']
N=struct.unpack_from('<I',v.data,co+8)[0]
hdr=0xBC
u_off=co+hdr+N*16; v_off=u_off+N*4
U=[struct.unpack_from('<i',v.data,u_off+i*4)[0] for i in range(N)]
V=[struct.unpack_from('<i',v.data,v_off+i*4)[0] for i in range(N)]
W=[struct.unpack_from('<I',v.data,co+hdr+i*16)[0] for i in range(N)]

# atlas in textures.vpp (fnt_chinese, 4194304 = 2048x2048 DXT3?) - 用 sr2lib.dxt3_decode
vt=Vpp(G+'/textures.vpp_pc')
te=[x for x in vt.entries() if x['name']=='fnt_chinese'][0]
ab=vt.data_start+te['body']
raw=vt.data[ab:ab+te['size']]
print('atlas size',len(raw))
# 尝试 sr2lib dxt3_decode
try:
    from sr2lib import dxt3_decode
    rgb,al=dxt3_decode(raw,2048,2048)
    AT=Image.fromarray(np.dstack([np.asarray(rgb),np.asarray(al)]).astype('uint8'),'RGBA')
    print('decoded atlas',AT.size)
except Exception as ex:
    print('dxt3 fail',ex)
    AT=None

# 渲染指定索引的 32x32 字形
CELL=31
def glyph(idx, size=48):
    if not (0<=idx<N): return None
    x,y=U[idx],V[idx]
    if AT is None: return None
    # atlas 坐标(x,y) -> 取 CELLxCELL 区域
    tile=AT.crop((x, y, x+CELL, y+CELL)).resize((size,size), Image.NEAREST)
    # 深色底
    bg=Image.new('RGBA',(size,size),(25,25,35,255))
    bg.alpha_composite(tile)
    return bg

tests=[('你',403),('的',1868),('弟',1067),('兄',454),('们',364),('需',2699),('要',2328),('保',423),('护',1222)]
if AT:
    im=Image.new('RGBA',(len(tests)*56, 5*56),(20,20,28,255))
    d=ImageDraw.Draw(im)
    for col,(ch,s) in enumerate(tests):
        cands=[s-0x20, s-0x40, s, s-0x20-0x20]
        for row,c in enumerate(cands[:5]):
            g=glyph(c)
            if g: im.alpha_composite(g,(col*56+4, row*56+4))
            d.text((col*56+4, 0), str(c), fill=(255,255,0))
    im.save('F:/sr2-cn/_I1_uv_glyphs.png')
    print('saved _I1_uv_glyphs.png')
    # 打印每列首行字
    print('列(目标字): 候选索引')
    for ch,s in tests:
        print(f'  {ch} slot{s}: idx{s-0x20} idx{s-0x40} idx{s}')
