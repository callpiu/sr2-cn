# -*- coding: utf-8 -*-
"""
打「地名改名」补丁包（圣徒街 -> 圣徽街）
基底 = v525(8fa4cf3d) + v526(e7821a0a)
"""
import os, hashlib, zipfile, datetime

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
STAMP = datetime.date.today().strftime("%Y%m%d")

FIXED  = os.path.join(GAME, "patch.vpp_pc")
BEFORE = FIXED + ".v525bak"
OUTDIR = r"F:\sr2-cn\_发布包"
NAME = "黑道圣徒2简体汉化_地名改名补丁_圣徽街_%s" % STAMP
OUT = os.path.join(OUTDIR, NAME + ".zip")

M_FIXED  = "e7821a0aa4aee392458574896f26267e"
M_BEFORE = "8fa4cf3d88249de25addcfb9e2ac4e2b"

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
assert len(d) == 4, "差异字节数异常（预期 4），停止打包"
print("✓ 差异符合预期（4 字节 / 4 条记录）")
print("  说明：只改每条的 1 个字（徒→徽），两字码点仅低字节不同，故差异极小。")

README = """黑道圣徒2 简体汉化 —— 地名改名补丁（圣徒街 -> 圣徽街）
========================================

【改动内容】
把地图地名「圣徒街」改名为「圣徽街」，共 4 条记录。
仅替换其中 1 个字（徒 -> 徽），等长替换，文件大小完全不变。

改动位置（static_CH 表，4 条独立记录）：
  @0x2B168 / @0x3550C / @0x3D732 / @0x530EC

【为什么只有 4 条】
游戏里的地图地名是 4 条彼此独立的记录（不是一处文字被多处引用）。
全部都已改名。

【未改动的内容】
以下含有"圣徒街"的文字一律保持原样（按需求只改地图地名本身）：
  · 长句叙述，例如"或者前往圣徒街区""这肯定是 Eiswolf"。
  · 复合地名，例如：圣徒街教堂 / 圣徒街车站 / 圣徒街运河 /
    圣徒街阁楼 / 圣徒街杀手 / 圣徒街超级公寓 / 圣徒街服务器
  · 界面提示串，例如 前往[...]/返回[...] 中的"圣徒街"
共 36 条同类记录未动。若希望一并改名，请另行告知。

【兼容性说明】
"徽"字在字体字表中已存在（字表内已有 20 条记录使用该字，如"徽章"），
且与被替换的"徒"字在字表中的位置相邻但不相撞，字形坐标正常，
不会出现渲染错字。

common.vpp_pc / textures.vpp_pc / SR2_pc.exe / DFEngine.dll / DLC 文件
全部保持原样。

【安装方法】
把 patch.vpp_pc 复制到游戏目录覆盖同名文件即可
（通常是 C:\\Program Files (x86)\\Steam\\steamapps\\common\\Saints Row 2\\）。

★ 覆盖前请先把自己现有的 patch.vpp_pc 改名备份一份。

【回滚方法】
本包里 _回滚用_patch_修正前.bak 就是改名前的原文件，想撤销时
改名回 patch.vpp_pc 覆盖回去即可。

【重要提醒】
★ 不要在 Steam 里点"验证文件完整性"！那会把 patch.vpp_pc 还原成
  官方原版，汉化全部丢失。
★ 本补丁是叠在「拆车厂崩溃修复版 + 前三批用语修正」之上的。

【文件清单】
见 FILELIST.txt
"""

fl = [
  "patch.vpp_pc,%d,%s,%s" % (len(b), M_FIXED, "改名后的汉化主包"),
  "FILELIST.txt,-,自身,校验清单",
  "README.txt,-,%s,本说明" % hashlib.md5(README.encode("utf-8")).hexdigest(),
  "_回滚用_patch_修正前.bak,%d,%s,%s" % (len(a), M_BEFORE, "改名前原文件（回滚用）"),
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
