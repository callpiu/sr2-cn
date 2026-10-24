# -*- coding: utf-8 -*-
"""
打「地名双区修复」补丁包
基底 = v524(b654cb3c) + v525(8fa4cf3d)
"""
import os, hashlib, zipfile, datetime

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
STAMP = datetime.date.today().strftime("%Y%m%d")

FIXED  = os.path.join(GAME, "patch.vpp_pc")
BEFORE = FIXED + ".v524bak"
OUTDIR = r"F:\sr2-cn\_发布包"
NAME = "黑道圣徒2简体汉化_地名双区修复补丁_%s" % STAMP
OUT = os.path.join(OUTDIR, NAME + ".zip")

M_FIXED  = "8fa4cf3d88249de25addcfb9e2ac4e2b"
M_BEFORE = "b654cb3cfd5020dbdf28f94cae671191"

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
assert len(d) == 66, "差异字节数异常（预期 66），停止打包"
print("✓ 差异符合预期（66 字节 / 33 条记录）")

README = """黑道圣徒2 简体汉化 —— 地名双「区」修复补丁
========================================

【问题】
在暂停菜单的地图界面，地名后面会被游戏自动加一个「区」字，
而部分中文地名本身已经带了「区」，于是显示成：
    前往 住宅区 区
    前往 老城 区
提示格式串「前往[format][color:teal]%ls 区[/format]」也会追加「区」。

【方案】
只改地名本身：把末尾的「区」换成一个空格（等长替换）。
游戏追加的「区」正好补上，界面显示成：
    前往 住宅  区
偏移表 / 桶表零改动，容器长度不变，不会崩溃。

【改动清单】共 33 条记录 / 66 字节

  英文自带 District（原译带「区」合理，但会重复）：
    工厂区 / 红灯区 / 酒店码头区 / 码头区 / 拖车公园区 /
    巴里奥区 / Barrio 区 / 市中心区 / 娱乐区 /
    斯蒂尔沃特核厂区 / 码头区/博物馆区 / 主城区

  英文不带 District（本就不该有「区」）：
    棚户区(Projects) / 大学区(University) / 住宅区(Residential) /
    工业区(Industrial) / 老城区(Old Town) / 城郊(Suburbs) /
    城郊扩建区(Suburbs Expansion) / 街区(Hoods)x4 /
    未知街区 / 控制街区 / 兄弟街区(Frat Row)

  ★ 其中「主城区」与「城郊」是上一批（第2批）修正时引入的，
    末字同样是「区」，本补丁一并修正。

【未改动的内容】
句子里带「区」的一律不动（它们的「区」是句内成分，界面追加的「区」
只跟在孤立地名后面）：
    正在进入禁区 / 正在离开禁区 / 第 9 区 / 竞技场，贫民区 / 返回市区
复合地名也不动（如「城郊码头」「主城区拆车厂」），它们不占用
地图地名的槽位。

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
★ 本补丁是叠在「拆车厂崩溃修复版 + 前两批用语修正」之上的。

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
