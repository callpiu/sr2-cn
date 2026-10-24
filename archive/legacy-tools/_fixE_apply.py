# -*- coding: utf-8 -*-
"""
修复 E：把汉化字体图集写入 textures.vpp_pc（原地等长，安全版）

根因（由 SR2_pc.exe 反汇编 + DFEngine.dll PDB 符号双重确认）：
  语言全局 0xE8C470 = 13(CH) ⇒ 0x51D408: mov ecx,0xDE0FD0("fnt_chinese")
  ⇒ 引擎加载 common.vpp_pc 的 fnt_chinese.vf3_pc 作为字形表，
    而字形图片(atlas)来自 textures.vpp_pc 的 fnt_chinese。
  但 charlist_CH(2795) 与所有 .le_strings 的 slot 都是按
  patch.vpp_pc/fnt_chinese.g_peg_pc（汉化图集，md5 34034076…）排布的。
  ⇒ 坐标一致、图集错配 ⇒ 每个字都画成别的字（任/璨/偶/巧…）。
  唯一解：让 texts 里的图集变成汉化版。
"""
import sys, os, struct, hashlib, shutil
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

GAME   = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
TEX    = os.path.join(GAME, "textures.vpp_pc")
PATCH  = os.path.join(GAME, "patch.vpp_pc")
COMMON = os.path.join(GAME, "common.vpp_pc")
BAKDIR = r"F:\sr2-cn\_backup_E"
os.makedirs(BAKDIR, exist_ok=True)

def md5f(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()

# ---- 1. 取汉化图集（patch.vpp_pc 里的 g_peg_pc）----
vp = Vpp(PATCH)
han = vp.read(vp.find("fnt_chinese", "g_peg_pc"))
han_md5 = hashlib.md5(han).hexdigest()
print("[1] 汉化图集 md5 %s  size %d" % (han_md5, len(han)))

# ---- 2. 校验 texts 当前图集 ----
vt = Vpp(TEX)
ent = next(x for x in vt.entries() if x['name'] == 'fnt_chinese')
cur = vt.read(ent)
cur_md5 = hashlib.md5(cur).hexdigest()
print("[2] texts 当前图集 md5 %s  size %d" % (cur_md5, len(cur)))

assert len(han) == len(cur) == ent['size'], "长度不一致，无法原地覆盖"

if cur_md5 == han_md5:
    print("    已修复，无需改动")
    sys.exit(0)

# ---- 3. 备份（带时间戳，绝不覆盖已有备份）----
import time
ts = time.strftime("%Y%m%d_%H%M%S")
bak = os.path.join(BAKDIR, "textures.official_%s.vpp_pc" % ts)
if not os.path.exists(bak):
    shutil.copy2(TEX, bak)
print("[3] ✓ 备份 -> %s  md5 %s" % (bak, md5f(bak)))

# ---- 4. 原地等长覆盖 ----
off = vt.data_start + ent['body']
vt.data[off:off + len(han)] = han
vt.data[off:off + len(han)] = han
vt.save(TEX)
print("[4] ✓ 已写入 %s" % TEX)

# ---- 5. 校验 ----
v2 = Vpp(TEX)
e2 = next(x for x in v2.entries() if x['name'] == 'fnt_chinese')
new = v2.read(e2)
new_md5 = hashlib.md5(new).hexdigest()
print("[5] 新图集 md5 %s  (期望 %s)  %s" % (
    new_md5, han_md5, "OK" if new == han else "FAIL"))
assert new == han, "覆盖失败"

# ---- 6. 渲染验证：用 common.vpp_pc 的 vf3(2838) 坐标 + 新图集，画 REC1 的字符串 ----
cl = [int(s) for s in vp.read(vp.find("charlist_CH", "txt")).decode('utf-8').split('\n')
      if s.strip().isdigit()]
c2s = {}
for i, cp in enumerate(cl):
    if cp >= 0x100:
        c2s.setdefault(chr(cp), i + 0x20)

vc = Vpp(COMMON)
ec = vc.find("fnt_chinese", "vf3_pc")
co = vc.data_start + ec['body']
uoff = struct.unpack_from('<i', vc.data, co + 0xB8)[0]   # 0xAF6C
voff = struct.unpack_from('<i', vc.data, co + 0xB4)[0]   # 0xDB18
def cuv(i):
    return (struct.unpack_from('<i', vc.data, co + uoff + i*4)[0],
            struct.unpack_from('<i', vc.data, co + voff + i*4)[0])

_, alp = dxt3_decode(new, 2048, 2048)
target = "你的弟兄们需要你的保护"
print("\n[6] 用【common vf3 + 新图集】渲染 '%s'：" % target)
ok = 0
for ch in target:
    s = c2s.get(ch)
    if s is None:
        print("   %r 不在字表" % ch); continue
    U, V = cuv(s - 0x20)
    ink = int((alp[V:V+31, U:U+31] > 8).sum())
    print("   %r slot=%-5d idx=%-5d U/V=(%d,%d) 墨迹=%d" % (ch, s, s-0x20, U, V, ink))
print("\n✓ 修复 E 已应用（原地覆盖，未改文件大小）")
