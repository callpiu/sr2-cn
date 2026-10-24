# -*- coding: utf-8 -*-
"""empirical 定位 common vf3 的 U/V 数组偏移。

判据：U 数组应是大批落在 [0,2047] 的 u32，且行内等差（~31 或 ~30）、每 66 个归零；
V 数组应是 66 个一组常值、组间跳变。扫所有 4 字节对齐偏移找最佳。
"""
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
import sr2lib as S

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

vpc = S.Vpp(os.path.join(G, "common.vpp_pc"))
ec = None
for e in vpc.entries():
    if e["name"].lower() == "fnt_chinese" and e["ext"].lower() == "vf3_pc":
        ec = e; break
buf = bytes(vpc.read(ec))
N = struct.unpack_from("<I", buf, 8)[0]
print("[common] vf3 %d 字节, count@8=%d, 头16字节=%s" % (len(buf), N, buf[:16].hex(" ")))
print("  184+N*16+4 = %d ; 208+N*16 = %d ; 文件长-2*4*N = %d"
      % (184 + N * 16 + 4, 208 + N * 16, len(buf) - 8 * N))

best = []
for O in range(0, len(buf) - 8 * 100, 4):
    vals = struct.unpack_from("<100I", buf, O)
    if max(vals) > 2047 or min(vals) < 0:
        continue
    # U 状：多数连续差在 28..34
    du = [b - a for a, b in zip(vals, vals[1:])]
    good = sum(1 for d in du if 28 <= d <= 34)
    if good >= 60:
        best.append(("U", O, good, vals[:8]))
    # V 状：连续相同居多
    same = sum(1 for a, b in zip(vals, vals[1:]) if a == b)
    if same >= 60:
        best.append(("V", O, same, vals[:8]))

print("\n候选数组偏移（前 20）：")
seen = set()
for kind, O, sc, head in best[:40]:
    key = (kind, O)
    if key in seen:
        continue
    seen.add(key)
    print("  %s @0x%X (0x%X)  得分%d  头8项=%s" % (kind, O, O, sc, head))

# 用最佳候选验证网格结构
print("\n=== 验证：取 U 候选，检查行结构 ===")
for kind, O, sc, head in best:
    if kind != "U":
        continue
    vals = struct.unpack_from("<%dI" % N, buf, O) if O + 4 * N <= len(buf) else None
    if vals is None:
        continue
    # 找换行点（值突然变小）
    rows = []
    cur = [vals[0]]
    for a, b in zip(vals, vals[1:]):
        if b < a:
            rows.append(cur); cur = []
        cur.append(b)
    rows.append(cur)
    lens = [len(r) for r in rows[:6]]
    print("  U@0x%X: 行长度前6=%s, 首行头=%s" % (O, lens, vals[:6]))
    if lens and lens[0] >= 60:
        print("  ★ 采用 U@0x%X" % O)
        break
