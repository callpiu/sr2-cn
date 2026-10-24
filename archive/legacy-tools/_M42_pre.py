# -*- coding: utf-8 -*-
# 前置检验：fnt_body_n 的图集与内嵌 peg 名；确认替换 vf3 是否安全
import sys, os, struct, hashlib
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
COMMON = os.path.join(G, "common.vpp_pc")
PATCH = os.path.join(G, "patch.vpp_pc")

for path, tag in ((COMMON, "common"), (PATCH, "patch")):
    v = Vpp(path)
    print("\n########## %s.vpp_pc  md5=%s ##########" % (
        tag, hashlib.md5(open(path, "rb").read()).hexdigest()[:12]))
    for e in v.entries():
        n = (e["name"] or "")
        if not (n in ("fnt_body_n", "fnt_body_s", "fnt_chinese")):
            continue
        d = v.read(e)
        s28 = s68 = ""
        if len(d) > 0x30 and d[:4] == b"VFNT":
            for off in (0x28, 0x68):
                end = d.find(b"\x00", off)
                s = d[off:end if end > 0 else off + 40]
                if s and all(32 <= b < 127 for b in s):
                    if off == 0x28:
                        s28 = s.decode()
                    else:
                        s68 = s.decode()
        print("  %-14s %-10s %8d B  内嵌peg=%s  nobdr=%s" % (
            n, e["ext"], e["size"], s28 or "-", s68 or "-"))

# fnt_body_n 的图集在哪
print("\n=== fnt_body_n.peg / fnt_chinese 图集位置 ===")
for path, tag in ((COMMON, "common"), (PATCH, "patch")):
    v = Vpp(path)
    for e in v.entries():
        n = (e["name"] or "")
        if n in ("fnt_body_n", "fnt_chinese") and (e["ext"] or "") in ("peg_pc", "g_peg_pc"):
            print("  %s: %s.%s  %d B" % (tag, n, e["ext"], e["size"]))
