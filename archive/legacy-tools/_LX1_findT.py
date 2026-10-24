# -*- coding: utf-8 -*-
# 关键追查：引擎校验用的繁体表 T（2838 项）到底来自哪个文件？
# 候选：pegs.vpp_pc 的字体描述符 / common.vpp_pc / 图集 peg 内嵌
import sys, struct, os, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
VANILLA = r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017"


def parse_charlist(raw):
    B = []
    for L in raw.split(b"\r\n"):
        s = L.strip()
        if not s or s.startswith(b"//") or s.startswith(b"count="):
            continue
        for tok in s.split():
            if tok.isdigit():
                B.append(chr(int(tok)))
    return B


vv = Vpp(VANILLA)
T = parse_charlist(vv.read(vv.find("charlist_CH", "txt")))
Tcps = [ord(c) for c in T]
print("官方繁体表 T = %d 项" % len(T))

# 在多个 vpp 里搜 T 的码点序列（u16 LE/BE）
targets = []
for f in ("patch.vpp_pc", "common.vpp_pc", "pegs.vpp_pc", "textures.vpp_pc"):
    p = os.path.join(G, f)
    if os.path.exists(p):
        targets.append((f, p))

for name, p in targets:
    try:
        v = Vpp(p)
    except Exception as e:
        print("%s: 打开失败 %s" % (name, e)); continue
    print("\n=== %s ===" % name)
    for e in v.entries():
        raw = None
        try:
            raw = v.read(e)
        except Exception:
            continue
        if not raw or len(raw) < 400:
            continue
        for endian in ("<", ">"):
            for seg in (Tcps, Tcps[:100]):
                pat = b"".join(struct.pack(endian + "H", cp) for cp in seg)
                pos = raw.find(pat)
                if pos >= 0:
                    print("  ★ %s.%s (%d B) 含 T 的 %s-endian 码点序列(%d项) @0x%X" % (
                        e["name"], e["ext"], len(raw), endian, len(seg), pos))
                    break
            else:
                continue
            break

# 也搜单个特征：T[0] 和 T[2837] 的码点
print("\n=== 搜 T 的首尾码点 ===")
for name, p in targets:
    try:
        v = Vpp(p)
    except Exception:
        continue
    for e in v.entries():
        try:
            raw = v.read(e)
        except Exception:
            continue
        if not raw or len(raw) < 400:
            continue
        hits = 0
        for cp in (Tcps[0], Tcps[1], Tcps[500], Tcps[-1]):
            for endian in ("<", ">"):
                if struct.pack(endian + "H", cp) in raw:
                    hits += 1
        if hits >= 2:
            print("  %s.%s 含 %d 个 T 特征码点" % (e["name"], e["ext"], hits))
