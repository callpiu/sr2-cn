# -*- coding: utf-8 -*-
"""
整合修复包（v407 -> v531，共 11 项）
基底 = v407(beforescrapyardfix.bak) + v530(ead5dcf2)
"""
import os, hashlib, zipfile, datetime

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
STAMP = datetime.date.today().strftime("%Y%m%d")

FIXED  = os.path.join(GAME, "patch.vpp_pc")
BEFORE = FIXED + ".beforescrapyardfix.bak"
OUTDIR = r"F:\sr2-cn\_发布包"
NAME = "黑道圣徒2简体汉化_整合修复包_11项_%s" % STAMP
OUT = os.path.join(OUTDIR, NAME + ".zip")

M_FIXED  = "7a30500e82435e4e28d8b1f84cd98052"
M_BEFORE = "b430930fd03a2106e7fa810722ab2f29"

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
assert len(d) == 978, "差异字节数异常（预期 978），停止打包"
print("OK 差异符合预期（978 字节 / 11 项修复全集）")

README = """黑道圣徒2 简体汉化 —— 整合修复包（v407 -> v531，共 11 项）
========================================================

本包把从 2026-10-11 起对 patch.vpp_pc 的全部修复整合为一份，
覆盖以下 10 项。文件大小完全不变（仅等长槽值替换）。

【1 拆车厂崩溃修复】
  2 条任务提示的占位符顺序错误导致读取越界崩溃，修正顺序。

【2 专名修正（5 组，13 条）】
  七圣集结 / Rounds 广场购物商城 / 新亨内凯娱乐天地 /
  斯蒂尔沃特大学学生楼 / 开始兄弟帮任务

【3 用语统一（105 条）】
  "赚到"79 处、"计分"25 处、"赚到分数"1 处 等统一。

【4 地名与术语（65 条）】
  有货即达 / 主城区 / 城郊 / 老 -> 旧 等。

【5 地名双「区」修复（33 条）】
  地图界面在部分地名后强制加"区"，把尾部"区"改空格避免重复。

【6 地名改名（4 条）】
  圣徒街 -> 圣徽街（仅地图地名）。

【7 任务列表兄弟帮（8 条）】
  任务列表条目名"兄弟会任务 N" -> "兄弟帮任务 N"。

【8 枪械/弹药改名（10 条）】
  霰弹枪 -> 散筒枪（3 条，字表缺"丸"）；
  子弹 -> 火料（7 条，字表缺"铳"）。
  ★ 字表共 2795 字，缺"丸/铳"，加字需改字体图集（此前试 5 次未成），
    故改用字表内已有的常用字。长句里的旧词有意保留。

【9 帮派名兄弟帮（5 条）】
  界面单独显示的"兄弟会" -> "兄弟帮"（报纸/任务完成界面等）。

【10 武器店分类投掷类（2 条）】
  "已扔出" -> "投掷类"（原英文 Thrown 误译）。

【11 等候主机玩家（1 条）】
  据点/任务完成界面"等待主机玩家" -> "等候主机玩家"。

【未统一的部分（如需统一请告知）】
  · 圣徽街：仅改地图地名，界面提示串仍是"圣徒街"
  · 兄弟帮：任务列表+界面改了，剧情台词/成员称呼等 139 条仍是"兄弟会"
  · 散筒枪/火料：仅改武器列表条目名与 HUD 标签，说明文字仍是"霰弹枪/子弹"

common.vpp_pc / textures.vpp_pc / SR2_pc.exe / DFEngine.dll / DLC 文件
全部保持原样。

【安装方法】
把 patch.vpp_pc 复制到游戏目录覆盖同名文件即可
（通常是 C:\\Program Files (x86)\\Steam\\steamapps\\common\\Saints Row 2\\）。

★ 覆盖前请先把自己现有的 patch.vpp_pc 改名备份一份。

【回滚方法】
本包里 _回滚用_patch_修正前.bak 就是 v407（全部修复之前的原始状态），
想撤销全部 10 项时改名回 patch.vpp_pc 覆盖回去即可。

【重要提醒】
★ 不要在 Steam 里点"验证文件完整性"！那会把 patch.vpp_pc 还原成
  官方原版，汉化全部丢失（含本包修复）。

【文件清单】
见 FILELIST.txt
"""

fl = [
  "patch.vpp_pc,%d,%s,%s" % (len(b), M_FIXED, "修正后的汉化主包（v531）"),
  "FILELIST.txt,-,自身,校验清单",
  "README.txt,-,%s,本说明" % hashlib.md5(README.encode("utf-8")).hexdigest(),
  "_回滚用_patch_修正前.bak,%d,%s,%s" % (len(a), M_BEFORE, "v407 原文件（回滚用）"),
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
