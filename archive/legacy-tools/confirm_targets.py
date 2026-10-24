# -*- coding: utf-8 -*-
"""确认 4 条目标条目的英文原文（static_US 同 resID），并核对
   等长英文替换方案：字符数必须等于原 slot 数。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
import sr2lib
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = sr2lib.Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(x) for x in v.read(v.find("charlist_CH")).decode("utf-8").split("\n")
       if x.strip().isdigit()]
N = len(cps)


def scan(blob):
    bk = struct.unpack_from("<I", blob, 8)[0]
    ct = struct.unpack_from("<I", blob, 12)[0]
    o, e2, out = 16 + bk * 8 + ct * 4 + 4, len(blob), []
    while o < e2 - 1:
        st = o; sl = []
        while True:
            if o >= e2:
                return out
            s = struct.unpack_from(">H", blob, o)[0]; o += 2
            if s == 0:
                break
            sl.append(s)
        if sl:
            out.append((st, sl))
    return out


def dec(sl):
    return "".join(chr(cps[s - 0x20]) if 0 <= s - 0x20 < N
                   else ("\n" if s == 10 else "<%d>" % s) for s in sl)


TARGETS = [(52696, 9602), (7228, 43019), (14679, 63447), (13594, 28212)]

for tbl, skip in (("static_CH", 0), ("static_US", 2)):
    blob = v.read(v.find(tbl))
    base = 16 + struct.unpack_from("<I", blob, 8)[0] * 8 \
        + struct.unpack_from("<I", blob, 12)[0] * 4 + 4
    idx = {}
    for st, sl in scan(blob):
        if len(sl) >= 2:
            # US 表需跳过 resID 后的 2 字节
            idx.setdefault(tuple(sl[:2]), (st, sl[2 + skip // 2:]))
    print("=== %s（skip=%d）===" % (tbl, skip))
    for t in TARGETS:
        hit = idx.get(t)
        if hit:
            st, body = hit
            print("   %-18s @%-8d %r  slots=%s"
                  % (str(t), st, dec(body), body))
        else:
            print("   %-18s 未找到" % (str(t),))
    print()

print("=== 等长替换方案（长度必须严格相等）===")
PLAN = [
    ((52696, 9602),  "指定辩护律师", 6, "指定律师",  4, "6 slot 只能放 4 字+2字"),
    ((7228, 43019),  "指定辩护律师 ", 7, "指定律师  ", 7, "含尾空格"),
    ((14679, 63447), "三王", 2, "3K",  2, "2 slot"),
    ((13594, 28212), "三王", 2, "3K",  2, "2 slot"),
]
for tid, cur, ln, new, nlen, note in PLAN:
    flag = "OK" if ln == nlen else "长度不符!"
    print("  %-18s %-14r %d slot -> %-12r %d slot  %s  (%s)"
          % (str(tid), cur, ln, new, nlen, flag, note))

print("\n所有候选字符是否在字表内：")
for ch in "指定律师3K ":
    print("   %r U+%04X -> %s" % (ch, ord(ch),
          "OK slot=%d" % (cps.index(ord(ch)) + 0x20)
          if ord(ch) in cps else "★不在字表★"))