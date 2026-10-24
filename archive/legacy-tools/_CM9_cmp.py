import sys, os
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn")
from _vpp import Vpp

D = r"F:\sr2-cn\_fontdump"
def grab(vpp, name, ext, out):
    v = Vpp(vpp)
    e = v.find(name, ext)
    if e is None:
        print("MISS", name, ext, vpp); return None
    b = v.read(e)
    open(out, "wb").write(b)
    print("OK", out, len(b))
    return b

grab(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig", "fnt_chinese", "g_peg_pc", D + r"\off_patch.tex")
grab(r"F:\sr2-cn\vpp_backup\textures.vpp_pc.orig", "fnt_chinese", None, D + r"\off_tex.tex")
grab(r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc", "fnt_chinese", "g_peg_pc", D + r"\game_patch.tex")
grab(r"G:\SteamLibrary\steamapps\common\Saints Row 2\textures.vpp_pc", "fnt_chinese", None, D + r"\game_tex.tex")

for tag in ("off_patch", "off_tex", "game_patch", "game_tex"):
    p = D + "\\" + tag + ".tex"
    if not os.path.exists(p): continue
    a = np.fromfile(p, dtype=np.uint8)
    if len(a) != 4194304:
        print(tag, "size", len(a)); continue
    a = a.reshape(2048, 2048)
    nz = int((a > 0).sum()); strong = int((a > 110).sum())
    rows = (a > 0).sum(axis=1)
    nzrow = int((rows > 0).sum())
    print("%-11s 非零=%d 强墨=%d 非零行=%d 行28..39=%s 行10,14,18,22=%s" % (
        tag, nz, strong, nzrow, list(rows[28:40]), [int(rows[i]) for i in (10, 14, 18, 22)]))
    Image.fromarray(a, "L").resize((1024, 1024), Image.NEAREST).save(D + r"\ov_" + tag + ".png")
