# -*- coding: utf-8 -*-
# 修复方案评估：统计 们/护 受益 与 位/该 副作用
# 结论前提：位、该 显示正常 => 第357格是「位」的正统落点，第2337格是「该」的
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
cn = Vpp(CN)
f = Font(CN)
B = [chr(c) for c in f.charlist]
bidx = {c: i for i, c in enumerate(B)}
OFF = 5


def load(name):
    d = cn.read(cn.find(name, "le_strings"))
    buckets, = struct.unpack_from("<H", d, 6)
    count, = struct.unpack_from("<I", d, 8)
    ptrs = struct.unpack_from("<%dI" % count, d, 12 + buckets * 8)
    return d, count, ptrs


def rec(d, p):
    id1, id2 = struct.unpack_from("<HH", d, p)
    q = p + 4
    out = []
    while True:
        s, = struct.unpack_from(">H", d, q)
        q += 2
        if s == 0:
            break
        k = s - 32
        out.append(B[k] if 0 <= k < len(B) else "{%d}" % s)
    return id1, id2, "".join(out)


# 收集所有文本（按来源分类：voice_script=对白, static=UI/提示, platform=平台）
texts = {"voice_script_CH": [], "static_CH": [], "platform_pc_CH": []}
for name in texts:
    d, count, ptrs = load(name)
    for i in range(count):
        p = ptrs[i]
        if p + 6 > len(d):
            continue
        try:
            a, b_, t = rec(d, p)
        except Exception:
            continue
        texts[name].append((a, b_, t))

print("=== 四字出现次数（按来源）===")
print("%-6s %-14s %-12s %-12s %s" % ("字", "voice_script", "static", "platform", "合计"))
for ch in "们护位该":
    row = [sum(t.count(ch) for _, _, t in texts[n]) for n in texts]
    print("%-6s %-14d %-12d %-12d %d" % (ch, row[0], row[1], row[2], sum(row)))

print("\n=== 「保护」一词出现次数 ===")
for n in texts:
    c = sum(t.count("保护") for _, _, t in texts[n])
    print("  %-18s %d" % (n, c))

print("\n=== static_CH 中含「位」的句子（UI/提示，改图集会顶坏）===")
n = 0
for a, b_, t in texts["static_CH"]:
    if "位" in t:
        print("  [%04X.%04X] %s" % (a, b_, t[:60]))
        n += 1
        if n >= 12:
            break

print("\n=== static_CH 中含「该」的句子 ===")
n = 0
for a, b_, t in texts["static_CH"]:
    if "该" in t:
        print("  [%04X.%04X] %s" % (a, b_, t[:60]))
        n += 1
        if n >= 12:
            break

# 关键：voice_script 里 们/护 的句子（对白，走字幕路径）
print("\n=== voice_script_CH 中含「们」的高频句型（前10）===")
n = 0
for a, b_, t in texts["voice_script_CH"]:
    if "们" in t and 4 <= len(t) <= 40:
        print("  [%04X.%04X] %s" % (a, b_, t[:56]))
        n += 1
        if n >= 10:
            break
