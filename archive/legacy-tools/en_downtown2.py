# -*- coding: utf-8 -*-
"""直接按 UTF-16LE 字节扫英文表，抽出含 Downtown 的完整记录"""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
v=Vpp(r"F:\sr2-cn\_ref_第三方补丁\原始基准\patch_第三方原版.vpp_pc")
d=bytes(v.read(v.find('static_US','le_strings')))

# 文本区：跳过桶索引区。做法 = 全表扫 ASCII 可打印 UTF-16LE 序列
# 记录以 0000 结尾，我们用「向前找最近 0000 边界」定位起点
def rec_start(b,i):
    p=i
    while p>=2 and b[p-2:p]!=b'\x00\x00': p-=2
    return p
def rec_text(b,i):
    p=rec_start(b,i); q=p; out=[]
    while q+2<=len(b):
        w=struct.unpack_from('<H',b,q)[0]
        if w==0: break
        out.append(w); q+=2
    return ''.join(chr(c) for c in out)

pats=[kw.encode('utf-16-le') for kw in ('Downtown','Outskirts','Stilwater','downtown')]
seen=set()
for p in pats:
    st=0
    while True:
        i=d.find(p,st)
        if i<0: break
        t=rec_text(d,i)
        t=t.replace('\x00','').encode('utf-8','replace').decode('utf-8')
        if t not in seen:
            seen.add(t)
            print('[%s] %s'%(p.decode(),t[:200]))
        st=i+1
print('---- 独立串 =',len(seen))