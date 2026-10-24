# -*- coding: utf-8 -*-
"""第10轮：把 thin / thin_overlay 指向的 fnt_body_n / fnt_body_s 三件套
(vf3@common + 图集@textures + 描述符@pegs) 整体替换为 fnt_chinese 的数据。
改前完整备份；改动为「追加+重定向」，原始字节仍留在文件内。"""
import os, sys, shutil, hashlib, json
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
PATCH  = os.path.join(G, "patch.vpp_pc")
COMMON = os.path.join(G, "common.vpp_pc")
TEX    = os.path.join(G, "textures.vpp_pc")
PEGS   = os.path.join(G, "pegs.vpp_pc")
BK     = r"F:\sr2-cn\_backup_ALIAS"
os.makedirs(BK, exist_ok=True)

def md5f(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

def find_ent(v, name, ext=None):
    cands = [e for e in v.entries() if e['name'].lower() == name.lower()]
    if ext is not None:
        for e in cands:
            if e['ext'].lower() == ext.lower():
                return e
        return None
    return cands[0] if cands else None

TARGETS = ["fnt_body_n", "fnt_body_s"]

# ---------- 1. 取源数据 ----------
pv = Vpp(PATCH)
src_vf3   = pv.read(find_ent(pv, "fnt_chinese", "vf3_pc"))
src_atlas = pv.read(find_ent(pv, "fnt_chinese", "g_peg_pc"))
print(f"源 fnt_chinese: vf3={len(src_vf3)}  atlas={len(src_atlas)}")

gv = Vpp(PEGS)
src_desc = gv.read(find_ent(gv, "fnt_chinese"))
print(f"源描述符: {len(src_desc)} B")
del gv

# ---------- 2. 备份 ----------
for src, tag in ((COMMON, "common"), (TEX, "textures"), (PEGS, "pegs")):
    dst = os.path.join(BK, f"{tag}.vpp_pc.before_aliasfont")
    if not os.path.exists(dst):
        shutil.copy2(src, dst)
        print(f"备份 {tag} -> {dst}")
    else:
        print(f"备份已存在 {dst}")

with open(os.path.join(BK, "state_before.json"), "w", encoding="utf-8") as f:
    json.dump({"md5": {t: md5f(p) for t, p in
                       (("common", COMMON), ("textures", TEX), ("pegs", PEGS))}},
              f, indent=1)

# ---------- 3. common.vpp_pc : vf3 ----------
cv = Vpp(COMMON)
for nm in TARGETS:
    e = find_ent(cv, nm, "vf3_pc")
    old = len(cv.read(e))
    cv.replace_body_appended(e, src_vf3)
    print(f"  common {nm}.vf3_pc : {old} -> {len(src_vf3)}")
cv.save(COMMON)
print("common saved, md5 =", md5f(COMMON))

# ---------- 4. textures.vpp_pc : 图集 ----------
tv = Vpp(TEX)
for nm in TARGETS:
    e = find_ent(tv, nm)
    old = len(tv.read(e))
    tv.replace_body_appended(e, src_atlas)
    print(f"  textures {nm} : {old} -> {len(src_atlas)}")
tv.save(TEX)
print("textures saved, md5 =", md5f(TEX))

# ---------- 5. pegs.vpp_pc : 描述符 ----------
gv = Vpp(PEGS)
for nm in TARGETS:
    e = find_ent(gv, nm)
    old = len(gv.read(e))
    gv.replace_body_appended(e, src_desc)
    print(f"  pegs {nm} : {old} -> {len(src_desc)}")
gv.save(PEGS)
print("pegs saved, md5 =", md5f(PEGS))

# ---------- 6. 回读校验 ----------
def verify(path, nm, ext, expect):
    v = Vpp(path)
    b = v.read(find_ent(v, nm, ext))
    ok = hashlib.md5(b).hexdigest() == hashlib.md5(expect).hexdigest()
    print(f"  校验 {os.path.basename(path)}::{nm} -> {'OK' if ok else 'FAIL'} ({len(b)} B)")

print("=== 回读校验 ===")
for nm in TARGETS:
    verify(COMMON, nm, "vf3_pc", src_vf3)
    verify(TEX, nm, None, src_atlas)
    verify(PEGS, nm, None, src_desc)
print("DONE")
