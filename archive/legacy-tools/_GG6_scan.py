# -*- coding: utf-8 -*-
"""GG6: 扫描所有 VPP, 找出哪些归档里含 fnt_* 条目。"""
import sys, os, glob, struct
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def vpp_entries(path):
    """只读 VPP 头, 返回 [(name, ext, size)]"""
    with open(path, "rb") as f:
        head = f.read(8)
        if len(head) < 8:
            return None
        magic, ver = head[:4], struct.unpack_from("<I", head, 4)[0]
        f.seek(0)
        # 常见 SR2 vpp 头: 0x00 magic, 0x04 ver, 0x08 entries, 0x0C size, 0x10 data_start
        hdr = f.read(0x10)
        n = struct.unpack_from("<I", hdr, 8)[0]
        dstart = struct.unpack_from("<I", hdr, 0x10 - 4)[0] if False else None
        f.seek(0x10)
        idx = f.read(n * 8)
        names = []
        for i in range(n):
            nm_off, ext_off = struct.unpack_from("<II", idx, i * 8)
            names.append((nm_off, ext_off))
        # 读字符串区
        f.seek(0)
        blob = f.read(min(os.path.getsize(path), 4 << 20))
        out = []
        for i, (nm_off, ext_off) in enumerate(names):
            def rd(off):
                e = blob.find(b"\x00", off)
                return blob[off:e].decode("latin-1") if 0 <= off < len(blob) and e > 0 else ""
            out.append((rd(nm_off), rd(ext_off)))
        return out

for p in sorted(glob.glob(os.path.join(G, "*.vpp_pc"))) + sorted(glob.glob(os.path.join(G, "*", "*.vpp_pc"))) + sorted(glob.glob(os.path.join(G, "*", "*", "*.vpp_pc"))):
    sz = os.path.getsize(p)
    try:
        ents = vpp_entries(p)
    except Exception as ex:
        print("%-52s %12d  解析失败 %s" % (os.path.relpath(p, G), sz, ex)); continue
    if ents is None:
        continue
    hits = [x for x in ents if x[0].startswith("fnt")]
    if hits:
        print("=== %s  (%d 条, %d 个 fnt_*) ===" % (os.path.relpath(p, G), len(ents), len(hits)))
        for nm, ex_ in hits:
            print("      %-20s %s" % (nm, ex_))
