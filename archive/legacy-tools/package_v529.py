# -*- coding: utf-8 -*-
"""
打「帮派名兄弟会→兄弟帮」补丁包（界面显示用）
基底 = v528(503946b4) + v529(92de2f2e)
"""
import os, hashlib, zipfile, datetime

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
STAMP = datetime.date.today().strftime("%Y%m%d")

FIXED  = os.path.join(GAME, "patch.vpp_pc")
BEFORE = FIXED + ".v528bak"
OUTDIR = r"F:\sr2-cn\_发布包"
NAME = "黑道圣徒2简体汉化_帮派名兄弟帮补丁_%s" % STAMP
OUT = os.path.join(OUTDIR, NAME + ".zip")

M_FIXED  = "92de2f2e6916a382823f0edab284f725"
M_BEFORE = "503946b452c043f34345e0fcd941df30"

def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

for p, exp, tag in ((FIXED, M_FIXED, "修正版 patch"), (BEFORE, M_BEFORE, "修正前 patch")):
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
assert len(d) == 10, "差异字节数异常（预期 10），停止打包"
print("✓ 差异符合预期（10 字节 / 5 条记录）")

README = """黑道圣徒2 简体汉化 —— 帮派名「兄弟会」改「兄弟帮」补丁
========================================

【改动内容】
把界面上单独显示的帮派名「兄弟会」改为「兄弟帮」，共 5 条记录。
仅替换 1 个字（会 -> 帮），等长替换，文件大小完全不变。

改动位置（static_CH 表，5 条彼此独立的记录）：
  @0x13542   @0x266EC   @0x2E908   @0x44CEA   @0x603F0

这 5 条是游戏中"只显示帮派名本身"的位置，覆盖：
  · 报纸界面（黄色大字标题，如"兄弟伙 / 第一印象"）
  · 任务完成界面
  · 帮派相关的界面标签

【为什么整段只改 5 条】
  磁盘上"整串恰为『兄弟会』"的记录共 5 条，而英文表里整串
  "The Brotherhood" 只有 3 条 —— 两边数量不对应，无法从数据反推
  界面具体读哪几条，因此按用户确认：5 条全改。
  若改后仍有界面显示"兄弟会"，请告知具体位置。

【未改动的内容】
表里另有 139 条含「兄弟会」的记录，按需求本次不改，包括：
  · 剧情叙述与台词
  · 兄弟会成员 / 副手 / 帮派成员 等称呼
  · 兄弟会通缉度 / 恶名降低 / 据点
  · 嘲讽、赞语、性格
  · 兄弟会配乐 / 近战 / 车辆
  · 欢迎加入兄弟会
  · 击杀兄弟会成员数 等统计项
★ 因此游戏里会出现"界面标题写兄弟帮、说明文字仍写兄弟会"的情况。
  若希望全表统一，改法告知即可。

common.vpp_pc / textures.vpp_pc / SR2_pc.exe / DFEngine.dll / DLC 文件
全部保持原样。

【安装方法】
把 patch.vpp_pc 复制到游戏目录覆盖同名文件即可
（通常是 C:\\Program Files (x86)\\Steam\\steamapps\\common\\Saints Row 2\\）。

★ 覆盖前请先把自己现有的 patch.vpp_pc 改名备份一份。

【回滚方法】
本包里 _回滚用_patch_修正前.bak 就是修正前的原文件，想撤销时
改名回 patch.vpp_pc 覆盖回去即可。

【重要提醒】
★ 不要在 Steam 里点"验证文件完整性"！那会把 patch.vpp_pc 还原成
  官方原版，汉化全部丢失。
★ 本补丁是叠在「拆车厂崩溃修复 + 前六批用语与地名修正」之上的。

【文件清单】
见 FILELIST.txt
"""

fl = [
  "patch.vpp_pc,%d,%s,%s" % (len(b), M_FIXED, "修正后的汉化主包"),
  "FILELIST.txt,-,自身,校验清单",
  "README.txt,-,%s,本说明" % hashlib.md5(README.encode("utf-8")).hexdigest(),
  "_回滚用_patch_修正前.bak,%d,%s,%s" % (len(a), M_BEFORE, "修正前原文件（回滚用）"),
]
FILELIST = "文件名,大小(bytes),md5,说明\n" + "\n".join(fl) + "\n"

os.makedirs(OUTDIR, exist_ok=True)
if os.path.exists(OUT):
    os.remove(OUT)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    z.writestr("README.txt", README.encode("utf-8"))
    z.writestr("FILELIST.txt", FILELIST.encode("utf-8"))
    z.write(FIXED, "patch.vpp_pc")
    z.write(BEFORE, "_回滚用_patch_修正前.bak")

print()
print("OK 完成:", OUT)
print("   大小: {:,} bytes".format(os.path.getsize(OUT)))
print("   md5  :", md5(OUT))
