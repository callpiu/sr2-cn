# -*- coding: utf-8 -*-
"""T 映射结构分析：
1. 9 个乱码输出码点是否在 charlist_CH(patch 字表) 中？
2. common 锚点(索引,码点) 与 patch 索引的偏移规律
3. 若输出来自 common 数组，用偏移函数插值求 out 的 common 索引，找 in_idx -> out_idx 规律
"""
import json, bisect, sys

CL = json.load(open(r"F:\sr2-cn\_day_2026-10-07\04_规则与数据\_expected_charlist.json"))
print("charlist_CH 条目数 =", len(CL), " 首项=", CL[0], " 末项=", CL[-1])
assert CL == sorted(CL), "charlist 非升序！"
cp2idx = {cp: i for i, cp in enumerate(CL)}

def c(ch):
    return ord(ch)

# ---- 9 个已实证映射：charlist 索引 -> 屏幕显示码点 ----
MAP = [
    ("们", 332, 0x4F4D),   # 位
    ("你", 371, 0x4EFB),   # 任
    ("保", 391, 0x4F2A),   # 伪
    ("兄", 422, 0x5DE7),   # 巧
    ("弟", 1035, 0x5076),  # 偶
    ("护", 1190, 0x8BE5),  # 该
    ("的", 1836, 0x74A8),  # 璨
    ("要", 2296, 0x8861),  # 衡
    ("需", 2667, 0x96C4),  # 雄
]
# 自校验：输入索引的码点应与字符一致
for ch, idx, out in MAP:
    ok = "OK " if CL[idx] == c(ch) else "MISMATCH"
    print(f"  [{ok}] CL[{idx}]=U+{CL[idx]:04X}({chr(CL[idx])}) 期望={ch}")

print("\n=== 1. 乱码输出码点是否在 charlist_CH ===")
for ch, idx, out in MAP:
    if out in cp2idx:
        print(f"  {ch}(idx{idx}) -> U+{out:04X}({chr(out)})  在 charlist_CH 中, 索引 {cp2idx[out]}")
    else:
        print(f"  {ch}(idx{idx}) -> U+{out:04X}({chr(out)})  *** 不在 charlist_CH ***  => 必来自 common 数组")

# ---- common 渲染锚点（h2b_test.py 实测）----
ANCH = [(332, 0x4F5C), (359, 0x5012), (371, 0x5065), (390, 0x50CF),
        (1003, 0x5FD7), (1158, 0x633D), (1804, 0x76EF), (2264, 0x91CC), (2635, 0x9664)]
print("\n=== 2. common 锚点 vs patch 索引 ===")
rows = []
for ci, cp in ANCH:
    pi = cp2idx.get(cp)
    if pi is None:
        print(f"  common[{ci}] = U+{cp:04X}({chr(cp)})  **不在 charlist_CH**")
        rows.append((ci, cp, None))
    else:
        print(f"  common[{ci}] = U+{cp:04X}({chr(cp)})  patch_idx={pi}  偏移 common-patch = {ci-pi}")
        rows.append((ci, cp, pi))

print("\n=== 3. 用偏移函数估计各输出码点的 common 索引 ===")
# 用有 patch 对应点的锚点做线性插值（按码点）
pts = sorted([(cp, ci - pi) for ci, cp, pi in rows if pi is not None])
cps = [p[0] for p in pts]
offs = [p[1] for p in pts]
def est_common_idx(cp):
    j = bisect.bisect_left(cps, cp)
    if j == 0:
        return offs[0]
    if j >= len(cps):
        return offs[-1]
    # 线性插值
    c0, c1 = cps[j-1], cps[j]
    o0, o1 = offs[j-1], offs[j]
    if c1 == c0:
        return o0
    t = (cp - c0) / (c1 - c0)
    return o0 + t * (o1 - o0)

print("  (偏移 = common_idx - patch_idx, 按码点分段线性)")
for ch, idx, out in MAP:
    if out in cp2idx:
        pi = cp2idx[out]
        d = est_common_idx(out)
        print(f"  {ch}: in_idx={idx} -> U+{out:04X} patch_idx={pi}  估计 common_idx≈{pi+d:.0f}  (in_idx-common_idx = {idx-(pi+d):+.0f})")
    else:
        d = est_common_idx(out)
        print(f"  {ch}: in_idx={idx} -> U+{out:04X} 不在charlist, 估计 common_idx≈? (仅可估偏移 {d:.0f})")

print("\n=== 4. 假设检验: in_idx 与 patch_idx(out) 的差是否恒定 ===")
diffs = []
for ch, idx, out in MAP:
    if out in cp2idx:
        diffs.append((ch, idx, cp2idx[out], idx - cp2idx[out]))
for ch, i, o, d in diffs:
    print(f"  {ch}: {i} - {o} = {d:+d}")
if diffs:
    ds = [d for _, _, _, d in diffs]
    print(f"  => 差值集合 {sorted(set(ds))}  极差 {max(ds)-min(ds)}")
