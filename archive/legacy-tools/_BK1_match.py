# -*- coding: utf-8 -*-
import sys, struct
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from _vpp import Vpp
gv=Vpp(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc')
def pc(buf):
    out=[]
    for ln in buf.decode('latin-1').splitlines():
        s=ln.strip()
        if not s or s.startswith('//') or s.startswith('count'): continue
        try: out.append(int(s))
        except: pass
    return out
cl=pc(gv.read(gv.find('charlist_CH')))
inv={}
for i,c in enumerate(cl): inv.setdefault(c,i)
def parse_records(buf):
    magic, ver, buckets, count = struct.unpack_from('<IHHI', buf, 0)
    offs=[]
    for i in range(buckets):
        c,off=struct.unpack_from('<II',buf,0x0C+i*8)
        for j in range(c): offs.append(struct.unpack_from('<I',buf,off+j*4)[0])
    offs.sort(); recs=[]
    for k,o in enumerate(offs):
        end = offs[k+1] if k+1<len(offs) else len(buf)
        body=buf[o:end]
        h=struct.unpack_from('>I',body,0)[0]
        n=(len(body)-4)//2
        recs.append((h, list(struct.unpack_from('>%dH'%n, body, 4))))
    return recs
def dec(slots):
    out=''
    for s in slots:
        if s==0: continue
        if s<0x100: out+=chr(s)
        else:
            i=s-32; out += chr(cl[i]) if 0<=i<len(cl) else '?'
    return out
recs=parse_records(gv.read(gv.find('static_CH')))
# S1 推出的映射
M = {371:336, 1836:1784, 1035:410, 422:967, 332:362, 2667:2656, 2296:2268, 391:354, 1190:2342}
invM = {v:k for k,v in M.items()}
# S2 渲染出的索引序列
s2_idx = [336,1784,410,967,362,1458,2268,535,2491,2234,287,1292,354,2342,301,362,2514,417,543,458,1243,1221]
print('S2 渲染序列中，能用 S1 映射反推源字的:')
for i,x in enumerate(s2_idx):
    if x in invM:
        print('   pos%d idx=%d -> 源字 %s'%(i+1, x, chr(cl[invM[x]])))
print()
# 搜索: 含 你的 弟兄们 保护 的记录，打印全部
print('=== 含「弟兄们」的全部记录 ===')
for h,s in recs:
    t=dec(s)
    if '弟兄们' in t:
        print(' 0x%08X: %s'%(h,t))
print()
print('=== 含「你的」且含「保护」的记录 (前 25) ===')
n=0
for h,s in recs:
    t=dec(s)
    if '你的' in t and '保护' in t:
        print(' 0x%08X: %s'%(h,t)); n+=1
        if n>25: break
