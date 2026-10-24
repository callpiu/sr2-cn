# -*- coding: utf-8 -*-
"""对比各版本 patch 的 REC1/REC2 slot"""
import sys, struct
sys.path.insert(0,'.')
from sr2lib import Vpp
import os

def decode_recs(vpp_path, name='static_CH'):
    v=Vpp(vpp_path)
    e=None
    for x in v.entries():
        if x['name']==name and x['ext']=='le_strings': e=x;break
    if e is None: return None
    data=v.read(e)
    magic,ver,buckets,count=struct.unpack_from('<IHHI',data,0)
    ptra=12+buckets*8
    offs=struct.unpack_from('<%dI'%count,data,ptra)
    out={}
    for off in set(offs):
        i1,i2=struct.unpack_from('<HH',data,off)
        j=off+4; sl=[]
        while j+2<=len(data):
            s=struct.unpack_from('>H',data,j)[0]
            if s==0: break
            sl.append(s); j+=2
        out[(i1<<16)|i2]=sl
    return out

files=[('当前v534','G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc'),
       ('v422','_fix_candidates/patch_v422.vpp_pc'),
       ('v421','_fix_candidates/patch_v421.vpp_pc'),
       ('v515','_fix_candidates/patch_v515.vpp_pc'),
       ('v513','_fix_candidates/patch_v513.vpp_pc')]
for nm,p in files:
    if not os.path.exists(p): print(nm,'missing'); continue
    r=decode_recs(p)
    if r is None: print(nm,'no static_CH'); continue
    r1=r.get(0x84F287ED); r2=r.get(0x10AF1E62)
    print(f'--- {nm} ---')
    print('  REC1:',r1)
    print('  REC2:',r2)
