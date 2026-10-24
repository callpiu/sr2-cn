# -*- coding: utf-8 -*-
"""定位 static_CH 内 5 条单字「城」记录的 ID，再在 static_US 同 ID 找英文原文"""
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
    BT=12; PTR=BT+buckets*8
    recs=[]
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
            recs.append((bi,idx,off,t))
    return recs

v=Vpp(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc')
CH=bytes(v.read(v.find('static_CH','le_strings')))
RCH=parse(CH,True)
v2=Vpp(r"F:\sr2-cn\_ref_第三方补丁\原始基准\patch_第三方原版.vpp_pc")
US=bytes(v2.read(v2.find('static_US','le_strings')))
RUS=parse(US,False)
UMAP={}
for bi,idx,off,t in RUS:
    UMAP[(bi,idx)]=t
UMAP2={idx:t for bi,idx,off,t in RUS}

print('=== static_CH 内精确等于「城」的记录 ===')
n=0
for bi,idx,off,t in RCH:
    if t=='城':
        n+=1
        en1=UMAP.get((bi,idx),'<无>')
        en2=UMAP2.get(idx,'<无>')
        print('  bucket=%-5d idx=%-6d off=0x%06X'%(bi,idx,off))
        print('      EN(同桶同序)=%s'%(en1[:70].encode('utf-8','replace').decode('utf-8')))
        print('      EN(同idx)   =%s'%(en2[:70].encode('utf-8','replace').decode('utf-8')))
print('  共 %d 条'%n)

print()
print('=== 含「Suburb」的英文记录 → 同 idx 的中文 ===')
subs=[(bi,idx,off,t) for bi,idx,off,t in RUS if 'Suburb' in t]
print('  英文含 Suburb = %d 条'%len(subs))
for bi,idx,off,t in subs:
    cn=''
    for a,b,c2,t2 in RCH:
        if a==bi and b==idx: cn=t2; break
    en=t.replace('\n',' ')
    en=en.encode('utf-8','replace').decode('utf-8')
    print('  [%d/%d] EN=%-52s CN=%s'%(bi,idx,en[:52],cn[:40]))