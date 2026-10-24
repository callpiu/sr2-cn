# -*- coding: utf-8 -*-
"""对比官方 common 与 common_v422 的 vf3 差异"""
import sys, struct, hashlib
sys.path.insert(0,'.')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'

def load_vf3(path):
    v=Vpp(path)
    e=v.find('fnt_chinese','vf3_pc')
    co=v.data_start+e['body']
    N=struct.unpack_from('<I',v.data,co+8)[0]
    return v,co,N

v1,c1,n1=load_vf3(G+'/common.vpp_pc')
v2,c2,n2=load_vf3('_fix_candidates/common_v422.vpp_pc')
print('official N=',n1,' v422 N=',n2)

# U 数组 @ co + 0xAF6C? 先用 v421 里的偏移: U@0xAF6C, V@0xDB18, rec@0xD0
UO, VO, RO = 0xAF6C, 0xDB18, 0xD0
print('检查偏移合理性:')
print('  头部 u32@0..3:',struct.unpack_from('<4I',v1.data,c1)[:4])
print('  N@+8:',struct.unpack_from('<I',v1.data,c1+8)[0])
# 真实 vf3 结构: 头部 0xBC, rec@0xBC? 交接文档说 0xBC. 试算
hdr=0xBC
rec_off=c1+hdr
u_off=rec_off+n1*16
v_off=u_off+n1*4
print('按0xBC: rec@%#x u@%#x v@%#x (file len %#x)'%(rec_off-c1,u_off-c1,v_off-c1,len(v1.data)-c1))
print('v_off+n*4 =',v_off+n1*4-c1)

diffs=[]
for i in range(min(n1,n2)):
    a=struct.unpack_from('<4I',v1.data,rec_off+i*16)
    b=struct.unpack_from('<4I',v2.data,rec_off+i*16)
    ua=struct.unpack_from('<i',v1.data,u_off+i*4)[0]
    ub=struct.unpack_from('<i',v2.data,u_off+i*4)[0]
    va=struct.unpack_from('<i',v1.data,v_off+i*4)[0]
    vb=struct.unpack_from('<i',v2.data,v_off+i*4)[0]
    if (a,b,ua,ub,va,vb) and (a!=b or ua!=ub or va!=vb):
        diffs.append((i,a,b,ua,ub,va,vb))
print('\n差异数:',len(diffs))
for i,a,b,ua,ub,va,vb in diffs:
    print(f'  idx{i}: rec {a}->{b}  U {ua}->{ub}  V {va}->{vb}')
