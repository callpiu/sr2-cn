# -*- coding: utf-8 -*-
"""GD1: 补齐 pegs 描述符里被漏掉的第二个 size 字段(@52)。

_GB4_fontfix 只改了 @12(dataSize)，但官方描述符里 @12 与 @52 是同一个值的两份拷贝。
@52 没改 -> 引擎若读 @52 就会按 262144 去取图集 -> 图集被截断 -> 仍然是乱的。
本脚本把 6 个字体的 @12/@52/w,h/fmt 全部对齐到 fnt_chinese 的值。
"""
import sys, os, struct, hashlib, shutil, subprocess

sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
PEGS = os.path.join(G, "pegs.vpp_pc")
COMMON = os.path.join(G, "common.vpp_pc")
TEX = os.path.join(G, "textures.vpp_pc")
BAK = r"F:\sr2-cn\_backup_N"

TARGETS = ["fnt_body_n", "fnt_body_s", "fnt_head_n", "fnt_head_s",
           "fnt_bodyital_n", "fnt_bodyital_s"]

def md5f(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

out = subprocess.run(["tasklist"], capture_output=True).stdout
if b"sr2_pc.exe" in out.lower():
    print("[ABORT] 游戏仍在运行，请先完全退出。"); sys.exit(1)

os.makedirs(BAK, exist_ok=True)
for p in (PEGS, COMMON, TEX):
    dst = os.path.join(BAK, os.path.basename(p) + ".before_desc_fix")
    if not os.path.exists(dst):
        shutil.copy2(p, dst); print("备份 ->", dst)

pg = Vpp(PEGS)
cn = pg.read(pg.find("fnt_chinese"))
SIZE = struct.unpack_from("<I", cn, 12)[0]
W, H = struct.unpack_from("<HH", cn, 28)
FMT = struct.unpack_from("<I", cn, 32)[0]
print("\nfnt_chinese 描述符: size=%d w,h=%s fmt=%d" % (SIZE, (W, H), FMT))

print("\n=== 修正 6 个字体的描述符 ===")
for nm in TARGETS:
    e = pg.find(nm)
    if e is None:
        print("  %-16s MISSING" % nm); continue
    d = bytearray(pg.read(e))
    before = (struct.unpack_from("<I", d, 12)[0], struct.unpack_from("<I", d, 52)[0],
              struct.unpack_from("<HH", d, 28), struct.unpack_from("<I", d, 32)[0])
    struct.pack_into("<I", d, 12, SIZE)
    struct.pack_into("<I", d, 52, SIZE)
    struct.pack_into("<HH", d, 28, W, H)
    struct.pack_into("<I", d, 32, FMT)
    pg.replace_body_appended(e, bytes(d))
    after = (struct.unpack_from("<I", d, 12)[0], struct.unpack_from("<I", d, 52)[0],
             struct.unpack_from("<HH", d, 28), struct.unpack_from("<I", d, 32)[0])
    print("  %-16s @12,@52,w/h,fmt  %s -> %s" % (nm, before, after))
pg.save(PEGS)
print("  pegs 已保存 md5 =", md5f(PEGS))

# ---------------------------------------------------------------- 回读校验
print("\n=== 回读校验 ===")
p2 = Vpp(PEGS)
ok = True
for nm in TARGETS:
    e = p2.find(nm)
    if e is None: continue
    d = p2.read(e)
    a = struct.unpack_from("<I", d, 12)[0]
    b = struct.unpack_from("<I", d, 52)[0]
    wh = struct.unpack_from("<HH", d, 28)
    f = struct.unpack_from("<I", d, 32)[0]
    good = (a == SIZE and b == SIZE and wh == (W, H) and f == FMT)
    ok &= good
    print("  %-16s @12=%d @52=%d w,h=%s fmt=%d  %s" % (nm, a, b, wh, f, "OK" if good else "FAIL"))

# ---------------------------------------------------------------- 顺带核对 vf3 / 图集
c = Vpp(COMMON); t = Vpp(TEX)
print("\n=== vf3 / 图集 核对 ===")
for nm in TARGETS:
    ev = c.find(nm, "vf3_pc"); et = t.find(nm)
    n = struct.unpack_from("<I", c.read(ev), 8)[0] if ev else -1
    print("  %-16s vf3 N=%-5d  图集 %d" % (nm, n, et["size"] if et else -1))

print("\n=== 完成，一致性:", "PASS" if ok else "FAIL", "===")
