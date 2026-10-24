# -*- coding: utf-8 -*-
# 修复：把 common.vpp_pc 里 fnt_body_n 的 vf3 换成 fnt_chinese 的 vf3（N=2795）
# 做法：把 fnt_chinese.vf3 的数据追加到 vpp 末尾，重指 fnt_body_n 条目的 offset/size
import sys, os, struct, shutil, hashlib
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
COMMON = os.path.join(G, "common.vpp_pc")
PATCH = os.path.join(G, "patch.vpp_pc")
BAK = r"F:/sr2-cn/_backup_FONT/common.vpp_pc.before_bodyvf3"
OUT = r"F:/sr2-cn/_FIX/common_bodyvf3.vpp_pc"

# 1) 取 fnt_chinese.vf3 数据（从 patch.vpp_pc，与 common 里的应一致）
pv = Vpp(PATCH)
ce = pv.find("fnt_chinese", "vf3_pc")
chi = pv.read(ce)
print("fnt_chinese.vf3 = %d B  md5=%s" % (len(chi), hashlib.md5(chi).hexdigest()[:12]))

# 2) 读 common.vpp_pc
cv = Vpp(COMMON)
raw = bytearray(open(COMMON, "rb").read())
print("common.vpp_pc = %d B" % len(raw))

# 3) 定位数据区末尾（所有条目 body+size 的最大值）
maxend = 0
for e in cv.entries():
    end = e["body"] + e["size"]
    if end > maxend:
        maxend = end
print("数据区末尾 = %d（文件大小 %d）" % (maxend, len(raw)))

# 4) 对齐到 2048（vpp 常见对齐），追加数据
align = 2048
newoff = (maxend + align - 1) // align * align
if newoff + len(chi) > len(raw):
    raw.extend(b"\x00" * (newoff + len(chi) - len(raw)))
raw[newoff:newoff + len(chi)] = chi
print("追加 fnt_chinese.vf3 @ offset %d" % newoff)

# 5) 修改 fnt_body_n 条目
be = cv.find("fnt_body_n", "vf3_pc")
if not be:
    raise SystemExit("找不到 fnt_body_n.vf3_pc")
# 条目结构（28字节）：[name_off u32][ext_off u32][body i32][size i32][? i32][? i32]...
# 从 entries() 已知 body 在 entry_off+8，size 在 entry_off+12
eo = be["entry_off"]
old_body, old_size = struct.unpack_from("<ii", raw, eo + 12)
print("fnt_body_n 原条目: body=%d size=%d" % (old_body, old_size))
struct.pack_into("<ii", raw, eo + 12, newoff - cv.ds, len(chi))
print("fnt_body_n 新条目: body=%d(相对ds) size=%d  ds=%d" % (newoff - cv.ds, len(chi), cv.ds))

# 6) 更新 container_size（文件头偏移 0x0C 附近，结构见 Vpp 类）
# Vpp 头：[?][?][num u32][data_start u32][container_size u32]...
# 保守做法：重写 num/数据偏移后，把 container_size 设为新文件长度
# 先看头部
print("\n文件头前 32 字节:", raw[:32].hex(" "))
num, ds = struct.unpack_from("<II", raw, 4)
print("num=%d data_start=%d" % (num, ds))

os.makedirs(os.path.dirname(BAK), exist_ok=True)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
if not os.path.exists(BAK):
    shutil.copy2(COMMON, BAK)
    print("\n已备份 common.vpp_pc ->", BAK)
open(OUT, "wb").write(bytes(raw))
print("输出:", OUT, " md5=", hashlib.md5(bytes(raw)).hexdigest())

# 7) 验证：新文件里 fnt_body_n 读出来 == fnt_chinese.vf3
nv = Vpp(OUT)
ne = nv.find("fnt_body_n", "vf3_pc")
nd = nv.read(ne)
print("\n验证：新 fnt_body_n.vf3 = %d B  与 fnt_chinese 相同 = %s" % (
    len(nd), nd == chi))
N, = struct.unpack_from("<I", nd, 8)
print("新 N =", N, "（原为 224）")
