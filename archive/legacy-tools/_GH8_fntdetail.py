# -*- coding: utf-8 -*-
"""GH8: 逐条 dump common/pegs/patch/textures 里 name 含 fnt_chinese 的条目详情。"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def md5(b):
    return hashlib.md5(b).hexdigest()

for vp in ("common.vpp_pc", "pegs.vpp_pc", "patch.vpp_pc", "textures.vpp_pc"):
    p = os.path.join(G, vp)
    v = Vpp(p)
    print("\n===== %s (%d B) =====" % (vp, os.path.getsize(p)))
    for e in v.entries():
        nm = (e["name"] or "")
        if "fnt_chinese" not in nm and "fnt_chinese" not in (e["ext"] or ""):
            continue
        raw = v.read(e)
        hdr = raw[:48]
        print("  idx=%-6s name=%-20r ext=%-12r size=%-10d md5=%s" % (
            e["idx"], e["name"], e["ext"], e["size"], md5(raw)[:12]))
        print("     head: " + " ".join("%02X" % c for c in hdr[:32]))
        print("     ascii: " + "".join(chr(c) if 32 <= c < 127 else "." for c in hdr[:48]))
        # 尝试描述符解析
        if len(raw) > 0x40:
            try:
                f8 = struct.unpack_from("<I", raw, 8)[0]
                fc = struct.unpack_from("<I", raw, 0x0C)[0]
                f34 = struct.unpack_from("<I", raw, 0x34)[0]
                print("     @8=%d @0x0C=%d @0x34=%d" % (f8, fc, f34))
            except Exception:
                pass
