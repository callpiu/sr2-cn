# -*- coding: utf-8 -*-
"""GE2: 找出这条字幕在各个 static_CH 里的分布, 判断游戏到底加载哪一份。"""
import sys, os, struct, glob
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

ORIG = r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig"
HAN  = r"F:\sr2-cn\_zip92\黑道圣徒2简体汉化补丁\patch.vpp_pc"
G    = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
FMT  = [91, 102, 111, 114, 109, 97, 116, 93]   # "[format]"

def parse(raw):
    N = struct.unpack_from("<I", raw, 8)[0]
    body = raw[16 + N * 8:]
    pieces, cur, i = [], [], 0
    while i + 1 < len(body):
        c = struct.unpack_from(">H", body, i)[0]; i += 2
        if c == 0:
            pieces.append(cur); cur = []
        else:
            cur.append(c)
    if cur: pieces.append(cur)
    return N, pieces

def sub(a, b):
    n = len(b)
    return [i for i in range(len(a) - n + 1) if a[i:i + n] == b]

def scan(tag, path, name="static_CH", ext="le_strings", vp_for_cl=None):
    try:
        v = Vpp(path)
    except Exception as ex:
        print("[%s] 打开失败 %s" % (tag, ex)); return
    e = v.find(name, ext)
    if not e:
        print("[%s] 无 %s.%s" % (tag, name, ext)); return
    raw = v.read(e)
    T = None
    src = vp_for_cl or path
    try:
        vv = Vpp(src); ce = vv.find("charlist_CH", "txt")
        if ce:
            T = [int(s) for s in vv.read(ce).decode("utf-8", "replace").replace("\r", "\n").split("\n") if s.strip().isdigit()]
    except Exception:
        pass
    N, pieces = parse(raw)
    print("=" * 72)
    print("[%s] %s.%s  %d bytes  N=%d pieces=%d charlist=%s" % (tag, name, ext, len(raw), N, len(pieces), len(T) if T else "?"))
    hits = 0
    for k, p in enumerate(pieces):
        for off in sub(p, FMT):
            hits += 1
            st = max(0, off - 12)
            seg = p[st:off + 30]
            idx = "".join(chr(T[c - 32]) if T and 0 <= c - 32 < len(T) else "?" for c in p[:off + 14])
            cp = "".join(chr(c) if 32 <= c < 0x10000 else "?" for c in p[:off + 14])
            print("  piece#%d off=%d  hdr=%s" % (k, off, p[:2]))
            print("     idx: %s" % idx)
            print("     cp : %s" % cp)
            if hits >= 4: break
        if hits >= 4: break
    if hits == 0:
        print("  (无 [format] 命中)")

scan("ORIG-patch", ORIG)
scan("HAN-zip-patch", HAN)
scan("CUR-game-patch", os.path.join(G, "patch.vpp_pc"))
scan("CUR-game-common", os.path.join(G, "common.vpp_pc"))
for f in glob.glob(os.path.join(G, "Mods", "static_*.le_strings")):
    print("\n[LOOSE] %s  (%d bytes)" % (os.path.basename(f), os.path.getsize(f)))
