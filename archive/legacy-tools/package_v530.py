# -*- coding: utf-8 -*-
"""
打「武器店分类 已扔出→投掷类」补丁包
基底 = v529(92de2f2e) + v530(ead5dcf2)
"""
import os, hashlib, zipfile, datetime

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
STAMP = datetime.date.today().strftime("%Y%m%d")

FIXED  = os.path.join(GAME, "patch.vpp_pc")
BEFORE = FIXED + ".v529bak"
OUTDIR = r"F:\sr2-cn\_发布包"
NAME = "黑道圣徒2简体汉化_武器分类投掷类补丁_%s" % STAMP
OUT = os.path.join(OUTDIR, NAME + ".zip")

M_FIXED  = "ead5dcf22ac724db83c470ec128df6e2"
M_BEFORE = "92de2f2e6916a382823f0edab284f725"

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
assert len(d) == 12, "差异字节数异常（预期 12），停止打包"
print("OK 差异符合预期（12 字节 / 2 条记录 × 3 字）")

README = """黑道圣徒2 简体汉化 —— 武器店分类「已扔出」改「投掷类」补丁
==============================================

【改动内容】
武器店分类标签「已扔出」改为「投掷类」，共 2 条记录。
原英文为 Thrown（投掷武器栏，放手雷/燃烧瓶等投掷物），
原译文「已扔出」是误译（像一句已完成的话，不像是分类名）。
3 字等长替换，文件大小完全不变。

改动位置（static_CH 表，2 条记录）：
  @0x1C4EB5A  (ID 6172,35166)
  @0x1C5B5EA  (ID 20823,811)

选「投掷类」的原因：
  游戏其它地方的 Thrown 都译作「投掷」
  （如「投掷武器致死次数」「从投掷击杀赚到的声望」），
  分类名统一用词。
  「投/掷/类」三字均为字表内大量使用过的常用字，渲染无风险。

【未改动的内容】
含「扔」的其它 15 条记录保持原样（如「扔烟花箱来保卫卡车」、
「（点按）扔出人质盾牌」等剧情与操作提示），它们语义正确。

common.vpp_pc / textures.vpp_pc / SR2_pc.exe / DFEngine.dll / DLC 文件
全部保持原样。

【安装方法】
把 patch.vpp_pc 复制到游戏目录覆盖同名文件即可。

★ 覆盖前请先把自己现有的 patch.vpp_pc 改名备份一份。

【回滚方法】
本包里 _回滚用_patch_修正前.bak 就是修正前的原文件，想撤销时
改名回 patch.vpp_pc 覆盖回去即可。

【重要提醒】
★ 不要在 Steam 里点"验证文件完整性"！那会把 patch.vpp_pc 还原成
  官方原版，汉化全部丢失。
★ 本补丁叠在此前全部修复（拆车厂崩溃 + 用语地名 + 圣徽街 +
  兄弟帮 + 散筒枪/火料）之上。

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
