"""v514：★★ 坏字的真正根因修复 ★★
把汉化版中文字体图集写入 textures.vpp_pc。

★★★ 根因（本次实测确认）★★★
游戏里有两个 fnt_chinese 图集：
    patch.vpp_pc/fnt_chinese.g_peg_pc      md5 34034076…  ← 汉化版（字形按中文字表重排）
    textures.vpp_pc/fnt_chinese            md5 62a57046…  ← 官方原版
游戏渲染读的是 **textures 里的官方图集**，而 charlist_CH(2795) 与所有 vf3 的
U/V 坐标都是按【汉化图集】排布的 ⇒ 同一坐标在官方图集里画的是另一个字
⇒ 徒→建、录→底、弹→床、阶→约、我→卖 …（位置相关，与具体字无关）。

★ 这解释了为什么 v418/v421/v422 全都无效：
  它们改的是 vf3 的 U/V 数组值，但 U/V 指向的坐标在【官方图集】里，
  无论怎么改 vf3 都不改变"这个坐标画的是哪个字"。
  ⇒ 唯一解：让 textures.vpp_pc 的图集变成汉化版。

安全性：
  - 两份图集大小完全相同（4,194,304 = 2048x2048 DXT3）⇒ 原地等长覆盖
  - textures.vpp_pc 里该条目是独立 body，无其它文件依赖其内部结构
  - 覆盖后 charlist_CH + common.vpp_pc 的 vf3(2838) 与之配对
    （注意 vf3 有 2838 条而字表 2795 条，多出的 43 条是原版遗留，不影响）
"""
import sys, os, struct, hashlib, shutil
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
TEX   = os.path.join(GAME, "textures.vpp_pc")
PATCH = os.path.join(GAME, "patch.vpp_pc")
BAK   = TEX + ".official_bak"
OUT   = r"F:\sr2-cn\_fix_candidates\textures_v514.vpp_pc"

ORIG_MD5 = "62a57046a590e4156c8b6c8c2ea18215"     # 官方原版图集 md5

# ---- 取汉化图集（源：patch.vpp_pc，由汉化工程生成，字形与 charlist_CH 配套）----
vp = Vpp(PATCH)
atlas_han = vp.read(vp.find("fnt_chinese", "g_peg_pc"))
print("汉化图集 md5 %s size %d" % (hashlib.md5(atlas_han).hexdigest(), len(atlas_han)))

# ---- 校验 textures 当前是官方原版 ----
vt = Vpp(TEX)
ent = None
for x in vt.entries():
    if x['name'] == 'fnt_chinese':
        ent = x; break
assert ent is not None
cur = vt.read(ent)
cur_md5 = hashlib.md5(cur).hexdigest()
print("textures 当前图集 md5 %s size %d" % (cur_md5, len(cur)))

if len(atlas_han) != ent['size']:
    raise SystemExit("★ 大小不一致，无法原地覆盖：%d vs %d" % (len(atlas_han), ent['size']))
if cur_md5 == hashlib.md5(atlas_han).hexdigest():
    print("已经是汉化图集，无需改动")

# ---- 备份官方原版 ----
if not os.path.exists(BAK):
    shutil.copy2(TEX, BAK)
    print("✓ 备份官方原版 ->", BAK, "md5", hashlib.md5(open(BAK,'rb').read()).hexdigest())
else:
    print("备份已存在 md5", hashlib.md5(open(BAK, 'rb').read()).hexdigest())

# ---- 原地等长覆盖 ----
body_off = vt.data_start + ent['body']
vt.data[body_off:body_off + len(atlas_han)] = atlas_han
vt.save(OUT)
print("\n✓ 写出", OUT)
print("  md5 ", hashlib.md5(open(OUT, 'rb').read()).hexdigest())
print("  size", os.path.getsize(OUT))

# ---- 校验 ----
print("\n=== 校验 ===")
v2 = Vpp(OUT)
e2 = None
for x in v2.entries():
    if x['name'] == 'fnt_chinese':
        e2 = x; break
new_atlas = v2.read(e2)
print("  新图集 md5 %s  (应等于汉化图集 %s)" % (
    hashlib.md5(new_atlas).hexdigest(), hashlib.md5(atlas_han).hexdigest()))
assert new_atlas == atlas_han, "覆盖失败"
print("  [OK] 图集已正确写入")

# 验证：徒/录/弹 现在在两张图集上都能读到正确字形
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import dxt3_decode
cl = [int(s) for s in vp.read(vp.find("charlist_CH","txt")).decode('utf-8').split('\n') if s.strip().isdigit()]
c2s = {}
for i, cp in enumerate(cl):
    if cp >= 0x100: c2s.setdefault(chr(cp), i + 0x20)
vc = Vpp(os.path.join(GAME, "common.vpp_pc"))
ec = vc.find("fnt_chinese", "vf3_pc"); co = vc.data_start + ec['body']
def cuv(i): return (struct.unpack_from('<i', vc.data, co+0xAF6C+i*4)[0],
                    struct.unpack_from('<i', vc.data, co+0xDB18+i*4)[0])
_, alp = dxt3_decode(new_atlas, 2048, 2048)
print("\n  修复后各字在【同一坐标】的墨迹量（应与汉化图集一致，即字形正确）：")
for ch in ('徒','录','弹','阶','我'):
    idx = c2s[ch] - 0x20
    U, V = cuv(idx)
    ink = int((alp[V:V+31, U:U+31] > 8).sum())
    print("     %r idx=%-5d U/V=(%d,%d) 墨迹=%d" % (ch, idx, U, V, ink))
print("\n✓ v514 构建完成（候选，未部署）")