# -*- coding: utf-8 -*-
# 测试 f(i) 是否等于 LC[i] 在某个"其它顺序表"中的位置
import re, sys
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

def load(path, name):
    v = Vpp(path); e = v.find(name, "txt")
    buf = v.read(e)
    m = re.search(rb'count\s*=\s*(\d+)', buf)
    seg = buf[m.end():] if m else buf
    return [int(x) for x in re.findall(rb'\d+', seg)]

CN = r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc"
OF = r"F:\sr2-cn\pristine\patch.vpp_pc"
LC = load(CN, "charlist_CH")   # 汉化 2795
LO = load(OF, "charlist_CH")   # 官方 2838
print("LC", len(LC), "LO", len(LO))

# 观测: 正确索引 i -> 显示字索引 j (在 LC 中)
OBS = [(371,336),(1836,1784),(1035,410),(422,967),(332,362),
       (2667,2656),(2296,2268),(391,354),(1190,2342)]
# 附带正确字
NAME = {371:"你",1836:"的",1035:"弟",422:"兄",332:"们",2667:"需",2296:"要",391:"保",1190:"护"}
for i,j in OBS:
    print("  %s i=%4d (U+%04X) -> j=%4d (%s)  diff=%d" % (NAME[i], i, LC[i], j, chr(LC[j]), j-i))

def test(name, key):
    hit=0; rows=[]
    for i,j in OBS:
        cp = LC[i]
        v = key(cp)
        ok = (v==j)
        hit += ok
        rows.append((NAME[i], i, j, v, ok))
    print("\n[%s] hit=%d/%d" % (name, hit, len(OBS)))
    for n,i,j,v,ok in rows:
        print("   %s i=%4d exp=%4d got=%s %s" % (n,i,j,v,"OK" if ok else "-"))
    return hit

# 候选1: 该字在官方 charlist 中的位置
posLO = {}
for k,c in enumerate(LO): posLO.setdefault(c,k)
test("官方charlist中的位置", lambda cp: posLO.get(cp))

# 候选2: 该字在 LC 按码点排序后的秩
srt = sorted(LC); posSort = {c:k for k,c in enumerate(srt)}
test("LC按码点排序的秩", lambda cp: posSort.get(cp))

# 候选3: 该字在官方 charlist 按码点排序后的秩
srtO = sorted(LO); posSortO = {c:k for k,c in enumerate(srtO)}
test("LO按码点排序的秩", lambda cp: posSortO.get(cp))

# 候选4: 码点本身 - 0x20
test("码点-0x20", lambda cp: cp-0x20)

# 候选5: j = i - (i的某函数) —— 先看 diff 与码点的关系
print("\n=== diff vs codepoint ===")
for i,j in OBS:
    print("   cp=U+%04X=%5d  i=%4d j=%4d diff=%5d  j*? " % (LC[i], LC[i], i, j, j-i))
