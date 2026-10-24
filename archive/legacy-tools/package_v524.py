# -*- coding: utf-8 -*-
"""
打「地名与术语修正（第2批）」补丁包
基底 = v523(af27de34) + v524(b654cb3c)
只含 patch.vpp_pc + 回滚件 + 说明
"""
import os, hashlib, zipfile, datetime

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
STAMP = datetime.date.today().strftime("%Y%m%d")

FIXED  = os.path.join(GAME, "patch.vpp_pc")
BEFORE = FIXED + ".v523bak"
OUTDIR = r"F:\sr2-cn\_发布包"
NAME = "黑道圣徒2简体汉化_地名与术语修正2_%s" % STAMP
OUT = os.path.join(OUTDIR, NAME + ".zip")

M_FIXED  = "b654cb3cfd5020dbdf28f94cae671191"
M_BEFORE = "af27de344ca40a28a4fb5895569aad70"

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
assert len(d) == 304, "差异字节数异常（预期 304），停止打包"
print("✓ 差异符合预期（304 字节 / 65 条记录）")

README = """黑道圣徒2 简体汉化 —— 地名与术语修正补丁（第2批）
========================================

【本补丁内容】
只改中文文本的字词，不改任何数据结构。
共修正 65 条记录 / 304 字节，文件大小完全不变。

一、有货必达 -> 有货即达   3 条
      "必达"（必定达到）改为 "即达"（即刻达成），更贴合任务语义。

二、市中心 -> 主城区    27 条
      英文原串是 Downtown（不是 City Center），因此译作"主城区"更贴合。
      涉及地图地名、任务等级后缀、解救/烈焰冲锋等活动的区域标注、
      主城区拆车厂 / 火车站 / 阁楼公寓，以及教程长句。

三、郊区 -> 城郊        33 条
      全表替换，包括地图地名与教程叙述。
      例：城郊码头 / 城郊 - 墓地 / 在城郊拓展区最容易找到。

四、年龄档「旧」->「老」   2 条
      「旧」是 old 的误译，年龄档应作"老"。
      ★ 该字符串在表里有两条独立记录，两条都已修正；
        只改一条会导致看不到效果。
      以下用"旧"的词句一律未动（改了就不通顺）：
        旧酒吧 / 依旧逍遥法外 / 移除旧曲目 / 移除旧播放列表 /
        怀旧 / 旧肉类加工厂 / 洗去旧纹身

【未改动的内容】
common.vpp_pc / textures.vpp_pc / SR2_pc.exe / DFEngine.dll / DLC 文件
全部保持原样。本补丁只在 patch.vpp_pc 上做等长字词替换。

【已知遗留】
  5 处「市中心区」保持原样未改。
    原因：「市中心区」是 4 个字，改成"主城区"只有 3 个字，属于变短，
    需要重建 VPP 数据区，风险较高；若为保持等长写成"主城区区"则是叠字，
    读起来不通顺。为安全起见这 5 处保持原样：
      · Varsity 深受高中橄榄球队那帮人欢迎，在市中心区最容易找到。
      · Wellington 在市中心区最容易找到。
      · 市中心区
      · 坚固。霸气。有钱。Titan 最容易在市中心区找到。
      · 这款经久不衰的 Hammerhead 设计经典，在市中心区最容易找到。
    若希望一并修改，需要允许变长写入，请另行告知。

【安装方法】
把 patch.vpp_pc 复制到游戏目录覆盖同名文件即可
（通常是 C:\\Program Files (x86)\\Steam\\steamapps\\common\\Saints Row 2\\）。

★ 覆盖前请先把自己现有的 patch.vpp_pc 改名备份一份。

【回滚方法】
本包里 _回滚用_patch_修正前.bak 就是修正前的原文件
（含拆车厂崩溃修复 + 第1批用语修正），想撤销时改名回 patch.vpp_pc 覆盖回去即可。

【重要提醒】
★ 不要在 Steam 里点"验证文件完整性"！
  那样会把 patch.vpp_pc 还原成官方原版，汉化全部丢失。
★ 本补丁是叠在「拆车厂崩溃修复版 + 第1批用语修正版」之上的。

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
