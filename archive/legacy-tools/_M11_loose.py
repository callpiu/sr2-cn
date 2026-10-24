# -*- coding: utf-8 -*-
"""检查 Mods/JUICED - Strings 下的 loose le_strings 内容，
以及它们是否会覆盖 patch.vpp_pc 里的 voice_script_CH / static_CH。"""
import sys, struct, os
sys.path.insert(0,'F:/sr2-cn')
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
SD=G+r'\Mods\JUICED - Strings'
from sr2lib import Vpp
v=Vpp(G+'/patch.vpp_pc')
txt=v.read(v.find('charlist_CH','txt')).decode()
CL=[int(t) for t in txt.split() if t.lstrip('-').isdigit()]

def recs(raw):
    magic,ver,buckets,count=struct.unpack_from('<IHHI',raw,0)
    oa=16+buckets*8
    d={}
    for i in range(count):
        o=struct.unpack_from('<I',raw,oa+i*4)[0]
        if not(0<=o<len(raw)-4):continue
        h=struct.unpack_from('<H',raw,o)[0]
        p=o+4; us=[]
        while p+1<len(raw):
            u=struct.unpack_from('>H',raw,p)[0]; p+=2
            if u==0:break
            us.append(u)
        d.setdefault(h,us)
    return ver,buckets,count,d

def dec(units):
    out=[]
    for u in units:
        if u<0x100: out.append(chr(u))
        else:
            i=u-32
            out.append(chr(CL[i]) if 0<=i<len(CL) else '?')
    return ''.join(out)

for fn in os.listdir(SD):
    if not fn.endswith('.le_strings'): continue
    p=os.path.join(SD,fn)
    raw=open(p,'rb').read()
    try:
        ver,buckets,count,d=recs(raw)
    except Exception as e:
        print("%-28s ERR %s" % (fn,e)); continue
    print("=== %s (%d bytes) ver=%d buckets=%d count=%d ===" % (fn,len(raw),ver,buckets,count))
    for h in list(d.keys())[:8]:
        print("     h=%04X  %s" % (h, dec(d[h])[:70]))
    print()
