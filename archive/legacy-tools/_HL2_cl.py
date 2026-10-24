# -*- coding: utf-8 -*-
# 修正 charlist 解析：先看原始格式，再做 9 组对照假设检验
import re, sys, os
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

def raw_cl(path, vppname):
    v = Vpp(path)
    e = v.find(vppname, "txt")
    if e is None:
        print("  !! not found", vppname); return None
    return v.read(e)

def parse_cl(buf):
    """返回 codepoint 列表；文件为十进制、换行分隔"""
    m = re.search(rb'count\s*=\s*(\d+)', buf)
    if m:
        start = m.end()
        nums = re.findall(rb'\d+', buf[start:])
        print("  has count= header, declared", m.group(1).decode(), "parsed", len(nums))
    else:
        nums = re.findall(rb'\d+', buf)
        print("  NO count= header, parsed", len(nums))
    return [int(x) for x in nums]

CN = r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc"
OF = r"F:\sr2-cn\pristine\patch.vpp_pc"

print("=== 汉化 patch charlist_CH.txt ===")
bc = raw_cl(CN, "charlist_CH")
print("  bytes", len(bc), "first64:", bc[:64])
LC = parse_cl(bc)

print("=== 官方 patch charlist_CH.txt ===")
bo = raw_cl(OF, "charlist_CH")
print("  bytes", len(bo), "first64:", bo[:64])
LO = parse_cl(bo)

print("  CN len", len(LC), " OF len", len(LO))
print("  CN[0:8] ", [hex(x) for x in LC[:8]])
print("  OF[0:8] ", [hex(x) for x in LO[:8]])

# 9 组对照: i = 正确字在【汉化 charlist】中的索引, want = 实际显示的字
PAIRS = [(371,"任"),(1836,"璨"),(1035,"偶"),(422,"巧"),(332,"位"),
         (2667,"雄"),(2296,"衡"),(391,"伪"),(1190,"该")]
# 正确字
RIGHT = ["你","的","弟","兄","们","需","要","你","的","保","护"]
# 正确字索引(来自历史日志)
RIDX  = [371,1836,1035,422,332,2667,2296,371,1836,391,1190]

print("\n=== 校验: 汉化 charlist[正确索引] 是否 == 正确字 ===")
for ch,i in zip(RIGHT,RIDX):
    got = chr(LC[i]) if i < len(LC) else "?"
    print("  i=%4d want=%s got=%s %s" % (i, ch, got, "OK" if got==ch else "MISS"))

print("\n=== 假设 H1: 官方charlist[正确索引] == 显示字 ? ===")
hit=0
for i,want in PAIRS:
    if i < len(LO):
        got = chr(LO[i])
        ok = (got==want)
        hit += ok
        print("  i=%4d want=%s  OF[i]=%s  %s" % (i, want, got, "HIT" if ok else "-"))
print("  H1 hit =", hit, "/", len(PAIRS))

print("\n=== 反推: 显示字在汉化charlist中的索引 j, 与 i 的关系 ===")
posCN = {}
for k,c in enumerate(LC): posCN.setdefault(c,k)
for i,want in PAIRS:
    j = posCN.get(ord(want))
    print("  i=%4d -> j=%s  diff=%s" % (i, j, (j-i) if j is not None else None))
