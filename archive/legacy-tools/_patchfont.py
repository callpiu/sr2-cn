# -*- coding: utf-8 -*-
"""patch 自带 vf3 + 图集 渲染测试"""
import sys, struct
sys.path.insert(0,'.')
from sr2lib import Vpp, dxt3_decode
from PIL import Image, ImageDraw
import numpy as np

G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
vp=Vpp(G+'/patch.vpp_pc')
CL=[int(s) for s in vp.read(vp.find('charlist_CH','txt')).decode('utf-8','ignore').replace('\r','\n').split('\n')
    if s.split('//')[0].strip().isdigit()]
print('patch charlist',len(CL))

# patch 里的字体条目
fe=[e for e in vp.entries() if 'fnt_chinese' in e['name'].lower()]
print('patch fnt entries:',[(e['name'],e['ext'],e['size']) for e in fe])
for e in fe:
    print(' ',e['name'],e['ext'],'head:',vp.data[vp.data_start+e['body']:vp.data_start+e['body']+16].hex(' '))

# vf3 结构
e=[x for x in fe if x['ext']=='vf3_pc'][0]
co=vp.data_start+e['body']
N=struct.unpack_from('<I',vp.data,co+8)[0]
print('patch vf3 N=',N)
hdr=0xBC
u_off=co+hdr+N*16; v_off=u_off+N*4
U=[struct.unpack_from('<i',vp.data,u_off+i*4)[0] for i in range(N)]
V=[struct.unpack_from('<i',vp.data,v_off+i*4)[0] for i in range(N)]
print('U head',U[:8],'V head',V[:8])
print('file len check: v_off+N*4-co =',v_off+N*4-co,'entry size',e['size'])

# 图集: patch 里的 g_peg_pc
ge=[x for x in fe if 'peg' in x['ext']]
print('peg entries:',[(x['name'],x['ext'],x['size']) for x in ge])
if ge:
    g=ge[0]; gb=vp.data_start+g['body']
    raw=vp.data[gb:gb+g['size']]
    print('peg head',raw[:32].hex(' '))
