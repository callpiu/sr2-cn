# -*- coding: utf-8 -*-
"""
打「等待主机玩家→等候主机玩家」补丁包
基底 = v530(ead5dcf2) + v531(7a30500e)
"""
import os, hashlib, zipfile, datetime

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
STAMP = datetime.date.today().strftime("%Y%m%d")

FIXED  = os.path.join(GAME, "patch.vpp_pc")
BEFORE = FIXED + ".v530bak"
OUTDIR = r"F:\sr2-cn\_发布包"
NAME = "黑道圣徒2简体汉化_等候主机玩家补丁_%s" % STAMP
OUT = os.path.join(OUTDIR, NAME + ".zip")

M_FIXED  = "7a30500e82435e4e28d8b1f84cd98052"
M_BEFORE = "ead5dcf22ac724db83c470ec128df6e2"

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
assert len(d) == 2, "差异字节数异常（预期 2），停止打包"
print("OK 差异符合预期（2 字节 / 1 条记录 1 字）")

README = """黑道圣徒2 简体汉化 —— 「等待主机玩家」改「等候主机玩家」补丁
======================================================

【改动内容】
据点/任务完成界面的联机提示「等待主机玩家」改为「等候主机玩家」，
共 1 条记录。仅替换 1 个字（待 -> 候），等长替换，文件大小不变。

改动位置（static_CH 表）：
  @0x1C640BC  (ID 20195,15179)

「候」为字表内大量使用过的常用字（128 条记录在用），渲染无风险。

【未改动的内容】
其它含「等待」的 11 条记录（等待玩家 1 / 等待更多玩家 /
正在等待服务器 / 请等待主机 等）保持原样。

common.vpp_pc / textures.vpp_pc / SR2_pc.exe / DFEngine.dll / DLC 文件
全部保持原样。

【安装方法】
把 patch.vpp_pc 复制到游戏目录覆盖同名文件即可。

★ 覆盖前请先把自己现有的 patch.vpp_pc 改名备份一份。

【回滚方法】
本包里 _回滚用_patch_修正前.bak 就是修正前的原文件（v530），
想撤销时改名回 patch.vpp_pc 覆盖回去即可。

【重要提醒】
★ 不要在 Steam 里点"验证文件完整性"！那会把 patch.vpp_pc 还原成
  官方原版，汉化全部丢失。
★ 本补丁叠在此前全部修复（v407 以来的 10 项）之上。

【文件清单】
见 FILELIST.txt
"""

fl = [
  "patch.vpp_pc,%d,%s,%s" % (len(b), M_FIXED, "修正后的汉化主包（v531）"),
  "FILELIST.txt,-,自身,校验清单",
  "README.txt,-,%s,本说明" % hashlib.md5(README.encode("utf-8")).hexdigest(),
  "_回滚用_patch_修正前.bak,%d,%s,%s" % (len(a), M_BEFORE, "v530 原文件（回滚用）"),
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
