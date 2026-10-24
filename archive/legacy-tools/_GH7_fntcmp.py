# -*- coding: utf-8 -*-
"""GH7: 对比 patch / common / pegs 三处的 fnt_chinese 数据（vf3 + g_peg_pc 描述符）。"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def md5(b):
    return hashlib.md5(b).hexdigest()

def vf3_info(raw):
    if len(raw) < 32:
        return "too small"
    magic = raw[:4]
    N = struct.unpack_from("<I", raw, 8)[0]
    return "magic=%r N=%d len=%d" % (magic, N, len(raw))

def peg_info(raw):
    # 提取可打印串
    import re
    strs = [m.group().decode("ascii") for m in re.finditer(rb"[\x20-\x7e]{4,}", raw)]
    head = raw[:0x40]
    return "len=%d  @0x0C=%d @0x34=%d  串=%s" % (
        len(raw),
        struct.unpack_from("<I", raw, 0x0C)[0] if len(raw) > 0x10 else -1,
        struct.unpack_from("<I", raw, 0x34)[0] if len(raw) > 0x38 else -1,
        strs[-3:] if strs else [])

for label, vp in [("common", "common.vpp_pc"), ("pegs", "pegs.vpp_pc"), ("patch", "patch.vpp_pc")]:
    p = os.path.join(G, vp)
    v = Vpp(p)
    print("\n===== %s =====" % label)
    for e in v.entries():
        nm = (e["name"] or "")
        ex = (e["ext"] or "")
        if nm.startswith("fnt_") and ex in ("vf3_pc", "g_peg_pc"):
            raw = v.read(e)
            if ex == "vf3_pc":
                print("  %s.%s  %s  md5=%s" % (nm, ex, vf3_info(raw), md5(raw)[:12]))
            else:
                print("  %s.%s  %s" % (nm, ex, peg_info(raw)))
