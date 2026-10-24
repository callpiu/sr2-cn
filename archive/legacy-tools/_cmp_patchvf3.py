# -*- coding: utf-8 -*-
"""对比 patch vf3: 当前v534 vs v422 vs 官方pristine; 及 patch g_peg_pc 差异"""
import sys, struct, os
sys.path.insert(0,'.')
from sr2lib import Vpp
def vf3(p):
    v=Vpp(p); e=v.find('fnt_chinese','vf3_pc'); b=v.data_start+e['body']
    N=struct.unpack_from('<I',v.data,b+8)[0]; hdr=0xBC
    u=b+hdr+N*16; vv=u+N*4
    U=[struct.unpack_from('<i',v.data,u+i*4)[0] for i in range(N)]
    V=[struct.unpack_from('<i',v.data,vv+i*4)[0] for i in range(N)]
    return U,V,N
def peg_md5(p):
    import hashlib
    v=Vpp(p); e=v.find('fnt_chinese','g_peg_pc'); b=v.data_start+e['body']
    return hashlib.md5(v.data[b:b+e['size']]).hexdigest()

files=[('当前v534','G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc'),
       ('v422','_fix_candidates/patch_v422.vpp_pc'),
       ('pristine','pristine/patch.vpp_pc')]
res={}
for nm,p in files:
    if not os.path.exists(p): print(nm,'missing'); continue
    U,V,N=vf3(p); res[nm]=(U,V,N)
    print(f'{nm}: N={N} U[0..6]={U[:6]} pegMD5={peg_md5(p)}')

# 对比 v534 vs v422
if '当前v534' in res and 'v422' in res:
    U1,V1,N1=res['当前v534']; U2,V2,N2=res['v422']
    n=min(N1,N2); diffs=[]
    for i in range(n):
        if U1[i]!=U2[i] or V1[i]!=V2[i]: diffs.append((i,U1[i],U2[i],V1[i],V2[i]))
    print(f'\nv534 vs v422 patch-vf3 差异 {len(diffs)}:')
    for d in diffs[:20]: print('  ',d)
