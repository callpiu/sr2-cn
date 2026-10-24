# -*- coding: utf-8 -*-
"""GH18(方案C): 把 jap 字体升级为中文（vf3 + 图集 + 描述符）。

依据：
  - jap 是 exe 字体名表里排第一的字体（默认字体），N 只有 1980/1981
  - 中文槽位最高 2790 > 1980 => 越界 => 从 jap 图集取随机汉字（正是观测到的乱码）
  - jap 图集 2048x1024 (66x33=2178 格)，装不下 2795 字
  - 中文图集 2048x2048 (65x43=2795 格) 才是正确的

做法：jap 的 vf3/图集/描述符 全部换成 fnt_chinese 的。
"""
import sys, os, shutil, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
BAK = r"F:\sr2-cn\_backup_J"
os.makedirs(BAK, exist_ok=True)

def md5(b):
    return hashlib.md5(b).hexdigest()

# ---------- 取基准（中文）数据 ----------
cv = Vpp(os.path.join(G, "common.vpp_pc"))
zh_vf3 = cv.read(cv.find("fnt_chinese", "vf3_pc"))
print("中文 vf3: %d B  N=%d" % (len(zh_vf3), struct.unpack_from("<I", zh_vf3, 8)[0]))

tv = Vpp(os.path.join(G, "textures.vpp_pc"))
zh_tex = tv.read(tv.find("fnt_chinese", ""))
print("中文图集: %d B  md5=%s" % (len(zh_tex), md5(zh_tex)[:12]))

pv = Vpp(os.path.join(G, "pegs.vpp_pc"))
zh_desc = pv.read(pv.find("fnt_chinese", ""))
print("中文描述符: %d B  @0x0C=%d  %dx%d  fmt=0x%X" % (
    len(zh_desc), struct.unpack_from("<I", zh_desc, 0x0C)[0],
    struct.unpack_from("<H", zh_desc, 0x1C)[0], struct.unpack_from("<H", zh_desc, 0x1E)[0],
    struct.unpack_from("<I", zh_desc, 0x20)[0]))

# ---------- 1) common/patch 的 jap.vf3_pc ----------
for fn in ("common.vpp_pc", "patch.vpp_pc"):
    p = os.path.join(G, fn)
    b = os.path.join(BAK, fn + ".before_japfix")
    if not os.path.exists(b):
        shutil.copy2(p, b)
    v = Vpp(p)
    e = v.find("jap", "vf3_pc")
    if e:
        v.replace_body_appended(e, zh_vf3)
        v.save(p)
        print("[%s] jap.vf3_pc -> 中文 vf3  已保存" % fn)

# ---------- 2) jap 图集 (textures 的 jap + patch 的 jap.g_peg_pc) ----------
p = os.path.join(G, "textures.vpp_pc")
v = Vpp(p)
e = v.find("jap", "")
if e:
    v.replace_body_appended(e, zh_tex)
    v.save(p)
    print("[textures] jap 图集 -> 中文图集  已保存")

p = os.path.join(G, "patch.vpp_pc")
v = Vpp(p)
e = v.find("jap", "g_peg_pc")
if e:
    v.replace_body_appended(e, zh_tex)
    v.save(p)
    print("[patch] jap.g_peg_pc -> 中文图集  已保存")

# ---------- 3) pegs 的 jap 描述符 ----------
p = os.path.join(G, "pegs.vpp_pc")
v = Vpp(p)
e = v.find("jap", "")
if e:
    d = bytearray(v.read(e))
    print("[pegs] jap 描述符改前: %d B @0x0C=%d %dx%d" % (
        len(d), struct.unpack_from("<I", d, 0x0C)[0],
        struct.unpack_from("<H", d, 0x1C)[0], struct.unpack_from("<H", d, 0x1E)[0]))
    struct.pack_into("<I", d, 0x0C, 4194304)
    struct.pack_into("<H", d, 0x1C, 2048)
    struct.pack_into("<H", d, 0x1E, 2048)
    struct.pack_into("<I", d, 0x34, 4194304)
    v.replace_body_appended(e, bytes(d))
    v.save(p)
    print("[pegs] jap 描述符改后: %d B @0x0C=%d %dx%d @0x34=%d" % (
        len(d), struct.unpack_from("<I", d, 0x0C)[0],
        struct.unpack_from("<H", d, 0x1C)[0], struct.unpack_from("<H", d, 0x1E)[0],
        struct.unpack_from("<I", d, 0x34)[0]))

# ---------- 校验 ----------
print("\n=== 校验 ===")
for fn, nm, ex in (("common.vpp_pc", "jap", "vf3_pc"), ("patch.vpp_pc", "jap", "vf3_pc"),
                   ("textures.vpp_pc", "jap", ""), ("patch.vpp_pc", "jap", "g_peg_pc")):
    v = Vpp(os.path.join(G, fn))
    e = v.find(nm, ex)
    raw = v.read(e)
    extra = ""
    if ex == "vf3_pc":
        extra = " N=%d" % struct.unpack_from("<I", raw, 8)[0]
    print("  [%s] jap.%s %d B md5=%s%s" % (fn, ex, len(raw), md5(raw)[:12], extra))
v = Vpp(os.path.join(G, "pegs.vpp_pc"))
raw = v.read(v.find("jap", ""))
print("  [pegs] jap 描述符 %d B @0x0C=%d %dx%d" % (
    len(raw), struct.unpack_from("<I", raw, 0x0C)[0],
    struct.unpack_from("<H", raw, 0x1C)[0], struct.unpack_from("<H", raw, 0x1E)[0]))
