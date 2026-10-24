# -*- coding: utf-8 -*-
# 测试 显示字 == 某张语言表[正确索引] / [正确索引+0x20]
import os, sys, re, struct, glob
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G  = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
OF = r"F:/sr2-cn/pristine/patch.vpp_pc"

def cl_from(buf):
    m = re.search(rb'count\s*=\s*(\d+)', buf)
    seg = buf[m.end():] if m else buf
    return [int(x) for x in re.findall(rb'\d+', seg)]

tables = {}
for tag, path in (("CN(游戏)", os.path.join(G,"patch.vpp_pc")), ("OFF(官方)", OF)):
    try: v = Vpp(path)
    except Exception as e: print("!!", tag, e); continue
    for e in v.entries():
        if e['ext'].lower() != 'txt': continue
        nm = e['name']
        if 'charlist' in nm.lower() or 'charlist' in nm.lower() or 'jpchar' in nm.lower():
            try: tables["%s/%s" % (tag, nm)] = cl_from(v.read(e))
            except Exception as ex: print("  !!", tag, nm, ex)

print("可用表:")
for k,v in tables.items(): print("   %-34s len=%d" % (k, len(v)))

# 观测 i -> 显示字
OBS = [(371,"任"),(1836,"璨"),(1035,"偶"),(422,"巧"),(332,"位"),
       (2667,"雄"),(2296,"衡"),(391,"伪"),(1190,"该")]

print("\n=== 测试各表: 表[i] 或 表[i+0x20] 是否 == 显示字 ===")
best = []
for name, T in tables.items():
    for off in (0, 0x20):
        hit = 0; detail = []
        for i, want in OBS:
            k = i + off
            got = chr(T[k]) if 0 <= k < len(T) else None
            ok = (got == want)
            hit += ok
            detail.append((i, want, got, ok))
        best.append((hit, name, off, detail))
best.sort(reverse=True, key=lambda x: x[0])
for hit, name, off, detail in best[:6]:
    print("\n  [%s] off=%d  hit=%d/9" % (name, off, hit))
    for i, want, got, ok in detail:
        print("     i=%4d want=%s got=%s %s" % (i, want, got, "HIT" if ok else "-"))

# 附: 显示字本身在 CN 表中的索引(用于后续比对)
print("\n=== 显示字在 CN 表中的索引 ===")
CNT = tables.get("CN(游戏)/charlist_CH") or tables.get("CN(游戏)/charlist_ch")
disp = "任璨偶巧位雄衡任璨伪该"
pos = {}
for k,c in enumerate(CNT): pos.setdefault(c,k)
print("  ", [(c, pos.get(ord(c))) for c in disp])
