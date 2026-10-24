# -*- coding: utf-8 -*-
"""
打「枪械与弹药改名」补丁包
基底 = v527(602587cf) + v528(503946b4)
"""
import os, hashlib, zipfile, datetime

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
STAMP = datetime.date.today().strftime("%Y%m%d")

FIXED  = os.path.join(GAME, "patch.vpp_pc")
BEFORE = FIXED + ".v527bak"
OUTDIR = r"F:\sr2-cn\_发布包"
NAME = "黑道圣徒2简体汉化_枪械弹药改名补丁_%s" % STAMP
OUT = os.path.join(OUTDIR, NAME + ".zip")

M_FIXED  = "503946b452c043f34345e0fcd941df30"
M_BEFORE = "602587cf0f72384cb1789be1803a4f51"

def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

for p, exp, tag in ((FIXED, M_FIXED, "改名版 patch"), (BEFORE, M_BEFORE, "改名前 patch")):
    assert os.path.exists(p), "%s 不存在: %s" % (tag, p)
    got = md5(p)
    assert got == exp, "%s md5 不符: %s != %s" % (tag, got, exp)
print("前置校验通过")

a = open(BEFORE, "rb").read()
b = open(FIXED, "rb").read()
assert len(a) == len(b), "大小不一致"
d = [i for i in range(len(a)) if a[i] != b[i]]
print("文件大小: %d 字节（未变）" % len(a))
print("差异字节: %d" % len(d))
assert len(d) == 40, "差异字节数异常（预期 40），停止打包"
print("✓ 差异符合预期（40 字节 / 10 条记录）")

README = """黑道圣徒2 简体汉化 —— 枪械与弹药改名补丁
========================================

【改动内容】
    霰弹枪 -> 散筒枪    3 条   （武器列表条目名）
    子弹   -> 火料      7 条   （HUD 弹药标签）
共 10 条记录 / 40 字节，文件大小完全不变。

霰弹枪改动位置（static_CH）：
  @0x1BD98   @0x29A76   @0x41E26

子弹改动位置（static_CH）：
  @0x19818   @0x37CBC   @0x407D4   @0x40FD2
  @0x4898E   @0x605CC   @0x6A952

这些是彼此独立的记录（不是一处文字被多处引用），已全部修改。


【为什么没有用「霰丸」「铳药」】
  「丸」和「铳」这两个字不在游戏的汉字表里（字表共 2795 字）。
  字表是字体渲染的依据，缺字就显示不出来。
  往字表加字需要同时改动 charlist 与字体图集（vf3 / g_peg），
  属于结构性改动，风险较高，因此改用字表里已有的字：
    散（已在 17 条记录中使用，如"遣散追随者"）
    筒（已在 5 条记录中使用，如"火箭筒""双筒望远镜"）
    火（已在 110 条记录中使用）
    料（已在 39 条记录中使用，如"有毒废料"）


【未改动的内容】
长句里出现的旧词一律保持原样（共 16 条），例如：
  · 霰弹枪弹药 / 无限霰弹枪弹药
  · 霰弹枪命中率 / 霰弹枪击杀数 / 霰弹枪射击数 / 霰弹枪死亡数
  · 短管双管霰弹枪
  · XS-2 Ultimax 霰弹枪现已在你的据点武器库中解锁。
  · 减少子弹伤害
  · 把子弹留给恶司。 / 发射 %ls 发子弹 / 你的背包里每种武器只能带一把…
★ 因此游戏里会出现「列表写散筒枪、说明文字仍写霰弹枪」的情况。
  若希望一并改名，改法告知即可。

common.vpp_pc / textures.vpp_pc / SR2_pc.exe / DFEngine.dll / DLC 文件
全部保持原样。

【安装方法】
把 patch.vpp_pc 复制到游戏目录覆盖同名文件即可
（通常是 C:\\Program Files (x86)\\Steam\\steamapps\\common\\Saints Row 2\\）。

★ 覆盖前请先把自己现有的 patch.vpp_pc 改名备份一份。

【回滚方法】
本包里 _回滚用_patch_改名前.bak 就是改名前的原文件，想撤销时
改名回 patch.vpp_pc 覆盖回去即可。

【重要提醒】
★ 不要在 Steam 里点"验证文件完整性"！那会把 patch.vpp_pc 还原成
  官方原版，汉化全部丢失。
★ 本补丁是叠在「拆车厂崩溃修复 + 前五批用语与地名修正」之上的。

【文件清单】
见 FILELIST.txt
"""

fl = [
  "patch.vpp_pc,%d,%s,%s" % (len(b), M_FIXED, "改名后的汉化主包"),
  "FILELIST.txt,-,自身,校验清单",
  "README.txt,-,%s,本说明" % hashlib.md5(README.encode("utf-8")).hexdigest(),
  "_回滚用_patch_改名前.bak,%d,%s,%s" % (len(a), M_BEFORE, "改名前原文件（回滚用）"),
]
FILELIST = "文件名,大小(bytes),md5,说明\n" + "\n".join(fl) + "\n"

os.makedirs(OUTDIR, exist_ok=True)
if os.path.exists(OUT):
    os.remove(OUT)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    z.writestr("README.txt", README.encode("utf-8"))
    z.writestr("FILELIST.txt", FILELIST.encode("utf-8"))
    z.write(FIXED, "patch.vpp_pc")
    z.write(BEFORE, "_回滚用_patch_改名前.bak")

print()
print("OK 完成:", OUT)
print("   大小: {:,} bytes".format(os.path.getsize(OUT)))
print("   md5  :", md5(OUT))
