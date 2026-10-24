# -*- coding: utf-8 -*-
"""解码当前部署(patch.vpp_pc) 里 REC1/REC2 的 slot 状态"""
import sys, struct
sys.path.insert(0,'.')
from sr2lib import Vpp
import hashlib

G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v=Vpp(G+'/patch.vpp_pc')
print('patch entries', len(v.entries()))

# 找 static_CH
cands=[e for e in v.entries() if e['ext']=='le_strings']
print('le_strings entries:', [(e['name'],e['ext'],e['size']) for e in cands])

def decode_records(data):
    magic,ver,buckets,count=struct.unpack_from('<IHHI',data,0)
    assert magic==0xA84C7F73, hex(magic)
    ptra=12+buckets*8
    offs=struct.unpack_from('<%dI'%count, data, ptra)
    recs={}
    for off in set(offs):
        if off+4>len(data): continue
        i1,i2=struct.unpack_from('<HH',data,off)
        j=off+4; sl=[]
        while j+2<=len(data):
            s=struct.unpack_from('>H',data,j)[0]
            if s==0: break
            sl.append(s); j+=2
        recs[(i1,i2)]=(off,sl)
    return buckets,count,recs

targets={0x84F287ED:'REC1(你的弟兄们需要你的保护)',0x10AF1E62:'REC2(…保护他们免遭袭击)'}
for e in cands:
    if 'static' not in e['name'].lower(): continue
    data=v.read(e)
    try:
        b,c,recs=decode_records(data)
    except Exception as ex:
        print(e['name'],'parse err',ex); continue
    print(f"\n=== {e['name']} buckets={b} count={c} ===")
    for (i1,i2),(off,sl) in recs.items():
        h=(i1<<16)|i2
        if h in targets or i2 in targets:
            print(f'  hash={h:#x} {targets.get(h,"")} off={off} slots({len(sl)})={sl}')
