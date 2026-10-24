# -*- coding: utf-8 -*-
"""
打「用语与专名修正」补丁包
基底 = 拆车厂崩溃修复版(59db8769) + v523 用语修正(af27de34)
只含 patch.vpp_pc + 回滚件 + 说明
"""
import os, hashlib, zipfile, datetime

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
STAMP = datetime.date.today().strftime("%Y%m%d")

FIXED = os.path.join(GAME, "patch.vpp_pc")
BEFORE = FIXED + ".v522bak"          # = 拆车厂修复版 59db8769
OUTDIR = r"F:\sr2-cn\_发布包"
NAME = "黑道圣徒2简体汉化_用语与专名修正补丁_%s" % STAMP
OUT = os.path.join(OUTDIR, NAME + ".zip")

M_FIXED = "af27de344ca40a28a4fb5895569aad70"
M_BEFORE = "59db87697208f6f404d03278b6b0c4cd"

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
assert len(d) == 440, "差异字节数异常（预期 440），停止打包"
print("✓ 差异符合预期（440 字节 / 118 条记录）")

README = """黑道圣徒2 简体汉化 —— 用语与专名修正补丁
========================================

【本补丁内容】
只改中文文本的字词与专有名词，不改任何数据结构。
共修正 118 条记录 / 440 字节，文件大小完全不变。

一、专有名词（全表替换，原词已清零）
  圣徒七人              -> 七圣集结            4 处
  Rounds 广场购物中心     -> Rounds 广场购物商城   4 处
  新亨内凯娱乐中心        -> 新亨内凯娱乐天地      2 处
  斯蒂尔沃特大学学生会    -> 斯蒂尔沃特大学学生楼  2 处
  开始兄弟会任务          -> 开始兄弟帮任务        1 处

二、用语统一
  获得 -> 赚到   79 条
      仅限「金钱 / 现金 / 声望」语境。例：
        从爆头获得的声望      -> 从爆头赚到的声望
        累计获得现金          -> 累计赚到现金
        按要求完成刺杀将获得现金奖励 -> ...将赚到现金奖励
      以下搭配保持原样（改了就不通顺）：
        已获得奖牌 / 获得分数 / 获得风格点数 / 获得成就 / 获得道具 …

  得分 -> 计分   25 条
      仅限 HUD 与标签的短串。例：
        得分上限       -> 计分上限
        我的得分       -> 我的计分
        前往得分区域    -> 前往计分区域
        送车得分：      -> 送车计分：
      比赛规则与教程的长句说明保留「得分」，因为那里讲的是计分规则本身，
      改成「计分」会读不通。

【未改动的内容】
common.vpp_pc / textures.vpp_pc / SR2_pc.exe / DFEngine.dll / DLC 文件
全部保持原样。本补丁只在 patch.vpp_pc 上做等长字词替换。

【安装方法】
把 patch.vpp_pc 复制到游戏目录覆盖同名文件即可
（通常是 C:\\Program Files (x86)\\Steam\\steamapps\\common\\Saints Row 2\\）。

★ 覆盖前请先把自己现有的 patch.vpp_pc 改名备份一份。

【回滚方法】
本包里 _回滚用_patch_修正前.bak 就是修正前的原文件
（内含拆车厂崩溃修复），想撤销时改名回 patch.vpp_pc 覆盖回去即可。

【重要提醒】
★ 不要在 Steam 里点"验证文件完整性"！
  那样会把 patch.vpp_pc 还原成官方原版，汉化全部丢失。
★ 本补丁是建立在「拆车厂崩溃修复版」之上的。
  如果你的 patch.vpp_pc 里没有那个修复，请先向我要拆车厂修复补丁。

【文件清单】
见 FILELIST.txt
"""

fl = ["patch.vpp_pc,%d,%s,%s" % (len(b), M_FIXED, "修正后的汉化主包")]
fl.append("FILELIST.txt,-,自身,校验清单")
fl.append("README.txt,-,%s,本说明" % hashlib.md5(README.encode("utf-8")).hexdigest())
fl.append("_回滚用_patch_修正前.bak,%d,%s,%s" % (len(a), M_BEFORE, "修正前原文件（回滚用）"))
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
