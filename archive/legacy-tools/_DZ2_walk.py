import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v=Vpp(os.path.join(G,"patch.vpp_pc")); x = v.read(v.find("static_CH","le_strings"))
n = struct.unpack_from('<I', x, 8)[0]
dirstart=12; dirend=dirstart+n*8
ents=[struct.unpack_from('<II', x, dirstart+i*8) for i in range(n)]
lens=[l for l,_ in ents]
print("n=%d dirend=%d filesize=%d  textbytes=%d" % (n,dirend,len(x),len(x)-dirend))
print("len stats: min=%d max=%d sum=%d sum*2=%d" % (min(lens),max(lens),sum(lens),sum(lens)*2))
from collections import Counter
print("len 分布前10:", Counter(lens).most_common(10))
# 有序 / 无序
ids=[i for _,i in ents]
print("id 单调递增:", all(ids[i]<ids[i+1] for i in range(len(ids)-1)))
print("前10 id:", [hex(i) for i in ids[:10]])
print("id 范围:", hex(min(ids)), hex(max(ids)))
# 试从 dirend+1 顺序走
def walk(start, order, unit):
    p=start; out=[]
    for k in order:
        l=lens[k]
        out.append((ents[k][1], p, l)); p += l*unit
    return out, p
for unit in (2,1):
    for start in (dirend, dirend+1):
        seg,p = walk(start, range(n), unit)
        print("unit=%d start=%d -> 终点 %d (文件 %d, 差 %d)" % (unit,start,p,len(x),len(x)-p))
