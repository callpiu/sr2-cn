# -*- coding: utf-8 -*-
"""中英表记录序号对齐：查中文「城区」「迷雾巷」对应的英文原文
   CH 表格式：header12(magic/ver/buckets u16/count u32) + 桶表 buckets*(count u32, addr u32)
              + 指针数组 count*u32(记录绝对偏移) + 记录 [slots...][0000]
"""
import sys, struct, os
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
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else ''

def parse_ch(blob, is_slot):
    """返回记录文本列表（按桶展开顺序）"""
    magic=blob[0:4]
    buckets=struct.unpack_from('<H',blob,8)[0]
    count=struct.unpack_from('<I',blob,12)[0]
    BT=16
    PTR=BT+buckets*8
    out=[]
    seen=set()
    for bi in range(buckets):
        o=BT+bi*8
        n,addr=struct.unpack_from('<II',blob,o)
        for k in range(n):
            idx=addr+k
            if idx>=count: continue
            off=struct.unpack_from('<I',blob,PTR+idx*4)[0]
            if off in seen: continue
            seen.add(off)
            q=off; o2=[]
            while q+2<=len(blob):
                w=struct.unpack_from('>H',blob,q)[0]
                if w==0: break
                o2.append(w); q+=2
            if is_slot:
                t=''.join(dec(x) for x in o2)
            else:
                t=''.join(chr(x) for x in o2)
            out.append((idx,off,t))
    out.sort()
    return buckets,count,out

# CH
zh=open(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc','rb').read()
v=Vpp(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc')
e=v.find('static_CH','le_strings')
CH=bytes(v.read(e))
print('static_CH blob size',len(CH))
bk,ct,CHR=parse_ch(CH,True)
print('  buckets=%d count=%d 解析记录=%d'%(bk,ct,len(CHR)))

# US
v2=Vpp(r"F:\sr2-cn\_ref_第三方补丁\原始基准\patch_第三方原版.vpp_pc")
US=bytes(v2.read(v2.find('static_US','le_strings')))
print('static_US blob size',len(US))
bk2,ct2,USR=parse_ch(US,False)
print('  buckets=%d count=%d 解析记录=%d'%(bk2,ct2,len(USR)))

print()
targets=[t for i,o,t in CHR if '城区' in t or '迷雾巷' in t]
print('CH 中含「城区」或「迷雾巷」的记录 = %d'%len(targets))
for i,o,t in CHR:
    if '城区' in t or '迷雾巷' in t:
        en='<idx %d 无对应>'%i
        for j,o2,t2 in USR:
            if j==i: en=t2; break
        print('  [%05d] CN=%-42s EN=%s'%(i,t[:40].replace('\n',''),en[:80]))