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
idx={cp:i for i,cp in enumerate(CL)}
buf=open(PATCH,'rb').read()

def slot(ch): return idx[ord(ch)]+0x20
def dec(s):
    return chr(CL[s-0x20]) if s>=0x20 and (s-0x20)<len(CL) else '<%04X>'%s

def scan(text,label):
    s=[slot(c) for c in text]
    pat=struct.pack('>%dH'%len(s),*s)
    hits=[];st=0
    while True:
        i=buf.find(pat,st)
        if i<0: break
        hits.append(i); st=i+1
    print('=== %s %r  命中 %d 处'%(label,text,len(hits)))
    for h in hits:
        # 往前找记录起点：扫描直到 slot==0 或不合法
        p=h
        while p>=0:
            v=struct.unpack_from('>H',buf,p)[0]
            if v==0: break
            p-=2
        start=p+2
        rec=start-4
        rid=struct.unpack_from('<I',buf,rec)[0] if rec>=0 else 0
        # 解码整条
        q=start; out=[]
        while q+2<=len(buf):
            v=struct.unpack_from('>H',buf,q)[0]
            if v==0: break
            out.append(v); q+=2
        print('   文本起始 @0x%X  记录ID字段@0x%X=0x%08X'%(start,rec,rid))
        print('   全记录(%d字)= %r'%(len(out),''.join(dec(v) for v in out)))
        print('   终止符 @0x%X   后随4字节=%s'%(q,buf[q+2:q+6].hex()))
    print()

scan('你的弟兄','前缀4')
scan('需要你的保护','后缀5')
scan('保护他们免遭袭击','REC2片段')