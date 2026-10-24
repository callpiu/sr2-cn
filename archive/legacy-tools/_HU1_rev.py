# -*- coding: utf-8 -*-
# 反查: 是否存在表 L 使 L[j] == 源字 (j = 显示字在汉化charlist中的索引)
import os, sys, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G  = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
OF = r"F:/sr2-cn/pristine/patch.vpp_pc"

def cl(buf):
    m = re.search(rb'count\s*=\s*(\d+)', buf)
    seg = buf[m.end():] if m else buf
    return [int(x) for x in re.findall(rb'\d+', seg)]

lists = {}
for tag, path in (("GAME", os.path.join(G,"patch.vpp_pc")), ("OFF", OF)):
    v = Vpp(path)
    for e in v.entries():
        if e['ext'].lower()=='txt' and ('charlist' in e['name'].lower() or 'jpchar' in e['name'].lower()):
            lists["%s/%s" % (tag, e['name'])] = cl(v.read(e))

# 也加入 common 的 vf3? 不。加入排序变体
import copy
extra = {}
for k, v in lists.items():
    extra[k + "|sorted"] = sorted(v)
    extra[k + "|rev"] = v[::-1]
lists.update(extra)

# (显示索引 j, 源字)
PAIRS = [(336,"你"),(1784,"的"),(410,"弟"),(967,"兄"),(362,"们"),
         (2656,"需"),(2268,"要"),(354,"保"),(2342,"护")]
print("=== 反查 L[j] == 源字 ===")
best=[]
for name, L in lists.items():
    hit=0; det=[]
    for j, want in PAIRS:
        got = chr(L[j]) if j < len(L) else None
        ok = (got==want); hit+=ok; det.append((j,want,got,ok))
    best.append((hit,name,det))
best.sort(reverse=True, key=lambda x:x[0])
for hit,name,det in best[:5]:
    print("\n [%s] hit=%d/9" % (name,hit))
    for j,want,got,ok in det:
        print("    j=%4d want=%s got=%s %s" % (j,want,got,"HIT" if ok else "-"))

# 顺带检查汉化 charlist 是否严格递增
LC = lists["GAME/charlist_CH"]
bad = [i for i in range(1,len(LC)) if LC[i] <= LC[i-1]]
print("\n汉化 charlist 非递增位置数 =", len(bad), bad[:20])
print("总长", len(LC), "唯一值", len(set(LC)))
