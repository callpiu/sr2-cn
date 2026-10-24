# -*- coding: utf-8 -*-
"""全局扫描：所有 CH 相关 le_strings，逐条解码，报告 slot 越界/异常记录数。
以及找出含"弟兄""保护"字样的所有记录及所在文件。
"""
import sys, struct, os
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v=Vpp(G+'/patch.vpp_pc')
CLraw=[int(t) for t in v.read(v.find('charlist_CH','txt')).decode().split() if t.lstrip('-').isdigit()]
print("charlist_CH 项数 =", len(CLraw))
N=len(CLraw)

def parse(raw):
    if len(raw)<16: return None
    magic,ver,buckets,count=struct.unpack_from('<IHHI',raw,0)
    if magic!=0xA84C7F73: return None
    tbase=16+buckets*8
    if tbase+count*4 > len(raw): return None
    offs=[struct.unpack_from('<I',raw,tbase+i*4)[0] for i in range(count)]
    return ver,buckets,count,offs

def scan(name, raw):
    r=parse(raw)
    if not r: 
        print("  %-30s 解析失败(magic=0x%08X)" % (name, struct.unpack_from('<I',raw,0)[0] if len(raw)>=4 else 0))
        return
    ver,buckets,count,offs=r
    bad=0; good=0; maxslot=0
    for o in offs:
        if not (0<o<len(raw)-4): continue
        p=o+4; units=[]
        while p+1<len(raw):
            u=struct.unpack_from('>H',raw,p)[0]; p+=2
            if u==0: break
            units.append(u)
        for u in units:
            if u>=0x100:
                maxslot=max(maxslot,u)
                if u-32>=N: bad+=1
                else: good+=1
    print("  %-30s ver=%d buckets=%d count=%-6d 有效slot=%-6d 越界slot=%-5d maxslot=%d" % (
        name,ver,buckets,count,good,bad,maxslot))

print("\n=== patch.vpp_pc ===")
for e in v.entries():
    n=e['name']+'.'+e['ext']
    if 'le_strings' in n.lower() and ('_CH' in n or '_ch' in n):
        scan(n, v.read(v.find(e['name'],e['ext'])))

print("\n=== Mods/JUICED - Strings (loose) ===")
SD=G+r'\Mods\JUICED - Strings'
for fn in sorted(os.listdir(SD)):
    if not fn.endswith('.le_strings'): continue
    if '_CH' not in fn and '_ch' not in fn: continue
    scan(fn, open(os.path.join(SD,fn),'rb').read())
