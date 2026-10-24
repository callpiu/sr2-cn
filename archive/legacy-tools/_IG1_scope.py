# -*- coding: utf-8 -*-
# 只读穷举: 方案B 作用域调研 (单脚本)
import os, sys, re, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
P = os.path.join(G, "patch.vpp_pc")

def cl_from(buf):
    return [int(x) for x in re.findall(rb'\d+', buf)]

def parse(data):
    ver, buckets, count = struct.unpack_from("<HHI", data, 4)
    off = 12 + buckets * 8
    n = len(data)
    if off + count * 4 > n: return [], count
    ptrs = [struct.unpack_from("<I", data, off + i*4)[0] for i in range(count)]
    out = []
    for p in ptrs:
        if p == 0 or p >= n - 4: continue
        id1, id2 = struct.unpack_from("<HH", data, p)
        q = p + 4; slots = []
        while q + 2 <= n:
            w = struct.unpack_from(">H", data, q)[0]
            if w == 0: break
            slots.append(w); q += 2
        out.append(((id1 << 16) | id2, slots))
    return out, count

v = Vpp(P)
LC = cl_from(v.read(v.find("charlist_CH", "txt")))
print("charlist_CH len =", len(LC))
print("LC[371]=", chr(LC[371]), " LC[1836]=", chr(LC[1836]))

tabs = {}
for nm in ["static_CH", "static_US", "voice_script_CH", "voice_script_US"]:
    e = v.find(nm, "le_strings")
    d = v.read(e)
    rs, cnt = parse(d)
    tabs[nm] = {h: s for h, s in rs}
    n_cjk = 0; mx = 0
    for h, s in rs:
        for w in s:
            if w > mx: mx = w
        t = "".join(chr(LC[w-0x20]) if 0x20 <= w-0x20 < len(LC) else '?' for w in s)
        if any('\u4e00' <= c <= '\u9fff' for c in t): n_cjk += 1
    print("%-18s header_count=%-6d parsed=%-6d  CJK记录=%-6d  最大槽位=0x%x(%d)  越界(>%d)=%d"
          % (nm, cnt, len(rs), n_cjk, mx, mx, len(LC), sum(1 for _, s in rs for w in s if w-0x20 >= len(LC))))

ch = set(tabs["static_CH"]); us = set(tabs["static_US"])
print("\nCH=%d  US=%d  CH&US=%d  CH-US=%d  US-CH=%d" %
      (len(ch), len(us), len(ch & us), len(ch - us), len(us - ch)))

print("\n=== 目标记录在哪些表里 ===")
for tgt in [0x84F287ED, 0x10AF1E62, 0xEC2D9F07, 0xE52F931A]:
    row = []
    for nm, tb in tabs.items():
        row.append("%s:%s" % (nm, "Y(%d槽)" % len(tb[tgt]) if tgt in tb else "N"))
    print("  %08X  %s" % (tgt, "  ".join(row)))

print("\n=== CH 表独有记录(不在US)中, 含CJK的有多少 ===")
only = []
for h in sorted(ch - us):
    s = tabs["static_CH"][h]
    t = "".join(chr(LC[w-0x20]) if 0x20 <= w-0x20 < len(LC) else '?' for w in s)
    if any('\u4e00' <= c <= '\u9fff' for c in t): only.append((h, t))
print("  CH独有且含CJK =", len(only))
for h, t in only[:15]:
    print("    %08X  %s" % (h, t[:60]))
