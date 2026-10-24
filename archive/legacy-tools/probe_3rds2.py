# -*- coding: utf-8 -*-
"""确认 3rdS / 3rd Street 1 / 3rd Street 2 是不是同一 hash 的多语种副本，
   以及当前中文表里这些条目是否本来就没汉化。"""
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
IDX={cp:i for i,cp in enumerate(CL)}
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else '<%04X>'%s
buf=open(PATCH,'rb').read()

def hash_of(off):
    return (struct.unpack_from('<H',buf,off-4)[0]<<16)|struct.unpack_from('<H',buf,off-2)[0]
def txt_at(tstart):
    q=tstart;out=[]
    while q+2<=len(buf):
        v=struct.unpack_from('>H',buf,q)[0]
        if v==0: break
        out.append(v); q+=2
    return out

# 注意：hash 看起来像 0xD00A0000 —— 说明我读错了偏移。
# 记录ID 是 [u16 LE][u16 LE] 存在文本前4字节；LE读 u32 得 hash。
# 但这里 hash 高位全是 0 => 说明"文本起点"往前4字节不是ID，而是我回退越界了。
# 正确做法：ID 应该是 [id1][id2] 各 u16 LE，hash=(id1<<16)|id2
# 0xD00A0000 拆成 u16 LE: id1=0x000A, id2=0x0000 -> hash=(0x000A<<16)|0x0000=0xA0000
# 更可能：这些是**德语表**里的条目（前面 grep 到大量德文）。
# 直接打印前后字节确认真实结构。
print('=== 原始字节 dump（"3rdS" 那条 @0x1C2E240）===')
for off in range(0x1C2E230,0x1C2E260,2):
    v=struct.unpack_from('>H',buf,off)[0]
    le=struct.unpack_from('<H',buf,off)[0]
    ch=chr(v) if 0x20<=v<0x7f else ''
    print('  0x%08X  BE=%04X  LE=%04X  %s'%(off,v,le,ch))
print()

print('=== 同hash 分组统计所有 "3rd Street*" 条目 ===')
from collections import defaultdict
groups=defaultdict(list)
for probe in ['3rd Street 1','3rd Street 2','3rd Street Saints','3rdS']:
    pb=b''.join(struct.pack('>H',ord(c)) for c in probe)
    st=0
    while True:
        i=buf.find(pb,st)
        if i<0: break
        p=i
        while p>=2:
            if struct.unpack_from('>H',buf,p-2)[0]==0: break
            p-=2
        slots=txt_at(p)
        groups[hash_of(p)].append((i,p,probe,''.join(dec(s) for s in slots),len(slots)))
        st=i+1
for h in sorted(groups):
    items=groups[h]
    print()
    print('hash 0x%08X  共 %d 条'%(h,len(items)))
    seen=set()
    for i,p,probe,t,L in items:
        if t in seen: continue
        seen.add(t)
        kind='ASCII(疑未汉化)' if all(ord(c)<128 for c in t.replace('<','')if c.isalnum() or True) and not any('\u4e00'<=c<='\u9fff' for c in t) else ''
        print('   @0x%X %2d字 %r  %s'%(p,L,t,kind))
print()

print('=== 结论性检查：中文表里"三街圣徒"104 处 vs 这些 ASCII 条目 ===')
print('说明：若同一 hash 下同时存在中文版和ASCII版，说明 ASCII 版才是"漏翻"的那条，')
print('      需把 ASCII 版内容换成中文（或反之：游戏读的是 ASCII 那条）。')
pat=b''.join(struct.pack('>H',IDX[ord(c)]+0x20) for c in '三街圣徒')
st=0;zh_hashes=set()
while True:
    i=buf.find(pat,st)
    if i<0: break
    p=i
    while p>=2:
        if struct.unpack_from('>H',buf,p-2)[0]==0: break
        p-=2
    zh_hashes.add(hash_of(p))
    st=i+1
print('含「三街圣徒」的 hash 数 =',len(zh_hashes))
ascii_hashes=set(groups.keys())
print('含 ASCII "3rd Street*" 的 hash 数 =',len(ascii_hashes))
print('交集 =',['0x%08X'%h for h in (zh_hashes & ascii_hashes)])