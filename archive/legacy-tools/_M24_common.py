# -*- coding: utf-8 -*-
# 决定性：common.vpp_pc 里 thin_overlay 别名指向的英文字体 vf3 是什么？
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
COMMON = os.path.join(G, "common.vpp_pc")
VANILLA_COMMON = r"F:/sr2-cn/_backup_CN/common.vpp_pc.official_20261017_0402"

import hashlib
for p in (COMMON, VANILLA_COMMON):
    if os.path.exists(p):
        print("%s  md5=%s" % (os.path.basename(p), hashlib.md5(open(p, "rb").read()).hexdigest()))


def scan(path, tag):
    v = Vpp(path)
    print("\n########## %s ##########" % tag)
    for e in v.entries():
        if (e["ext"] or "").lower() != "vf3_pc":
            continue
        d = v.read(e)
        if len(d) < 12 or d[:4] != b"VFNT":
            continue
        N, = struct.unpack_from("<I", d, 8)
        UOFF = 0xD0 + N * 16
        VOFF = UOFF + N * 4
        nv = (len(d) - VOFF) // 4
        s28 = ""
        if 0x28 < len(d):
            end = d.find(b"\x00", 0x28)
            s28 = d[0x28:end if end > 0 else 0x28 + 30]
        if "chinese" in (e["name"] or "").lower() or "body" in (e["name"] or "").lower() \
           or "head" in (e["name"] or "").lower() or "ital" in (e["name"] or "").lower():
            print("  %-22s %7d B  N=%-5d V项=%-5d  内嵌串=%s" % (
                e["name"], len(d), N, nv, s28.decode("ascii", "replace")))


scan(COMMON, "当前 common.vpp_pc（汉化版）")
scan(VANILLA_COMMON, "官方原版 common.vpp_pc")

# 关键对比：fnt_body_n 的 vf3 是否 == fnt_chinese 的
for p, tag in ((COMMON, "当前"), (VANILLA_COMMON, "官方")):
    v = Vpp(p)
    body = v.find("fnt_body_n", "vf3_pc")
    chi = v.find("fnt_chinese", "vf3_pc")
    if body and chi:
        db, dc = v.read(body), v.read(chi)
        print("\n%s: fnt_body_n.vf3 (%d B) vs fnt_chinese.vf3 (%d B) 相同=%s" % (
            tag, len(db), len(dc), db == dc))
