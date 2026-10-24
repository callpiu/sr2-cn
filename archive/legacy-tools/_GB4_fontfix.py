# -*- coding: utf-8 -*-
"""GB4: 把 UI 英文字体全部换成中文字体数据。

根因（已由多轮实验确认）：
  sr2.vint_proj 的字体别名
      thin / thin_overlay  -> fnt_body_n (+ fnt_body_s)
      header_n / ...       -> fnt_head_n (+ fnt_head_s)
      bodyital_overlay     -> fnt_bodyital_n (+ fnt_bodyital_s)
  这些 "fnt_*" 都是**英文**字体，vf3 只有 224 个字形；而字符表
  charlist_CH.txt 有 2795 项。凡是中文（槽位 >= 224）都会越界，
  取到 vf3 数组之外的垃圾 U/V -> 图集里随机的格子 -> 乱码。
  官方简/繁中本地化只提供 fnt_chinese，没有替换这些字体，所以
  原版游戏就存在该缺陷（用户已实测确认）。

修复：把 6 个英文字体的三件套全部替换为 fnt_chinese 的数据
      common.vpp_pc  : <font>.vf3_pc  <- fnt_chinese.vf3_pc  (N=2795)
      textures.vpp_pc: <font>         <- fnt_chinese 图集     (2048x2048)
      pegs.vpp_pc    : 描述符 dataSize/w/h/fmt 改为 fnt_chinese 的值
"""
import sys, os, struct, hashlib, shutil, subprocess

sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
COMMON = os.path.join(G, "common.vpp_pc")
TEX    = os.path.join(G, "textures.vpp_pc")
PEGS   = os.path.join(G, "pegs.vpp_pc")
BAK    = r"F:\sr2-cn\_backup_M"

TARGETS = ["fnt_body_n", "fnt_body_s", "fnt_head_n", "fnt_head_s",
           "fnt_bodyital_n", "fnt_bodyital_s"]

def md5f(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

# ---------------------------------------------------------------- 0 安全检查
out = subprocess.run(["tasklist"], capture_output=True).stdout
if b"sr2_pc.exe" in out.lower():
    print("[ABORT] 游戏仍在运行，请先完全退出。"); sys.exit(1)

os.makedirs(BAK, exist_ok=True)
for p in (COMMON, TEX, PEGS):
    dst = os.path.join(BAK, os.path.basename(p) + ".before_fontfix")
    if not os.path.exists(dst):
        shutil.copy2(p, dst); print("备份 ->", dst)
    else:
        print("备份已存在:", dst)

print()
print("修复前:")
print("  common  :", md5f(COMMON))
print("  textures:", md5f(TEX))
print("  pegs    :", md5f(PEGS))

# ---------------------------------------------------------------- 1 取源数据
c = Vpp(COMMON); cn_vf3 = c.read(c.find("fnt_chinese", "vf3_pc"))
assert len(cn_vf3) == 67268, len(cn_vf3)
N = struct.unpack_from("<I", cn_vf3, 8)[0]
print("\nfnt_chinese.vf3_pc : %d bytes  N=%d  md5=%s" % (
    len(cn_vf3), N, hashlib.md5(cn_vf3).hexdigest()[:12]))

t = Vpp(TEX); cn_atlas = t.read(t.find("fnt_chinese"))
assert len(cn_atlas) == 4194304, len(cn_atlas)
print("fnt_chinese 图集    : %d bytes  md5=%s" % (len(cn_atlas), hashlib.md5(cn_atlas).hexdigest()[:12]))

pg = Vpp(PEGS); cn_desc = pg.read(pg.find("fnt_chinese"))
cn_size = struct.unpack_from("<I", cn_desc, 12)[0]
cn_w, cn_h = struct.unpack_from("<HH", cn_desc, 28)
cn_fmt = struct.unpack_from("<I", cn_desc, 32)[0]
print("fnt_chinese 描述符  : dataSize=%d w=%d h=%d fmt=%d" % (cn_size, cn_w, cn_h, cn_fmt))
assert cn_size == len(cn_atlas) and (cn_w, cn_h) == (2048, 2048) and cn_fmt == 401

# ---------------------------------------------------------------- 2 替换 vf3
print("\n=== common.vpp_pc : 替换 vf3 ===")
for nm in TARGETS:
    e = c.find(nm, "vf3_pc")
    if e is None:
        print("  %-16s MISSING (跳过)" % nm); continue
    oldN = struct.unpack_from("<I", c.read(e), 8)[0]
    c.replace_body_appended(e, cn_vf3)
    print("  %-16s N=%d -> %d" % (nm, oldN, N))
c.save(COMMON)
print("  已保存 md5 =", md5f(COMMON))

# ---------------------------------------------------------------- 3 替换图集
print("\n=== textures.vpp_pc : 替换图集 ===")
for nm in TARGETS:
    e = t.find(nm)
    if e is None:
        print("  %-16s MISSING (跳过)" % nm); continue
    oldsz = e["size"]
    t.replace_body_appended(e, cn_atlas)
    print("  %-16s %d -> %d" % (nm, oldsz, len(cn_atlas)))
t.save(TEX)
print("  已保存 md5 =", md5f(TEX))

# ---------------------------------------------------------------- 4 改描述符
print("\n=== pegs.vpp_pc : 改描述符尺寸 ===")
for nm in TARGETS:
    e = pg.find(nm)
    if e is None:
        print("  %-16s MISSING (跳过)" % nm); continue
    d = bytearray(pg.read(e))
    before = (struct.unpack_from("<I", d, 12)[0],) + struct.unpack_from("<HH", d, 28) + \
             (struct.unpack_from("<I", d, 32)[0],)
    struct.pack_into("<I",  d, 12, cn_size)
    struct.pack_into("<HH", d, 28, cn_w, cn_h)
    struct.pack_into("<I",  d, 32, cn_fmt)
    after = (struct.unpack_from("<I", d, 12)[0],) + struct.unpack_from("<HH", d, 28) + \
            (struct.unpack_from("<I", d, 32)[0],)
    pg.replace_body_appended(e, bytes(d))
    print("  %-16s %s -> %s" % (nm, before, after))
pg.save(PEGS)
print("  已保存 md5 =", md5f(PEGS))

# ---------------------------------------------------------------- 5 回读校验
print("\n=== 回读校验 ===")
c2 = Vpp(COMMON)
for nm in TARGETS:
    e = c2.find(nm, "vf3_pc")
    if e is None: continue
    b = c2.read(e)
    assert hashlib.md5(b).hexdigest() == hashlib.md5(cn_vf3).hexdigest(), nm
    print("  %-16s vf3 OK (N=%d)" % (nm, struct.unpack_from("<I", b, 8)[0]))
t2 = Vpp(TEX)
for nm in TARGETS:
    e = t2.find(nm)
    if e is None: continue
    assert hashlib.md5(t2.read(e)).hexdigest() == hashlib.md5(cn_atlas).hexdigest(), nm
    print("  %-16s 图集 OK" % nm)
p2 = Vpp(PEGS)
for nm in TARGETS:
    e = p2.find(nm)
    if e is None: continue
    d = p2.read(e)
    assert struct.unpack_from("<I", d, 12)[0] == cn_size
    assert struct.unpack_from("<HH", d, 28) == (cn_w, cn_h)
    assert struct.unpack_from("<I", d, 32)[0] == cn_fmt
    print("  %-16s 描述符 OK" % nm)
print("\n条目数:", len(c2.entries()), len(t2.entries()), len(p2.entries()))
print("\n=== 完成 ===")
