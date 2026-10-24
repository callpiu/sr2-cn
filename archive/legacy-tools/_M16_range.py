# -*- coding: utf-8 -*-
"""检查 juiced_CH 的 slot 取值范围，判断它用的是哪张表。"""
import sys, struct
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v=Vpp(G+'/patch.vpp_pc')
tabs={}
for nm in ['charlist_CH','charlist_JP','charlist_CZ','charlist_SK','JPCharList']:
    tabs[nm]=[int(t) for t in v.read(v.find(nm,'txt')).decode().split() if t.lstrip('-').isdigit()]

raw=open(G+r'\Mods\JUICED - Strings\juiced_CH.le_strings','rb').read()
magic,ver,buckets,count=struct.unpack_from('<IHHI',raw,0)
tbase=16+buckets*8
offs=[struct.unpack_from('<I',raw,tbase+i*4)[0] for i in range(count) if struct.unpack_from('<I',raw,tbase+i*4)[0] < len(raw)]

allslots=[]
for o in offs:
    p=o+4
    while p+1<len(raw):
        u=struct.unpack_from('>H',raw,p)[0]; p+=2
        if u==0: break
        if u>=0x100: allslots.append(u)
print("juiced_CH 所有 slot 值: %s" % sorted(set(allslots)))
print("最大 slot = %d" % max(allslots))
print("最小 slot = %d" % min(allslots))
print()
print("=== 各表项数 ===")
for nm,t in tabs.items():
    print("  %-14s %d 项  -> slot(idx+32) 最大 = %d" % (nm, len(t), len(t)+31))
print()
print("=> 需要表项数 >= %d 才能容纳这些 slot" % (max(allslots)-31))
print()
# 用 charlist_JP / SK 试解
for nm,t in tabs.items():
    print("=== 用 %s 解 juiced_CH ===" % nm)
    for o in offs[:4]:
        p=o+4; out=[]
        while p+1<len(raw):
            u=struct.unpack_from('>H',raw,p)[0]; p+=2
            if u==0: break
            if u<0x100: out.append(chr(u))
            else:
                i=u-32
                out.append(chr(t[i]) if 0<=i<len(t) else '?')
        print("   ", "".join(out)[:70])
    print()
