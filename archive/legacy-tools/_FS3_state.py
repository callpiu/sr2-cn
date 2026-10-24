"""FS3: (a) original font alias table from the pre-fix backup, (b) current state
of fnt_body_n / fnt_body_s across common/textures/pegs.
"""
import sys, os, re, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
BAK = r"F:\sr2-cn\_backup_J\common.before_vintproj_font_20261014.vpp_pc"

if os.path.isfile(BAK):
    v = Vpp(BAK)
    e = v.find("sr2", "vint_proj")
    txt = v.read(e).decode("utf-8", "replace")
    print("== ORIGINAL sr2.vint_proj font aliases ==")
    for m in re.finditer(r"<font_info>(.*?)</font_info>", txt, re.S):
        blk = m.group(1)
        fn = re.search(r"<filename>(.*?)</filename>", blk)
        al = re.search(r"<alias>(.*?)</alias>", blk)
        fo = re.search(r"<filename_overlay>(.*?)</filename_overlay>", blk)
        print("   alias=%-20s filename=%-18s overlay=%s" % (
            al.group(1) if al else "?", fn.group(1) if fn else "?", fo.group(1) if fo else "?"))
else:
    print("no backup at", BAK)

print()
print("== CURRENT state of the fonts the aliases point to ==")
for name, targets in [("common.vpp_pc", [("fnt_body_n", "vf3_pc"), ("fnt_body_s", "vf3_pc"),
                                         ("fnt_head_n", "vf3_pc"), ("fnt_chinese", "vf3_pc")]),
                      ("textures.vpp_pc", [("fnt_body_n", None), ("fnt_body_s", None),
                                           ("fnt_head_n", None), ("fnt_chinese", None)]),
                      ("pegs.vpp_pc", [("fnt_body_n", None), ("fnt_chinese", None)])]:
    p = os.path.join(G, name)
    v = Vpp(p)
    print("--", name)
    for nm, ext in targets:
        e = v.find(nm, ext) if ext else v.find(nm)
        if e is None:
            print("   %-14s MISSING" % nm); continue
        b = v.read(e)
        extra = ""
        if ext == "vf3_pc":
            n = struct.unpack_from("<I", b, 8)[0]
            extra = " N=%d" % n
        if name == "pegs.vpp_pc" and len(b) < 120:
            extra = " dataSize=%d w=%d h=%d" % (
                struct.unpack_from("<I", b, 12)[0], *struct.unpack_from("<HH", b, 28))
        print("   %-14s size=%-9d md5=%s%s" % (nm, len(b), hashlib.md5(b).hexdigest()[:12], extra))
