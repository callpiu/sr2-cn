import sys, os, shutil, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G  = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pp = os.path.join(G, "common.vpp_pc")
BK = r"F:\sr2-cn\_backup_C"
os.makedirs(BK, exist_ok=True)
bak = os.path.join(BK, "common.vpp_pc.before_projfont")

if not os.path.exists(bak):
    shutil.copy2(pp, bak)
    print("backup ->", bak)
else:
    print("backup already exists ->", bak)

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

print("common.vpp_pc md5 BEFORE:", md5(pp))

v = Vpp(pp)
e = v.find("sr2", "vint_proj")
assert e, "sr2.vint_proj not found"
raw = bytearray(v.read(e))
print("vint_proj size:", len(raw))

A  = b"<alias>thin_overlay</alias>"
F1 = b"<filename>fnt_body_n</filename>"
O1 = b"<filename_overlay>fnt_body_s</filename_overlay>"
F2 = b"<filename>fnt_chinese</filename>"
O2 = b"<filename_overlay>fnt_chinese</filename_overlay>"

i = raw.find(A);  assert i > 0, "alias not found"
j = raw.rfind(F1, 0, i); assert j > 0, "filename before alias not found"
k = raw.find(O1, i);     assert k > i, "filename_overlay after alias not found"

# 从后往前替换，避免索引位移
raw[k:k + len(O1)] = O2
raw[j:j + len(F1)] = F2

i2 = raw.find(A)
print("\n=== 修改后的 thin_overlay 块 ===")
print(raw[i2 - 45:i2 + 200].decode("utf-8", "replace"))

v.replace_body_appended(e, bytes(raw))
v.save(pp)
print("\ncommon.vpp_pc md5 AFTER :", md5(pp))
print("REVERT: copy %s -> %s" % (bak, pp))
