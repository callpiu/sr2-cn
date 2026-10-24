import sys, struct
sys.stdout.reconfigure(encoding='utf-8')

PATCH=r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
OLD='你的弟兄们需要你的保护'

def load_cl(p):
    xs=[]
    for l in open(p,encoding='utf-8'):
        l=l.strip()
        if not l or l.startswith('//') or l.startswith('#'): continue
        xs.append(int(l))
    return xs
CL=load_cl(r'F:\sr2-cn\_juice_fix\charlist_CH.txt')
idx={cp:i for i,cp in enumerate(CL)}

slots=[idx[ord(c)]+0x20 for c in OLD]
pat=struct.pack('>%dH'%len(slots),*slots)
print('目标 slot 序列 =',[hex(s) for s in slots])
print('BE 搜索模式 =',pat.hex())
print()

buf=open(PATCH,'rb').read()
print('patch.vpp_pc = %d 字节'%len(buf))
hits=[];st=0
while True:
    i=buf.find(pat,st)
    if i<0: break
    hits.append(i); st=i+1
print('命中 %d 处'%len(hits))
for h in hits:
    print()
    print('  文件偏移 0x%X' % h)
    rec=h-4
    rid=struct.unpack_from('<I',buf,rec)[0]
    print('    前4字节 ID = 0x%08X'%rid)
    # 解码本记录
    n=0; out=[]
    p=h
    while True:
        if p+2>len(buf): break
        s=struct.unpack_from('>H',buf,p)[0]
        if s==0: break
        out.append(s); p+=2
    txt=''.join(chr(cp[idx2]) if False else '?' for cp,idx2 in [])
    dec=[]
    for s in out:
        if s>=0x20 and (s-0x20)<len(CL): dec.append(chr(CL[s-0x20]))
        else: dec.append('<%04X>'%s)
    print('    记录长度 = %d 字'%len(out))
    print('    解码 = %r'%''.join(dec))
    print('    终止符 @0x%X = 0x%04X'%(p,struct.unpack_from('>H',buf,p)[0]))
    print('    下一条记录 @0x%X'%(p+2))