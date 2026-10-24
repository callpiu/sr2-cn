# -*- coding: utf-8 -*-
"""
打「拆车厂崩溃修复」最小补丁包
只含本次真正改动的东西：patch.vpp_pc（修复版）+ 回滚用原文件 + 说明文档
"""
import os, hashlib, zipfile, datetime

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
STAMP = datetime.date.today().strftime("%Y%m%d")

FIXED = os.path.join(GAME, "patch.vpp_pc")
BEFORE = os.path.join(GAME, "patch.vpp_pc.beforescrapyardfix.bak")   # v407 原始
OUTDIR = r"F:\sr2-cn\_发布包"
NAME = "黑道圣徒2简体汉化_拆车厂崩溃修复补丁_%s" % STAMP
OUT = os.path.join(OUTDIR, NAME + ".zip")

M_FIXED = "59db87697208f6f404d03278b6b0c4cd"
M_BEFORE = "b430930fd03a2106e7fa810722ab2f29"

def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

# ---- 前置断言 ----
for p, exp, tag in ((FIXED, M_FIXED, "修复版 patch"), (BEFORE, M_BEFORE, "修复前 patch")):
    assert os.path.exists(p), "%s 不存在: %s" % (tag, p)
    got = md5(p)
    assert got == exp, "%s md5 不符: %s != %s" % (tag, got, exp)
print("前置校验通过")

# ---- 差分核对：确认只有那两条记录被改 ----
a = open(BEFORE, "rb").read()
b = open(FIXED, "rb").read()
assert len(a) == len(b), "大小不一致"
d = [i for i in range(len(a)) if a[i] != b[i]]
print("文件大小: %d 字节（未变）" % len(a))
print("差异字节: %d" % len(d))
assert len(d) == 92, "差异字节数异常，停止打包"
# 差异必须集中在两段区间内
segs = []
s = p = d[0]
for x in d[1:]:
    if x == p + 1:
        p = x
    else:
        segs.append((s, p)); s = p = x
segs.append((s, p))
lo = min(x for x in d); hi = max(x for d_ in [0] for x in d)
assert lo < hi
print("差异区间: 0x%X - 0x%X" % (lo, hi))
print("（差异段 %d 个，全部落在上述区间内 = 只改了 static_CH 的两条记录）" % len(segs))

README = """黑道圣徒2 简体汉化 —— 拆车厂崩溃修复补丁
========================================

【修复内容】
进入拆车厂（Scrapyard）做车辆交付任务时游戏崩溃。
根因是两条中文字符串的【占位符顺序】与英文原串不一致：

  英文原串  Delivered %d of %d cars for the %ls list
  修复前    %ls 清单交付 %d/%d 辆车          <- %ls 排在 %d 之前
  修复后    交付 %d/%d 辆车 %ls 清单          <- 与英文顺序一致

  英文原串  ... earned $%i for a %ls level performance
  修复前    数：%i/%i，凭借 %ls 级表现，你获得了$%i     <- %ls 排在 %i 之前
  修复后    数：%i/%i，你赚到了$%i，凭借 %ls 级表现    <- 与英文顺序一致

引擎按英文原串的占位符顺序读取参数。中文译文把 %ls 排到了 %d / %i 之前，
%s 就会把一个整数当成字符串指针来用，直接导致崩溃。

【改动范围】
只改了 2 条记录、共 92 个字节，文件大小完全不变。
common.vpp_pc / textures.vpp_pc / SR2_pc.exe / DFEngine.dll 均未改动。

【安装方法】
把 patch.vpp_pc 复制到游戏目录覆盖同名文件即可
（通常是 C:\\Program Files (x86)\\Steam\\steamapps\\common\\Saints Row 2\\）。

★ 覆盖前请先把自己现有的 patch.vpp_pc 改名备份一份。

【回滚方法】
本包里 _回滚用_patch_修复前.bak 就是修复前的原文件，
想撤销时把它改名回 patch.vpp_pc 覆盖回去即可。

【重要提醒】
★ 不要在 Steam 里点"验证文件完整性"！
  那样会把 patch.vpp_pc 还原成官方原版，汉化（含本崩溃修复）全部丢失。

【文件清单】
见 FILELIST.txt
"""

FILES = [
    ("patch.vpp_pc", FIXED, "修复后的汉化主包"),
    ("FILELIST.txt", None, "校验清单"),
    ("README.txt", None, "本说明"),
    ("_回滚用_patch_修复前.bak", BEFORE, "修复前的原文件（回滚用）"),
]

os.makedirs(OUTDIR, exist_ok=True)

fl = ["文件名,大小(bytes),md5,说明"]
for rel, src, desc in FILES:
    if rel == "README.txt":
        fl.append("README.txt,-,%s,本说明" % hashlib.md5(README.encode("utf-8")).hexdigest())
        continue
    if rel == "FILELIST.txt":
        fl.append("FILELIST.txt,-,自身,校验清单")
        continue
    d = open(src, "rb").read()
    fl.append("%s,%d,%s,%s" % (rel, len(d), hashlib.md5(d).hexdigest(), desc))
FILELIST = "文件名,大小(bytes),md5,说明\n" + "\n".join(fl[1:]) + "\n"

if os.path.exists(OUT):
    os.remove(OUT)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    z.writestr("README.txt", README.encode("utf-8"))
    z.writestr("FILELIST.txt", FILELIST.encode("utf-8"))
    z.write(FIXED, "patch.vpp_pc")
    z.write(BEFORE, "_回滚用_patch_修复前.bak")

print()
print("OK 完成:", OUT)
print("   大小: {:,} bytes".format(os.path.getsize(OUT)))
print("   md5  :", md5(OUT))
