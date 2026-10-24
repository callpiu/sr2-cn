# -*- coding: utf-8 -*-
"""核心验证：
1) 从 pristine 提取官方 charlist / 从 _v534_build 提取补丁 charlist
2) 用两张表分别解码运行时 slot [0x726,0x9b4,0x720,0x2af,0x1b3]
3) 看哪个表给出合理中文
"""
import sys, struct, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"F:/sr2-cn")
from minivpp import MiniVpp


def get_cl(vpp_path, name="charlist_CH", ext="txt"):
    v = MiniVpp(vpp_path)
    e = v.find(name, ext)
    if not e:
        return None
    raw = v.read(e)
    return raw


def parse_patch(raw):
    txt = raw.decode("ascii", "ignore")
    return [int(x) for x in txt.split() if x.strip().isdigit()]


def parse_orig(raw):
    i = raw.find(b"32")
    # 跳到第一个独立的 32
    import re
    m = re.search(rb"(?m)^32\r?$", raw)
    if m:
        raw2 = raw[m.start():]
    else:
        raw2 = raw
    return [int(x) for x in raw2.decode("ascii", "ignore").split() if x.strip().isdigit()]


print("=== 尝试各 vpp ===")
for p in [r"F:/sr2-cn/pristine/patch.vpp_pc", r"F:/sr2-cn/_v534_build.vpp_pc",
          r"F:/sr2-cn/_tmp_v532.vpp_pc", r"F:/sr2-cn/_broken_exp1.vpp_pc"]:
    if not os.path.exists(p):
        print("  missing", p); continue
    try:
        v = MiniVpp(p)
        names = [(e["name"], e["ext"]) if isinstance(e, dict) else e for e in v.entries()]
        cl = [x for x in names if "charlist" in str(x).lower()]
        print("  %s -> charlist entries: %s" % (os.path.basename(p), cl[:5]))
    except Exception as ex:
        print("  %s ERR %s" % (p, ex))

# 详细用 pristine
raw_o = get_cl(r"F:/sr2-cn/pristine/patch.vpp_pc")
print("\npristine charlist raw len:", len(raw_o) if raw_o else None)
if raw_o:
    print("head:", raw_o[:80])
    orig = parse_orig(raw_o)
    print("官方表项数:", len(orig), "前16:", orig[:16])
else:
    orig = []

raw_p = get_cl(r"F:/sr2-cn/_v534_build.vpp_pc")
print("\nv534 charlist raw len:", len(raw_p) if raw_p else None)
if raw_p:
    print("head:", raw_p[:80])
    patch = parse_patch(raw_p)
    print("补丁表项数:", len(patch), "前16:", patch[:16])
else:
    patch = []

# 运行时 slot（来自 0x7A8404A0）
slots = [0x726, 0x9B4, 0x720, 0x2AF, 0x1B3]
print("\n=== 用两张表解码运行时 slot %s ===" % [hex(x) for x in slots])


def decode(slots, table, name):
    out = []
    for s in slots:
        idx = s - 0x20
        if 0 <= idx < len(table):
            cp = table[idx]
            out.append(chr(cp) if cp < 0x10000 else "?")
        else:
            out.append("OOB")
    print("  %-16s -> %s" % (name, "".join(out)))


if orig:
    decode(slots, orig, "官方表(2838)")
if patch:
    decode(slots, patch, "补丁表(%d)" % len(patch))

# 也试 slot+5 / slot-5
for delta in (5, -5):
    s2 = [s + delta for s in slots]
    print("  --- slot%+d ---" % delta)
    if orig:
        decode(s2, orig, "官方表")
    if patch:
        decode(s2, patch, "补丁表")
