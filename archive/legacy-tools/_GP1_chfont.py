import sys, os, shutil, hashlib, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def md5f(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

# 取汉化版 fnt_chinese 的 vf3 + 图集（来自 patch.vpp_pc）
p = Vpp(os.path.join(G, "patch.vpp_pc"))
CH_VF3 = p.read(p.find("fnt_chinese", "vf3_pc"))          # 67268, N=2795
CH_ATL = p.read(p.find("fnt_chinese", "g_peg_pc"))        # 4194304
print("汉化 fnt_chinese vf3 :", len(CH_VF3), "N=", struct.unpack_from("<I", CH_VF3, 8)[0])
print("汉化 fnt_chinese atlas:", len(CH_ATL), "md5", hashlib.md5(CH_ATL).hexdigest())

# ---- 1) common.vpp_pc: fnt_chinese.vf3_pc <- 汉化版 ----
cp = os.path.join(G, "common.vpp_pc")
os.makedirs(r"F:\sr2-cn\_backup_C", exist_ok=True)
cbak = r"F:\sr2-cn\_backup_C\common.vpp_pc.before_chfont"
if not os.path.exists(cbak):
    shutil.copy2(cp, cbak); print("[backup]", cbak)
print("common md5 BEFORE:", md5f(cp))
c = Vpp(cp)
e = c.find("fnt_chinese", "vf3_pc")
c.replace_body_appended(e, CH_VF3)
c.save(cp)
print("common md5 AFTER :", md5f(cp))

# ---- 2) textures.vpp_pc: fnt_chinese <- 汉化版图集 ----
tp = os.path.join(G, "textures.vpp_pc")
os.makedirs(r"F:\sr2-cn\_backup_T", exist_ok=True)
tbak = r"F:\sr2-cn\_backup_T\textures.vpp_pc.before_chfont"
if not os.path.exists(tbak):
    shutil.copy2(tp, tbak); print("[backup]", tbak)
print("textures md5 BEFORE:", md5f(tp))
t = Vpp(tp)
e = t.find("fnt_chinese")
t.replace_body_appended(e, CH_ATL)
t.save(tp)
print("textures md5 AFTER :", md5f(tp))

# ---- 回读校验 ----
c2 = Vpp(cp); t2 = Vpp(tp)
cv = c2.read(c2.find("fnt_chinese", "vf3_pc"))
tv = t2.read(t2.find("fnt_chinese"))
print("\n=== 校验 ===")
print("  common  fnt_chinese.vf3 :", len(cv), "N=", struct.unpack_from("<I", cv, 8)[0], "md5", hashlib.md5(cv).hexdigest())
print("  textures fnt_chinese    :", len(tv), "md5", hashlib.md5(tv).hexdigest())
print("  与汉化版一致?", hashlib.md5(cv).hexdigest() == hashlib.md5(CH_VF3).hexdigest(),
      hashlib.md5(tv).hexdigest() == hashlib.md5(CH_ATL).hexdigest())
print("\nREVERT:")
print('  cp "F:/sr2-cn/_backup_C/common.vpp_pc.before_chfont" "%s/common.vpp_pc"' % G.replace("\\", "/"))
print('  cp "F:/sr2-cn/_backup_T/textures.vpp_pc.before_chfont" "%s/textures.vpp_pc"' % G.replace("\\", "/"))
