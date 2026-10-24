# -*- coding: utf-8 -*-
"""★★★ 修复 F（根治）：把 patch.vpp_pc 的 fnt_chinese.vf3_pc(2795) 覆盖进
        common.vpp_pc 的 fnt_chinese.vf3_pc(2838)。

根因（本轮彻底定位）：
  引擎加载的字体表是 common.vpp_pc/fnt_chinese.vf3_pc —— 这是一张【错误的表】：
    · 它的 U 数组是"字距/kerning"值（唯一值 307 个，最小间隔 1px），
      不是图集列坐标；
    · 它的 V 行距是 31（对），但 U 完全不对 ⇒ 每个字都取到无关格子。
  而 patch.vpp_pc/fnt_chinese.vf3_pc 的 U/V 是【标准 31px 网格坐标】
    （U/V 唯一值各 65/43 个，间隔恒为 31），与图集格完全对齐。

  实测（_E26_engine_compare.png）：
    行1 patch vf3 + patch 图集 = 你的弟兄们需要你的保护  ✅
    行2 patch vf3 + tex 图集   = 你的弟兄们需要你的保护  ✅
    行3 common vf3 + tex 图集  = 交 烬层 伟 为迫 腊 交 烬仑 E 恕  ❌（= 乱码源头）

  且两张图集已完全相同（textures 已于上一步被替换），
  ⇒ 唯一剩余差异 = vf3。

写入策略：common.vpp_pc 里该条目是独立 body。
  2795*4+... = 67268 < 68300（太小，不能直接原地覆盖，需缩短 body 并修正 VPP 索引）
  ⇒ 采用「整体重打包」：读入全部 entries，替换该条 body，重建容器。
  若条目是 VPP 里最后一条 / 后面无对齐依赖，也可以在原 body 内原地写 67268 字节
  再把该条的 size 改小（VPP 是按 size 读取的，多余字节会成为垃圾但无害）。
"""
import sys, os, struct, hashlib, shutil, time
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
COMMON = os.path.join(GAME, "common.vpp_pc")
PATCH  = os.path.join(GAME, "patch.vpp_pc")
BAKDIR = r"F:\sr2-cn\_backup_F"
os.makedirs(BAKDIR, exist_ok=True)

def md5f(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()

vp = Vpp(PATCH)
patch_vf3 = vp.read(vp.find("fnt_chinese", "vf3_pc"))
patch_atl = vp.read(vp.find("fnt_chinese", "g_peg_pc"))
print("patch vf3  size %d  md5 %s" % (len(patch_vf3), hashlib.md5(patch_vf3).hexdigest()))

vc = Vpp(COMMON)
ent = vc.find("fnt_chinese", "vf3_pc")
old = vc.read(ent)
print("common vf3 size %d  md5 %s  (entry body@%d size=%d)" % (
    len(old), hashlib.md5(old).hexdigest(), ent['body'], ent['size']))
print("VPP: data_start=%d  num=%d  container_size=%d" % (
    vc.data_start, vc.num, vc.container_size))

# 备份
ts = time.strftime("%Y%m%d_%H%M%S")
bak = os.path.join(BAKDIR, "common.official_%s.vpp_pc" % ts)
shutil.copy2(COMMON, bak)
print("备份 -> %s  md5 %s" % (bak, md5f(bak)))

# ---- 方案：原地覆盖 + 缩短 size（VPP 只按 size 读，尾随垃圾无害）----
# 先确认该条目后面是否还有条目（若有，缩短会破坏后续条目的偏移）
ents = vc.entries()
idx = [i for i, x in enumerate(ents) if x['name'] == 'fnt_chinese' and x['ext'] == 'vf3_pc'][0]
tail = [x for x in ents if x['body'] > ent['body'] and x['body'] + x['size'] > ent['body']]
print("该条目之后是否还有 body 与之重叠的条目:", len(tail))

body_off = vc.data_start + ent['body']
assert ent['body'] + ent['size'] <= len(vc.data)
# 写入 vf3（67268 字节，比原 68300 短 1032）
PATCH_VF3 = patch_vf3
U32_OLD = (ent['name'] and 0)  # placeholder
print("\n=== 就地修正：写数据 + 改 header.size ===")
print("entry_off=%d  原 body=%d 原 size=%d" % (ent['entry_off'], ent['body'], ent['size']))

# entry header 结构（小端 u32 x7）: name_off, ext_off, ?, body, size, -1, 0
v2 = Vpp(COMMON)
eo = ent['entry_off']
hdr = list(struct.unpack_from('<7I', v2.data, eo))
print("原 header:", hdr)
assert hdr[3] == ent['body'] and hdr[4] == ent['size'], "entry 结构假设不符"

body_off = v2.data_start + ent['body']
# ① 写入 patch 的 vf3
v2.data[body_off:body_off + len(PATCH_VF3)] = PATCH_VF3
# ② 尾部剩余清零
rest = ent['size'] - len(PATCH_VF3)
v2.data[body_off + len(PATCH_VF3):body_off + ent['size']] = b'\x00' * rest
# ③ header.size 改为新长度
struct.pack_into('<I', v2.data, eo + 4 * 4, len(PATCH_VF3))
print("新 header size =", len(PATCH_VF3), " (尾部 %d 字节清零)" % rest)

v2.save(COMMON)
print("\n✓ 已写入 %s  md5 %s" % (COMMON, md5f(COMMON)))

# ---- 校验 ----
v3 = Vpp(COMMON)
e3 = v3.find("fnt_chinese", "vf3_pc")
new = v3.read(e3)
print("[校验] 读回 size=%d  md5=%s" % (len(new), hashlib.md5(new).hexdigest()))
assert new == PATCH_VF3, "读回内容不一致"
print("[校验] ✓ common.vpp_pc 的 fnt_chinese.vf3_pc 已 == patch.vpp_pc 的版本")

# 还需确认其它条目未受影响
print("[校验] 条目总数 =", v3.num, "(应为 6166)")
assert v3.num == 6166

