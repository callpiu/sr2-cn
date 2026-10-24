# -*- coding: utf-8 -*-
"""取「迷雾巷」记录 ID，去 static_US 查同 ID 的英文原文（从而知道这一带的区域名怎么翻）"""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
b=open(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc','rb').read()

# 「迷雾巷」记录起点
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

for at in (0x01C2D86A, 0x02E3AE94):
    p=at
    while p>=2 and struct.unpack_from('>H',b,p-2)[0]!=0: p-=2
    print('迷雾巷记录起点 0x%08X'%p)
    print('  前 8 字节: %s'%b[p-8:p].hex(' '))
    id1,id2=struct.unpack_from('<HH',b,p-4)
    print('  候选 ID = %04X / %04X'%(id1,id2))
print()

# 用桶结构找记录：更可靠 —— 直接遍历 static_CH blob 全部记录，收集 ID
v=Vpp(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc')
CH=bytes(v.read(v.find('static_CH','le_strings')))
print('static_CH blob =',len(CH))
buckets=struct.unpack_from('<H',CH,8)[0]
count=struct.unpack_from('<I',CH,12)[0]
print('  buckets=%d count=%d'%(buckets,count))
BT=16; PTR=BT+buckets*8
print('  blob 内记录起点范围可用, 单字「城」id 查询:')
# 找 CH blob 内 base（blob 在 vpp 里的绝对位置）
print()

# 直接在 CH blob 里搜「迷雾巷」的 slot 序列
pat=struct.pack('>3H',S('迷'),S('雾'),S('巷'))
i=CH.find(pat)
print('「迷雾巷」在 static_CH blob 内偏移 =',hex(i) if i>=0 else 'NOT FOUND')
if i>=0:
    print('  该处 blob 绝对偏移 = 0x%08X'%(0x1C2D86A))  # 已知一处
    print('  前 8 字节: %s'%CH[i-8:i].hex(' '))
    id1,id2=struct.unpack_from('<HH',CH,i-4)
    print('  ID = %04X / %04X'%(id1,id2))
    # 英文表同 ID
    v2=Vpp(r"F:\sr2-cn\_ref_第三方补丁\原始基准\patch_第三方原版.vpp_pc")
    US=bytes(v2.read(v2.find('static_US','le_strings')))
    print()
    print('  在 static_US 内搜同 slot 字节（英文表是 u16LE 码点）— 改搜「雾巷」英文线索:')
    for kw in ('Misty','Mist ','Foggy','Alley','Lane'):
        p=kw.encode('utf-16-le')
        c=US.count(p)
        if c: print('    %-8s -> %d'%(kw,c))