# -*- coding: utf-8 -*-
"""
打「任务列表兄弟会→兄弟帮」补丁包
基底 = v526(e7821a0a) + v527(602587cf)
"""
import os, hashlib, zipfile, datetime

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
STAMP = datetime.date.today().strftime("%Y%m%d")

FIXED  = os.path.join(GAME, "patch.vpp_pc")
BEFORE = FIXED + ".v526bak"
OUTDIR = r"F:\sr2-cn\_发布包"
NAME = "黑道圣徒2简体汉化_任务列表兄弟帮补丁_%s" % STAMP
OUT = os.path.join(OUTDIR, NAME + ".zip")

M_FIXED  = "602587cf0f72384cb1789be1803a4f51"
M_BEFORE = "e7821a0aa4aee392458574896f26267e"

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
assert len(d) == 16, "差异字节数异常（预期 16），停止打包"
print("✓ 差异符合预期（16 字节 / 8 条记录）")

README = """黑道圣徒2 简体汉化 —— 任务列表「兄弟会」改「兄弟帮」补丁
========================================

【改动内容】
把任务列表里的条目名「兄弟会任务 N」改为「兄弟帮任务 N」，共 8 条记录。
仅替换 1 个字（会 -> 帮），等长替换，文件大小完全不变。

改动位置（static_CH 表）：
  @0x229F2  兄弟会任务 11  -> 兄弟帮任务 11
  @0x22CD4  兄弟会任务 11  -> 兄弟帮任务 11
  @0x319E0  兄弟会任务 2   -> 兄弟帮任务 2
  @0x3F458  兄弟会任务 11  -> 兄弟帮任务 11
  @0x446E8  兄弟会任务 11  -> 兄弟帮任务 11
  @0x45FEA  兄弟会任务 10  -> 兄弟帮任务 10
  @0x49840  兄弟会任务 11  -> 兄弟帮任务 11
  @0x63D4C  兄弟会 任务6   -> 兄弟帮 任务6

这些条目在英文原表里是 The Brotherhood Mission 2 / 6 / 10 / 11，
中文「兄弟会任务 N」是它的直译。任务 11 有 5 条独立记录（游戏里对应
多个任务节点），已全部修改。

【未改动的内容】
表里另有 144 条含「兄弟会」的记录，按需求本次不改，包括：
  · 帮派介绍与剧情叙述、任务目标描述
  · 嘲讽 / 赞语、车辆、性格、配乐等解锁项名称
  · 通缉度（兄弟会通缉度）、恶名降低、据点（开始兄弟会据点）
  · 成员称呼（兄弟会成员、兄弟会副手、兄弟会帮派成员）
  · 欢迎加入兄弟会
  · 上一批已改的「开始兄弟帮任务」保持不变
★ 因此游戏里会出现「任务列表写兄弟帮、其它界面写兄弟会」的情况。
  若希望全表统一为「兄弟帮」，改法告知即可。

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
★ 本补丁是叠在「拆车厂崩溃修复 + 前四批用语与地名修正」之上的。

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
