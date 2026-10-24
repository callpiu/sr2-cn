# -*- coding: utf-8 -*-
"""1) 「三街圣徒」这104处的上下文  2) ASCII "3rd" 162处的上下文"""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8')
PATCH=r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
def load_cl(p):
    xs=[]
    for l in open(p,encoding='utf-8'):
        l=l.strip()
        if not l or l.startswith('//') or l.startswith('#'): continue
        xs.append(int(l))
    return xs
CL=load_cl(r'F:\sr2-cn\_juice_fix\charlist_CH.txt')
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else '<%04X>'%s
buf=open(PATCH,'rb').read()

def ctx(start,label,n=40):
    q=start; out=[]
    while q+2<=len(buf):
        v=struct.unpack_from('>H',buf,q)[0]
        if v==0: break
        out.append(v); q+=2
    return ''.join(dec(v) for v in out)

print('=== 1) 含「三街圣徒」的记录（去重显示，最多30 条）===')
pat=b''.join(struct.pack('>H',CL.index(ord(c))+0x20) for c in '三街圣徒')
seen=set();shown=0;st=0;tot=0
while True:
    i=buf.find(pat,st)
    if i<0: break
    tot+=1
    p=i
    while p>=2:
        if struct.unpack_from('>H',buf,p-2)[0]==0: break
        p-=2
    t=ctx(p,'x')
    if t not in seen:
        seen.add(t); shown+=1
        if shown<=30:
            print('  @0x%X  %r'%(i,t))
    st=i+1
print('  共 %d 处，去重后 %d 种不同文本'%(tot,len(seen)))

print()
print('=== 2) ASCII "3rd" 的 162 处（去重，取前 40）===')
p3=b''.join(struct.pack('>H',ord(c)) for c in '3rd')
seen2={};st=0
while True:
    i=buf.find(p3,st)
    if i<0: break
    p=i
    while p>=2:
        if struct.unpack_from('>H',buf,p-2)[0]==0: break
        p-=2
    t=ctx(p,'x')
    seen2.setdefault(t,i)
    st=i+1
print('  去重后 %d 种文本'%len(seen2))
for t,i in list(seen2.items())[:40]:
    print('  @0x%X  %r'%(i,t))

print()
print('=== 3) 当前 patch 里都出现了哪些 gang 名相关译名 ===')
for name in ['三街圣徒','圣徒','兄弟帮','帮派','三合会','帝国','天使','毒蛇','卡彭']:
    if all(ord(c) in CL for c in name):
        s=b''.join(struct.pack('>H',CL.index(ord(c))+0x20) for c in name)
        print('  %-6r 命中 %d 处'%(name,buf.count(s)))
    else:
        print('  %-6r ✗缺字'%name)