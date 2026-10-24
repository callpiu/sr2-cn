# -*- coding: utf-8 -*-
"""修正 le_strings 解析：
header(16) + buckets*8 字节桶表(从0x10开始, 每项=<u32 off><u32 flag>)
记录体在 off 处: <u16 hash?><...>
"""
import sys, struct
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v=Vpp(G+'/patch.vpp_pc')
CL=[int(t) for t in v.read(v.find('charlist_CH','txt')).decode().split() if t.lstrip('-').isdigit()]

def parse(raw):
    magic,ver,buckets,count=struct.unpack_from('<IHHI',raw,0)
    oa=16          # 桶表从 16 开始
    recs=[]
    for i in range(count):
        o,flag=struct.unpack_from('<II',raw,oa+i*8)
        if o>=len(raw)-4: continue
        recs.append((o,flag))
    return ver,buckets,count,recs

def dec_body(raw,o):
    # 尝试: 记录体 = <u16 hash><u16 pad>? 或直接 UTF-16BE
    # dump 前 48 字节看结构
    return raw[o:o+48]

raw=open(G+r'\Mods\JUICED - Strings\juiced_CH.le_strings','rb').read()
ver,bk,cnt,recs=parse(raw)
print("juiced_CH ver=%d buckets=%d count=%d" % (ver,bk,cnt))
seen=set()
for o,f in recs:
    if o in seen: continue
    seen.add(o)
    body=dec_body(raw,o)
    print("\n off=0x%03X flag=%d" % (o,f))
    print("   raw:", body.hex(' ').upper())
    # 尝试两种: (a) BE 文本直接开始 (b) hash(2)+pad(2)+BE
    for skip in (0,2,4):
        units=[]
        p=o+skip
        while p+1<len(raw):
            u=struct.unpack_from('>H',raw,p)[0]; p+=2
            if u==0: break
            units.append(u)
        out=[]
        for u in units:
            if u<0x100: out.append(chr(u))
            else:
                i=u-32
                out.append(chr(CL[i]) if 0<=i<len(CL) else '.')
        print("   skip=%d d=32: %s" % (skip, "".join(out)[:70]))
