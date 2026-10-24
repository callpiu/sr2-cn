# -*- coding: utf-8 -*-
"""核验 0x019F0ED8 单字「城」记录：它在哪个表、桶结构里的 ID、对应英文原文"""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
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
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else '?'
b=open(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc','rb').read()

AT=0x019F0ED8
print('目标 0x%08X  slot=0x%04X (%r)'%(AT,struct.unpack_from('>H',b,AT)[0],
      dec(struct.unpack_from('>H',b,AT)[0])))
print('终止符 @0x%08X = 0x%04X'%(AT+2,struct.unpack_from('>H',b,AT+2)[0]))
print()
# 它属于哪个 VPP 条目？用各条目 body/size 定位
v=Vpp(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc')
ents=v.entries()
data_start=v.data_start
print('data_start = 0x%08X'%data_start)
hit=[]
for e in ents:
    s=data_start+e['body']; en=s+e['size']
    if s<=AT<en:
        hit.append(e)
        print('★ 落在条目: %s.%s  body=[0x%08X,0x%08X)'%(e['name'],e['ext'],s,en))
        print('   相对 blob 偏移 = 0x%X  (size=%d)'%(AT-s,e['size']))
if not hit:
    print('不在任何条目 body 范围？可能落在 names/ext 索引区')
print()

# 用之前算出的 static_CH base 校验
base=0x01BCC1D2
print('static_CH base=0x%08X → 相对偏移 = 0x%X'%(base,AT-base))
print('  负数 ⇒ 不在 static_CH 内' if AT<base else '')
print()
# 相邻 slot 分析：0x019F0ED8 区域结构
print('=== 该记录前后 ±40 字节 slot 序列 ===')
for o in range(AT-40,AT+44,2):
    w=struct.unpack_from('>H',b,o)[0]
    d=dec(w) if 0x20<=w<0x20+len(CL) else ''
    mark=' <<<' if o==AT else ''
    print('  0x%08X 0x%04X %-3s%s'%(o,w,d,mark))