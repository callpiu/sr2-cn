# -*- coding: utf-8 -*-
"""GE6: 精确定位 ID 0xF284ED87 在各 le_strings 中的位置并解码上下文。"""
import sys, os, struct, glob
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

ORIG = r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig"
HAN  = r"F:\sr2-cn\_zip92\黑道圣徒2简体汉化补丁\patch.vpp_pc"
G    = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
IDB  = bytes.fromhex("F284ED87")

def charlist(v):
    e = v.find("charlist_CH", "txt")
    if not e: return None
    return [int(s) for s in v.read(e).decode("utf-8","replace").replace("\r","\n").split("\n") if s.strip().isdigit()]

def body_of(raw):
    N = struct.unpack_from("<I", raw, 8)[0]
    return raw[16 + N*8:]

def dec_at(body, off, T, span=60):
    """从 off 开始按 u16 读到 0 为止"""
    out = []
    i = off
    while i + 1 < len(body) and len(out) < span:
        c = struct.unpack_from(">H", body, i)[0]; i += 2
        if c == 0: break
        out.append(c)
    s = "".join(chr(T[c-32]) if T and 0 <= c-32 < len(T) else "?" for c in out[2:])
    return out, s

def scan_vpp(tag, path):
    v = Vpp(path)
    T = charlist(v)
    print("="*72); print("[%s] %s   charlist=%s" % (tag, os.path.basename(path), len(T) if T else "无"))
    for k, e in enumerate(v.entries()):
        nm, ex_ = e["name"] or "", e["ext"] or ""
        if "le_strings" not in ex_ and "le_strings" not in nm: continue
        raw = v.read(e)
        off = raw.find(IDB)
        if off < 0: continue
        body = body_of(raw)
        bo = off - (16 + struct.unpack_from("<I", raw, 8)[0]*8)
        cds, s = dec_at(body, bo, T)
        print("  %-18s %-12s off=%d  ID_u16=%s" % (nm, ex_, off, cds[:2]))
        print("      %s" % s)

def scan_loose(path):
    raw = open(path, "rb").read()
    off = raw.find(IDB)
    if off < 0: return
    N = struct.unpack_from("<I", raw, 8)[0]
    body = raw[16 + N*8:]
    bo = off - (16 + N*8)
    cds, _ = dec_at(body, bo, None)
    # 用 US charlist (从 ORIG patch 取) 解
    v = Vpp(ORIG); Te = v.find("charlist_US", "txt")
    T = None
    if Te:
        T = [int(s) for s in v.read(Te).decode("utf-8","replace").replace("\r","\n").split("\n") if s.strip().isdigit()]
    s = "".join(chr(T[c-32]) if T and 0 <= c-32 < len(T) else "?" for c in cds[2:])
    print("  %-40s off=%d  N=%d" % (os.path.basename(path), off, N))
    print("      %s" % s)

scan_vpp("ORIG-patch", ORIG)
scan_vpp("HAN-patch", HAN)
scan_vpp("CUR-patch", os.path.join(G, "patch.vpp_pc"))
print("="*72); print("[LOOSE]")
for f in sorted(glob.glob(os.path.join(G, "Mods", "static_*.le_strings"))):
    scan_loose(f)
