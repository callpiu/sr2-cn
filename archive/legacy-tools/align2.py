# -*- coding: utf-8 -*-
"""正确解析 static_CH/static_US 头，按桶展开对齐两表，抽出「城」相关记录英文原文"""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

def load_cl(p):
    xs=[]
    for l in open(p,encoding='utf-8'):
        l=l.strip()
        if not l or l[0] in '/#': continue
        xs.append(int(l))
    return xs
CL=load_cl(r'F:\sr2-cn\_juice_fix\charlist_CH.txt')
IDX={cp:i for i,cp in enumerate(CL)}
def S(c): return IDX[ord(c)]+0x20
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else ''

def parse(blob, is_slot):
    buckets=struct.unpack_from('<H',blob,6)[0]
    count=struct.unpack_from('<I',blob,8)[0]
    BT=12
    PTR=BT+buckets*8
    recs={}
    for bi in range(buckets):
        n,addr=struct.unpack_from('<II',blob,BT+bi*8)
        for k in range(n):
            idx=addr+k
            if idx>=count: continue
            off=struct.unpack_from('<I',blob,PTR+idx*4)[0]
            q=off;o=[]
            while q+2<=len(blob):
                w=struct.unpack_from('>H',blob,q)[0]
                if w==0: break
                o.append(w);q+=2
            t=''.join(dec(x) for x in o) if is_slot else ''.join(chr(x) for x in o)
            recs[idx]=t
    return buckets,count,recs

v=Vpp(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc')
CH=bytes(v.read(v.find('static_CH','le_strings')))
bk,ct,RCH=parse(CH,True)
print('static_CH buckets=%d count=%d 记录=%d'%(bk,ct,len(RCH)))
v2=Vpp(r"F:\sr2-cn\_ref_第三方补丁\原始基准\patch_第三方原版.vpp_pc")
US=bytes(v2.read(v2.find('static_US','le_strings')))
bk2,ct2,RUS=parse(US,False)
print('static_US buckets=%d count=%d 记录=%d'%(bk2,ct2,len(RUS)))
print()

print('=== CH 含「城」的记录 → 英文原文 ===')
for idx in sorted(RCH):
    t=RCH[idx]
    if '城' in t:
        print('  [%05d] %-38s | EN=%s'%(idx,t[:38].replace('\n',''),RUS.get(idx,'<无>')[:70]))
print()
print('=== CH 短中文记录（<=4字全CJK）→ EN ===')
n=0
for idx in sorted(RCH):
    t=RCH[idx].replace('\n','')
    if 0<len(t)<=4 and all(0x4e00<=ord(c)<=0x9fff for c in t):
        en=RUS.get(idx,'')
        if en and len(en)<=40:
            print('  [%05d] %-8s | EN=%s'%(idx,t,en[:60])); n+=1
print('  共',n)