# -*- coding: utf-8 -*-
import sys, struct
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from _vpp import Vpp
gv=Vpp(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc')
def pc(buf):
    out=[]
    for ln in buf.decode('latin-1').splitlines():
        s=ln.strip()
        if not s or s.startswith('//') or s.startswith('count'): continue
        try: out.append(int(s))
        except: pass
    return out
cl=pc(gv.read(gv.find('charlist_CH')))
inv={}
for i,c in enumerate(cl): inv.setdefault(c,i)

s1_src = '你的弟兄们需要你的保护'
s1_out = '任璨偶巧位雄衡任璨伪该'
s2_src = '你的弟兄们要出去谈几笔生意，保护他们免遭袭击'
s2_out = '任璨偶巧位校衡勾远藐乱携伪该亡位通像匪冰挺拮'
slots1 = [403,1868,1067,454,364,2699,2328,403,1868,423,1222]
slots2 = [403,1868,1067,454,364,2328,510,613,2389,502,1995,1824,1159,2822,423,1222,356,364,460,2563,2312,511]

def analyze(name, src, out, slots):
    print('===', name, 'len src', len(src), 'len out', len(out))
    print('%-4s %-6s %-6s %-6s %-6s'%('i','src','slot','slot-32','outidx'))
    for i,(s,sl,o) in enumerate(zip(src, slots, out)):
        si = inv.get(ord(s), -1)
        oi = inv.get(ord(o), -1)
        print('%-4d %-6s %-6d %-6d %-6d'%(i+1, s, sl, sl-32, oi))
analyze('S1', s1_src, s1_out, slots1)
print()
analyze('S2', s2_src, s2_out, slots2)
print()
print('检查: outidx 是否 = slot-32 减去某个只依赖 slot 的值')
