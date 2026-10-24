# -*- coding: utf-8 -*-
"""GE1: 对比 官方 static_CH 与 汉化 static_CH 同一条字幕的原始 u16 序列。
判断两者存的到底是 "字符表索引+32" 还是 "Unicode 码位"。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

ORIG = r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig"
HAN  = r"F:\sr2-cn\_zip92\黑道圣徒2简体汉化补丁\patch.vpp_pc"
G    = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def get(vp, name, ext):
    v = Vpp(vp)
    e = v.find(name, ext)
    return v.read(e) if e else None

def charlist(vp):
    raw = get(vp, "charlist_CH", "txt")
    if raw is None:
        return None
    return [int(s) for s in raw.decode("utf-8", "replace").replace("\r", "\n").split("\n") if s.strip().isdigit()]

def parse(raw):
    N = struct.unpack_from("<I", raw, 8)[0]
    body = raw[16 + N * 8:]
    pieces = []
    cur = []
    i = 0
    while i + 1 < len(body):
        c = struct.unpack_from(">H", body, i)[0]
        i += 2
        if c == 0:
            pieces.append(cur); cur = []
        else:
            cur.append(c)
    if cur: pieces.append(cur)
    return N, pieces

TARGET = 0xF284ED87

def find_by_id(pieces, tid):
    lo, hi = tid & 0xFFFF, (tid >> 16) & 0xFFFF
    for k, p in enumerate(pieces):
        if len(p) >= 2 and ((p[0] == hi and p[1] == lo) or (p[0] == lo and p[1] == hi)):
            return k, p
    return None, None

for tag, vp in (("ORIG", ORIG), ("HAN", HAN)):
    raw = get(vp, "static_CH", "le_strings")
    T = charlist(vp)
    N, pieces = parse(raw)
    print("=" * 70)
    print("[%s] static_CH %d bytes  N=%d  pieces=%d  charlist=%d" % (tag, len(raw), N, len(pieces), len(T) if T else -1))
    print("     charlist head:", T[:12] if T else None)
    print("     charlist tail:", T[-8:] if T else None)
    # charlist 是否 ASCII 稠密 (T[i] == i+32)
    if T:
        dense = sum(1 for i, c in enumerate(T) if i < 200 and c == i + 32)
        print("     ASCII 稠密检查 (前200项中 T[i]==i+32 的个数):", dense)
    k, p = find_by_id(pieces, TARGET)
    if p is None:
        print("     !! 未找到 id=0x%08X" % TARGET)
        continue
    print("     piece #%d  len=%d" % (k, len(p)))
    body = p[2:]
    print("     raw u16:", body)
    print("     前8个 u16:", body[:8], " 最高:", max(body), " 最低:", min(body))
    # 解释A: 索引+32
    s_idx = "".join(chr(T[c - 32]) if T and 0 <= c - 32 < len(T) else "?" for c in body)
    print("     解A(索引+32):", s_idx)
    # 解释B: 直接当 Unicode 码位
    s_cp = "".join(chr(c) if 32 <= c < 0x10000 else "?" for c in body)
    print("     解B(码位):  ", s_cp)
    # 解释C: 当 codepoint 再查 charlist
    pos = {}
    if T:
        for i, c in enumerate(T):
            pos.setdefault(c, i)
    s_c = "".join(chr(T[pos[c]]) if T and c in pos else "?" for c in body)
    print("     解C(码位->查表):", s_c)
