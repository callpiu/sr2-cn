# -*- coding: utf-8 -*-
"""juiced_CH 越界 slot 详细分析 + 尝试用"完整CJK表"修复。
关键: maxslot=3491。若用 GBK 或 Unicode 顺序，3491 对应什么?
"""
import sys, struct
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v=Vpp(G+'/patch.vpp_pc')
CH=[int(t) for t in v.read(v.find('charlist_CH','txt')).decode().split() if t.lstrip('-').isdigit()]

raw=open(G+r'\Mods\JUICED - Strings\juiced_CH.le_strings','rb').read()
magic,ver,buckets,count=struct.unpack_from('<IHHI',raw,0)
tbase=16+buckets*8
offs=[struct.unpack_from('<I',raw,tbase+i*4)[0] for i in range(count)]
offs=[o for o in offs if o<len(raw)]

# 对照 CZ 同 hash 的记录（CZ 是完整正确的拉丁文）
rawc=open(G+r'\Mods\JUICED - Strings\juiced_CZ.le_strings','rb').read()
magicc,verc,bkc,cntc=struct.unpack_from('<IHHI',rawc,0)
tbc=16+bkc*8
offsc=[struct.unpack_from('<I',rawc,tbc+i*4)[0] for i in range(cntc)]
offsc=[o for o in offsc if o<len(rawc)]

def getrec(raw,o):
    h=struct.unpack_from('<H',raw,o)[0]
    p=o+4; units=[]
    while p+1<len(raw):
        u=struct.unpack_from('>H',raw,p)[0]; p+=2
        if u==0:break
        units.append(u)
    return h,units

def decCH(units):
    out=[]
    for u in units:
        if u<0x100: out.append(chr(u))
        else:
            i=u-32
            out.append(chr(CH[i]) if 0<=i<len(CH) else '<%d>'%u)
    return ''.join(out)

print("=== juiced_CH 逐条 (含越界) ===")
for o in offs:
    h,units=getrec(raw,o)
    print("h=%04X  %s" % (h, decCH(units)[:72]))

print("\n=== juiced_CZ 对照 ===")
for o in offsc:
    h,units=getrec(rawc,o)
    out=[]
    for u in units:
        out.append(chr(u) if u<0x100 else '<%d>'%u)
    print("h=%04X  %s" % (h, ''.join(out)[:72]))
