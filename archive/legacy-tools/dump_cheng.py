# -*- coding: utf-8 -*-
"""dump「城」单字记录 及 所有含「城郊」的记录 上下文"""
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
def S(c): return IDX[ord(c)]+0x20
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else ''
b=open(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc','rb').read()
n=len(b)
def dump(at,label):
    print('--- %s @0x%08X ---'%(label,at))
    lo=max(0,at-24); hi=min(n,at+24)
    for o in range(lo,hi,2):
        w=struct.unpack_from('>H',b,o)[0]
        print('   0x%08X  slot=0x%04X  %r'%(o,w,dec(w) if 0x20<=w<0x20+len(CL) else ''))
    print()

for at in (0x019F0ED8, 0x01AC1094):
    dump(at,'单字「城」')

print()
print('=== 所有含「城郊」的记录 ===')
pat=struct.pack('>2H',S('城'),S('郊'))
st=0
while True:
    i=b.find(pat,st)
    if i<0:break
    p=i
    while p>=2 and struct.unpack_from('>H',b,p-2)[0]!=0: p-=2
    o=[];q=p
    while q+2<=n:
        w=struct.unpack_from('>H',b,q)[0]
        if w==0:break
        o.append(w);q+=2
    print('  @0x%08X %r'%(p,''.join(dec(x) for x in o).replace('\n','')))
    st=i+1