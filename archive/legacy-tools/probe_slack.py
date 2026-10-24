# -*- coding: utf-8 -*-
"""摸底：32 条含「城郊」的记录 + 5 条单字「城」记录，
   检查各自周边有没有 0x0020 空格 slot 可吸收 1 个字"""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8')
def load_cl(p):
    xs=[]
    for l in open(p,encoding='utf-8'):
        l=l.strip()
        if not l or l[0] in '/#': continue
        xs.append(int(l))
    return xs
CL=load_cl(r'F:\sr2-cn\_juice_fix\charlist_CH.txt')
IDX={cp:i for i,cp in enumerate(CL)}
def S(c):
    if ord(c) not in IDX: raise KeyError(c)
    return IDX[ord(c)]+0x20
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else '?'
b=open(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc','rb').read()
n=len(b)
SP=0x0020

def rec_bounds(at):
    """at 是某个 slot 的文件偏移。返回 (记录起点, 记录结束含终止符)"""
    p=at
    while p>=2 and struct.unpack_from('>H',b,p-2)[0]!=0: p-=2
    st=p
    q=st; o=[]
    while q+2<=n:
        w=struct.unpack_from('>H',b,q)[0]
        if w==0: break
        o.append(w); q+=2
    return st, q+2, o

def scan(pat):
    hits=[];st=0
    while True:
        i=b.find(pat,st)
        if i<0:break
        hits.append(i); st=i+1
    return hits

print('=== A) 含「城郊」的记录（32 条）===')
pat=struct.pack('>2H',S('城'),S('郊'))
hits=scan(pat)
starts=set()
for i in hits:
    st,en,o=rec_bounds(i)
    starts.add((st,en))
print('命中 %d 处 / 独立记录 %d 条'%(len(hits),len(starts)))
slack_ok=0; slack_bad=[]
for st,en in sorted(starts):
    slots=[struct.unpack_from('>H',b,st+2*k)[0] for k in range((en-st)//2)]
    body=slots[:-1]
    txt=''.join(dec(x) for x in body)
    # 尾部连续空格数
    k=0
    while k<len(body) and body[len(body)-1-k]==SP: k+=1
    # 记录后紧邻的下一个 slot（下一条记录开头）
    nxt=struct.unpack_from('>H',b,en)[0] if en+2<=n else None
    flag='尾部有%d空格'%k if k>0 else '无尾部空格'
    ok = k>0
    if ok: slack_ok+=1
    else: slack_bad.append((st,txt))
    print('  @0x%08X len=%-3d %-8s | %s'%(st,len(body),flag,txt[:56]))
print('  可吸收(尾部空格)的记录 = %d / %d'%(slack_ok,len(starts)))
if slack_bad:
    print('  ★无余量的记录 %d 条：'%len(slack_bad))
    for st,t in slack_bad: print('     @0x%08X %s'%(st,t[:60]))
print()

print('=== B) 精确单字「城」的记录 ===')
pat1=struct.pack('>2H',S('城'),0x0000)
h1=scan(pat1)
print('命中 %d'%len(h1))
for i in h1:
    st,en,o=rec_bounds(i)
    print('  @0x%08X slots=%s  txt=%r  后邻slot=0x%04X'%(
        st,[hex(x) for x in o],''.join(dec(x) for x in o),
        struct.unpack_from('>H',b,en)[0] if en+2<=n else -1))
    for o2 in range(st-16,st,2):
        print('      -%02d 0x%08X slot=0x%04X %r'%(st-o2,o2,struct.unpack_from('>H',b,o2)[0],
              dec(struct.unpack_from('>H',b,o2)[0])))
    for o2 in range(en,en+16,2):
        print('      +%02d 0x%08X slot=0x%04X %r'%(o2-st,o2,struct.unpack_from('>H',b,o2)[0],
              dec(struct.unpack_from('>H',b,o2)[0])))