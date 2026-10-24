# -*- coding: utf-8 -*-
import sys, struct
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0,'.')
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
def parse_records(buf):
    magic, ver, buckets, count = struct.unpack_from('<IHHI', buf, 0)
    offs=[]
    for i in range(buckets):
        c,off=struct.unpack_from('<II',buf,0x0C+i*8)
        for j in range(c): offs.append(struct.unpack_from('<I',buf,off+j*4)[0])
    offs.sort(); recs=[]
    for k,o in enumerate(offs):
        end=offs[k+1] if k+1<len(offs) else len(buf)
        body=buf[o:end]
        h=struct.unpack_from('>I',body,0)[0]
        n=(len(body)-4)//2
        recs.append((h,list(struct.unpack_from('>%dH'%n,body,4))))
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

# 只保留中文字符槽位
def cjk(slots): return [s for s in slots if s>=0x100]

print('=== 搜索: cjk[0:5]=[403,1868,1067,454,364] 且 长度 22 ===')
n=0
for h,s in recs:
    c=cjk(s)
    if len(c)==22 and c[:5]==[403,1868,1067,454,364]:
        print(' 0x%08X: %s'%(h, dec(s)))
        print('        slots:', c)
        n+=1
print('  hits', n)
print()
print('=== 搜索: 含 [403,1868,...,1067,454,364] 且 423 出现在 cjk 第13位 ===')
n=0
for h,s in recs:
    c=cjk(s)
    if len(c)>=20 and c[:5]==[403,1868,1067,454,364] and 423 in c:
        pos=c.index(423)
        print(' 0x%08X pos423=%d len=%d : %s'%(h,pos+1,len(c), dec(s)))
        n+=1
        if n>12: break
print('  hits', n)
print()
print('=== 搜索: 含 2328(要) 与 423(保) 与 1222(护) 与 364(们) 的记录 (前12) ===')
n=0
for h,s in recs:
    c=cjk(s)
    if 2328 in c and 423 in c and 1222 in c:
        print(' 0x%08X len=%d : %s'%(h, len(c), dec(s)))
        n+=1
        if n>12: break
print('  hits', n)
