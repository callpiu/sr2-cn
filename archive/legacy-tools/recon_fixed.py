# -*- coding: utf-8 -*-
"""勘察别人修复后的 patch.vpp_pc (ea23ead4)：
   1) 字表是否还是旧的那份  2) 3rdS 记录现在在哪  3) 「三街圣徒」slot 是否变化"""
import sys, struct, hashlib
sys.stdout.reconfigure(encoding='utf-8')
NEW=r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
OLDBAK=r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc.v535_before_rec1.bak'

def load_cl(p):
    xs=[]
    for l in open(p,encoding='utf-8'):
        l=l.strip()
        if not l or l.startswith('//') or l.startswith('#'): continue
        xs.append(int(l))
    return xs
CL_OLD=load_cl(r'F:\sr2-cn\_juice_fix\charlist_CH.txt')
IDX_OLD={cp:i for i,cp in enumerate(CL_OLD)}

new=open(NEW,'rb').read()
old=open(OLDBAK,'rb').read()
print('新(修复后) %d 字节  md5=%s'%(len(new),hashlib.md5(new).hexdigest()))
print('旧(v534)   %d 字节  md5=%s'%(len(old),hashlib.md5(old).hexdigest()))
print('大小差 %+d 字节'%(len(new)-len(old)))
print()

def dec(s,CL): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else '<%04X>'%s
def rec_start(buf,i):
    p=i
    while p>=2:
        if struct.unpack_from('>H',buf,p-2)[0]==0: break
        p-=2
    return p
def tx(buf,t):
    q=t;o=[]
    while q+2<=len(buf):
        v=struct.unpack_from('>H',buf,q)[0]
        if v==0: break
        o.append(v); q+=2
    return o

# ---------- 1) 字表是否变 ----------
print('=== 1) 字表变化检测 ===')
# charlist_CH 在 patch 里应有原始 slot 序列（旧字表）
pat_old=b''.join(struct.pack('>H',i+0x20) for i in range(len(CL_OLD)))
print('旧字表 slot 升序序列前20 = %s'%pat_old[:40].hex())
# 检查 ASCII 区自检串 0x20..0x7E 是否仍是新表开头
asc=b''.join(struct.pack('>H',c) for c in range(0x20,0x50))
print('ASCII slot 序列在 新/旧 中命中: %d / %d'%(new.count(asc),old.count(asc)))
print()

# ---------- 2) 3rdS 现在在哪 ----------
print('=== 2) 3rdS 记录在新文件中的位置 ===')
p3=b''.join(struct.pack('>H',ord(c)) for c in '3rdS')
hits=[];st=0
while True:
    i=new.find(p3,st)
    if i<0: break
    hits.append(i); st=i+1
print('命中 %d 处'%len(hits))
for i in hits:
    p=rec_start(new,i)
    s=tx(new,p)
    pre=struct.unpack_from('>2H',new,p-4) if p>=4 else (0,0)
    tail=struct.unpack_from('>H',new,i+8)[0]
    print('  文本@0x%08X  起点=0x%08X  前缀=%04X %04X  尾部=0x%04X'%(i,p,pre[0],pre[1],tail))
    print('     slot=%s'%' '.join('%04X'%x for x in s))
    print('     ASCII=%r'%''.join(chr(x) for x in s))
print()

# ---------- 3) 「三街圣徒」用旧字表算的 slot 在新文件里是否是「三街圣徒」 ----------
print('=== 3) 新文件里「三街圣徒」的实际 slot（靠解码反查字表）===')
# 找新文件里的中文记录，用旧字表解码，看是否合理
targets=['需要你的保护','华丽座驾']
for t in targets:
    pat=b''.join(struct.pack('>H',IDX_OLD[ord(c)]+0x20) for c in t)
    c=new.count(pat)
    co=old.count(pat)
    print('  %-8r 旧字表slot序列命中: 新=%d  旧=%d'%(t,c,co))
print()

print('=== 4) 关键：别人修复后，字表索引是否还一致？===')
print('  若「新」和「旧」对同一 slot 解码出同一个字 ⇒ 字表未变，可沿用旧 slot')
for ch in '三街圣徒':
    i=IDX_OLD[ord(ch)]
    s=i+0x20
    # 在新文件里找单字 slot 出现在中文记录中的次数（抽样）
    print('   %s idx=%-5d slot=0x%04X'%(ch,i,s))
print()
print('  用旧 slot 序列搜「三街圣徒」在新文件中的命中数（判断字表是否仍对得上）：')
pat=b''.join(struct.pack('>H',IDX_OLD[ord(c)]+0x20) for c in '三街圣徒')
print('   新=%d  旧=%d'%(new.count(pat),old.count(pat)))