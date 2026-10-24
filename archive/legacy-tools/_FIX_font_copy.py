# -*- coding: utf-8 -*-
"""第十六轮：数据层兜底修复。

背景：
  sr2.vint_proj 的 font_info 改了无效 —— 引擎运行时不读它。
  alias "thin_overlay" 仍解析到 fnt_body_n / fnt_body_s（vf3 只有 224 字形），
  而 charlist 有 2795 项 -> 字幕字符索引全部越界 -> 乱码。

  但乱码显示的是"清晰汉字"，汉字只存在于 fnt_chinese 的 2048x2048 图集里，
  说明字幕的图集已经/本来就是 fnt_chinese，只是 vf3 用错了。

方案（绕开 alias 层，直接从数据层解决）：
  把 fnt_body_n / fnt_body_s 三件套全部替换成 fnt_chinese 的数据：
    1) common.vpp_pc  : *.vf3_pc   <- fnt_chinese.vf3_pc
    2) textures.vpp_pc: 图集       <- fnt_chinese 图集
    3) pegs.vpp_pc    : 描述符尺寸 <- fnt_chinese 描述符的 dataSize / w / h
  这样无论引擎如何解析字体名，只要加载 fnt_body_n(_s)，拿到的就是完整中文字体。
"""
import sys, os, struct, hashlib, shutil, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
COMMON = os.path.join(G, "common.vpp_pc")
TEX    = os.path.join(G, "textures.vpp_pc")
PEGS   = os.path.join(G, "pegs.vpp_pc")
BAK    = r"F:\sr2-cn\_backup_K"

TARGETS = ("fnt_body_n", "fnt_body_s")

def md5f(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

# ---------------------------------------------------------------- 0 安全检查
out = subprocess.run(["tasklist"], capture_output=True).stdout
if b"sr2_pc.exe" in out.lower():
    print("[ABORT] 游戏仍在运行，请先退出。")
    sys.exit(1)

os.makedirs(BAK, exist_ok=True)
for p in (COMMON, TEX, PEGS):
    dst = os.path.join(BAK, os.path.basename(p) + ".before_fontcopy_20261014")
    if not os.path.exists(dst):
        shutil.copy2(p, dst)
        print("备份 ->", dst)
    else:
        print("备份已存在:", dst)

print()
print("修复前 md5:")
print("  common  :", md5f(COMMON))
print("  textures:", md5f(TEX))
print("  pegs    :", md5f(PEGS))

# ---------------------------------------------------------------- 1 读源数据
c = Vpp(COMMON)
cn_vf3 = c.read(c.find("fnt_chinese", "vf3_pc"))
assert len(cn_vf3) == 67268, len(cn_vf3)
print("\nfnt_chinese.vf3_pc  =", len(cn_vf3), "md5", hashlib.md5(cn_vf3).hexdigest()[:12])

t = Vpp(TEX)
cn_atlas = t.read(t.find("fnt_chinese"))
assert len(cn_atlas) == 4194304, len(cn_atlas)
print("fnt_chinese 图集     =", len(cn_atlas), "md5", hashlib.md5(cn_atlas).hexdigest()[:12])

p = Vpp(PEGS)
cn_desc = p.read(p.find("fnt_chinese"))
print("fnt_chinese 描述符   =", len(cn_desc))
print("  描述符 hex:", cn_desc.hex())

# 解析 fnt_chinese 描述符的 dataSize / w / h
cn_size = struct.unpack_from("<I", cn_desc, 12)[0]
cn_w, cn_h = struct.unpack_from("<HH", cn_desc, 28)
print("  -> dataSize=%d  w=%d h=%d" % (cn_size, cn_w, cn_h))
assert cn_size == len(cn_atlas), (cn_size, len(cn_atlas))
assert (cn_w, cn_h) == (2048, 2048), (cn_w, cn_h)

# ---------------------------------------------------------------- 2 common: 替换 vf3
print("\n=== common.vpp_pc ===")
for nm in TARGETS:
    e = c.find(nm, "vf3_pc")
    assert e is not None, nm
    old = hashlib.md5(c.read(e)).hexdigest()[:12]
    c.replace_body_appended(e, cn_vf3)
    print("  %-14s .vf3_pc  %s -> 67268" % (nm, old))
c.save(COMMON)
print("  已保存, md5 =", md5f(COMMON))

# ---------------------------------------------------------------- 3 textures: 替换图集
print("\n=== textures.vpp_pc ===")
for nm in TARGETS:
    e = t.find(nm)
    assert e is not None, nm
    old_sz = e["size"]
    t.replace_body_appended(e, cn_atlas)
    print("  %-14s 图集  %d -> 4194304" % (nm, old_sz))
t.save(TEX)
print("  已保存, md5 =", md5f(TEX))

# ---------------------------------------------------------------- 4 pegs: 改描述符尺寸
print("\n=== pegs.vpp_pc ===")
for nm in TARGETS:
    e = p.find(nm)
    assert e is not None, nm
    d = bytearray(p.read(e))
    before = (struct.unpack_from("<I", d, 12)[0],) + struct.unpack_from("<HH", d, 28)
    struct.pack_into("<I",  d, 12, cn_size)      # dataSize
    struct.pack_into("<HH", d, 28, cn_w, cn_h)   # w, h
    p.replace_body_appended(e, bytes(d))
    after = (struct.unpack_from("<I", d, 12)[0],) + struct.unpack_from("<HH", d, 28)
    print("  %-14s 描述符 %s -> %s" % (nm, before, after))
p.save(PEGS)
print("  已保存, md5 =", md5f(PEGS))

# ---------------------------------------------------------------- 5 回读校验
print("\n=== 回读校验 ===")
c2 = Vpp(COMMON)
for nm in TARGETS:
    h = hashlib.md5(c2.read(c2.find(nm, "vf3_pc"))).hexdigest()
    assert h == hashlib.md5(cn_vf3).hexdigest(), nm
print("  common   vf3  : OK")
t2 = Vpp(TEX)
for nm in TARGETS:
    h = hashlib.md5(t2.read(t2.find(nm))).hexdigest()
    assert h == hashlib.md5(cn_atlas).hexdigest(), nm
print("  textures 图集 : OK")
p2 = Vpp(PEGS)
for nm in TARGETS:
    d = p2.read(p2.find(nm))
    assert struct.unpack_from("<I", d, 12)[0] == cn_size
    assert struct.unpack_from("<HH", d, 28) == (cn_w, cn_h)
print("  pegs 描述符   : OK")
print("\n条目完整性抽查:", len(c2.entries()), len(t2.entries()), len(p2.entries()))
print("\n=== 完成 ===")
