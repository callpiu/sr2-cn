# -*- coding: utf-8 -*-
"""核对 50 处「城区」的英文原文 —— 判断 Downtown(城区) / Outskirts(郊区)"""
import os, sys, struct, re, hashlib
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OFF = r"F:\sr2-cn\_ref_第三方补丁\原始基准\patch_第三方原版.vpp_pc"

def load_cl(p):
    xs=[]
    for l in open(p,encoding='utf-8'):
        l=l.strip()
        if not l or l[0] in '/#': continue
        xs.append(int(l))
    return xs
CL=load_cl(r'F:\sr2-cn\_juice_fix\charlist_CH.txt')
IDX={cp:i for i,cp in enumerate(CL)}
def S(ch): return IDX[ord(ch)]+0x20
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else '<%04X>'%s

# ---- 官方英文表：解析全部记录 ----
print('载入官方 static_US ...')
v=Vpp(OFF)
e=v.find('static_US','le_strings')
d=bytes(v.read(e))
print('  static_US size =',len(d))

# 记录格式：[id1 u16 LE][id2 u16 LE][utf16 chars][0x0000]（LE 文本，非 slot）
def parse_en(b):
    recs={}
    i=0; n=len(b)
    while i+4<=n:
        id1,id2=struct.unpack_from('<HH',b,i)
        j=i+4; cs=[]
        while j+2<=n:
            w=struct.unpack_from('<H',b,j)[0]
            if w==0: break
            cs.append(w); j+=2
        else:
            break
        if j>=n: break
        txt=''.join(chr(c) for c in cs)
        if txt:
            recs.setdefault((id1,id2),txt)
        i=j+2
    return recs
EN=parse_en(d)
print('  英文记录数 =',len(EN))

# ---- 中文表：记录 -> 偏移 ----
zh=open(PATCH:=(os.path.join(G,'patch.vpp_pc')),'rb').read()
pat=struct.pack('>2H',S('城'),S('区'))
hits=[];st=0
while True:
    i=zh.find(pat,st)
    if i<0: break
    hits.append(i); st=i+1
print('  「城区」命中 %d 处'%len(hits))
print()

# 中文记录头前 4 字节 = id1,id2
ok=0
for at in hits:
    if at<4: continue
    id1,id2=struct.unpack_from('<HH',zh,at-4)
    key=(id1,id2)
    en=EN.get(key,'<无匹配>')
    if en!='<无匹配>': ok+=1
    else: en='<★英文表无此ID>'
    # 中文上下文
    p=at
    while p>=2 and struct.unpack_from('>H',zh,p-2)[0]!=0: p-=2
    o=[];q=p
    while q+2<=len(zh):
        w=struct.unpack_from('>H',zh,q)[0]
        if w==0: break
        o.append(w); q+=2
    ctxt=''.join(dec(x) for x in o)
    ctxt=ctxt.replace('\n','')
    print('ID %04X/%04X' % (id1,id2))
    print('  CN: %s' % ctxt[:90])
    print('  EN: %s' % en[:120])
    print()
print('ID 匹配英文表 = %d/%d'%(ok,len(hits)))