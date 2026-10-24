# -*- coding: utf-8 -*-
"""校验被修改的两个 VPP 是否结构完整、可正常解析。"""
import os, sys, struct, hashlib

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
TARGETS = ["fnt_body_n", "fnt_body_s", "fnt_chinese"]

for fn in ("common.vpp_pc", "pegs.vpp_pc", "textures.vpp_pc", "patch.vpp_pc"):
    p = os.path.join(G, fn)
    print("=== %s ===" % fn)
    try:
        with LightVpp(p) as v:
            print("  num=%d csize=%d (实际 %d)" % (v.num, v.csize, os.path.getsize(p)))
            if v.csize != os.path.getsize(p):
                print("  ★ container_size 与实际大小不符！")
            print("  names_at=0x%X ext_at=0x%X data_start=0x%X" % (v.names_at, v.ext_at, v.data_start))
            # 读所有目标条目
            n_ok = 0
            for e in v.entries():
                nm = v.name(e)
                if nm in TARGETS or nm.startswith("fnt_"):
                    ex = v.ext(e)
                    d = v.read(e)
                    got = len(d)
                    status = "OK" if got == e["size"] else "★大小不符"
                    if got == e["size"]:
                        n_ok += 1
                    extra = ""
                    if ex == "vf3_pc":
                        N, = struct.unpack_from("<i", d, 0x08) if len(d) >= 12 else (0,)
                        extra = "N=%d" % N
                    elif "gekv" in "".join(chr(c) for c in d[:4]).lower() or d[:4] == b"GEKV":
                        i = d.find(b"fnt_")
                        extra = d[i:].rstrip(b"\x00").decode("latin1") if i >= 0 else ""
                    print("    %-16s %-10s size=%-8d 读出=%-8d %s  %s" %
                          (nm, ex or "-", e["size"], got, status, extra))
            print("  条目读取校验: %d 个 OK" % n_ok)
    except Exception as ex:
        print("  ★ 解析失败: %s" % ex)
    print()
