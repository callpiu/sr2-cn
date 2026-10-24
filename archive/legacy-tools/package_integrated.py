# -*- coding: utf-8 -*-
"""
整合包：2026-10-11 14:59 - 18:16 全部修复
基线 = v407 (b430930f，用户整目录备份状态)
当前 = v526 (e7821a0a)
"""
import os, hashlib, zipfile, datetime

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
STAMP = datetime.date.today().strftime("%Y%m%d")

FIXED  = os.path.join(GAME, "patch.vpp_pc")
BEFORE = FIXED + ".beforescrapyardfix.bak"     # v407 基线
OUTDIR = r"F:\sr2-cn\_发布包"
NAME = "黑道圣徒2简体汉化_整合修复包_6项_%s" % STAMP
OUT = os.path.join(OUTDIR, NAME + ".zip")

M_FIXED  = "e7821a0aa4aee392458574896f26267e"
M_BEFORE = "b430930fd03a2106e7fa810722ab2f29"

def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

for p, exp, tag in ((FIXED, M_FIXED, "修复版 patch"), (BEFORE, M_BEFORE, "基线 patch")):
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
assert len(d) == 898, "差异字节数异常（预期 898），停止打包"
print("✓ 差异符合预期（898 字节 / 6 个修复阶段）")

README = """黑道圣徒2 简体汉化 —— 整合修复包（6 项）
========================================

本包包含 2026-10-11 14:59 至 18:16 之间的全部修复，共 6 项。
所有改动都是对 patch.vpp_pc 内中文文本的等长字词替换，
文件大小完全不变，不涉及任何数据结构改动。

基线 md5：b430930fd03a2106e7fa810722ab2f29
修复后  ：e7821a0aa4aee392458574896f26267e
差异：898 字节


【一】拆车厂崩溃修复
  进入拆车厂做车辆交付任务时崩溃。
  原因是两条中文字符串的占位符顺序与英文原串不一致，
  %ls 被排到 %d / %i 之前，引擎把整数当字符串指针用。

    击杀数：%i/%i，凭借 %ls 级表现，你获得了$%i
      -> 击杀数：%i/%i，你赚到了$%i，凭借 %ls 级表现

    已为 %ls 清单交付 %d/%d 辆车
      -> 已为交付 %d/%d 辆车 %ls 清单


【二】专有名词修正
    圣徒七人            -> 七圣集结              4 处
    Rounds 广场购物中心   -> Rounds 广场购物商城     4 处
    新亨内凯娱乐中心      -> 新亨内凯娱乐天地        2 处
    斯蒂尔沃特大学学生会  -> 斯蒂尔沃特大学学生楼    2 处
    开始兄弟会任务        -> 开始兄弟帮任务          1 处
  其中「斯蒂尔沃特大学学生会」在表里有两条独立记录，两条都已修正，
  只改一条会看不到效果。


【三】用语统一
  获得 -> 赚到   79 条
      只改金钱 / 现金 / 声望语境。例：
        从爆头获得的声望   -> 从爆头赚到的声望
        累计获得现金       -> 累计赚到现金
      以下搭配保持原样（改了就不通顺）：
        已获得奖牌 / 获得奖牌 / 获得成就 / 获得道具 / 获得风格点数 …

  得分 -> 计分   25 条
      只改 HUD 与标签的短串。例：
        得分上限   -> 计分上限
        我的得分   -> 我的计分
        得分区域   -> 计分区域
      比赛规则与教程的长句说明保留「得分」，
      因为那里讲的是计分规则本身，改成「计分」会读不通。


【四】地名与术语
    有货必达 -> 有货即达   3 处
    市中心   -> 主城区    27 处
    郊区     -> 城郊      33 处
    年龄档「旧」->「老」    2 处
      ★「旧」在表里也是两条独立记录，两条都已修正。
        旧酒吧 / 依旧逍遥法外 / 移除旧曲目 / 怀旧 / 旧肉类加工厂 等未动。

  说明：「市中心」的英文原串是 Downtown（不是 City Center），
  译作「主城区」更贴合原意。


【五】地名双「区」修复
  暂停菜单地图界面会自动在地名后加一个「区」字，
  而中文地名本身也带「区」，于是显示成「住宅区 区」。
  本次把 33 条地名的末尾「区」换成空格（等长替换），
  界面会显示成「住宅  区」，不再重复。

  涉及：住宅 / 老城 / 棚户 / 工厂 / 拖车公园 / 码头 / 工业 / 大学 /
        红灯 / 娱乐 / 办公 / 巴里奥 / Barrio / 市中心 / 城郊扩建 /
        斯蒂尔沃特核厂 / 酒店码头 / 码头博物馆 / 街（4处）/
        未知街 / 控制街 / 兄弟街 / 主城 / 城郊 …

  句子里带「区」的一律不动（正在进入禁区 / 第 9 区 / 返回市区 等），
  复合地名也不动（城郊码头 / 主城区拆车厂 等）。


【六】地图地名改名
    圣徒街 -> 圣徽街      4 条
  游戏中该地名的记录是「圣徒街」3 个字（无「区」无空格），
  所以改用同样 3 字的「圣徽街」，等长替换。

  ★ 只改了 4 条地图地名记录。以下含「圣徒街」的地方按需求保持原样：
    界面提示串（前往[...]、返回[...]）、
    复合地名（圣徒街教堂 / 车站 / 运河 / 阁楼 / 杀手 / 超级公寓）、
    长句叙述。
    因此游戏里可能出现「地图显示圣徽街、提示文字写圣徒街」的情况。
    若要统一，改法告知即可。


【未改动的文件】
  common.vpp_pc / textures.vpp_pc / SR2_pc.exe / DFEngine.dll /
  DLC 文件 —— 全部保持原样。


【安装方法】
把 patch.vpp_pc 复制到游戏目录覆盖同名文件即可
（通常是 C:\\Program Files (x86)\\Steam\\steamapps\\common\\Saints Row 2\\）。

★ 覆盖前请先把自己现有的 patch.vpp_pc 改名备份一份。

【回滚方法】
本包里 _回滚用_patch_修改前.bak 就是修改前的原文件，
想撤销时改名回 patch.vpp_pc 覆盖回去即可。

【重要提醒】
★ 不要在 Steam 里点"验证文件完整性"！
  那会把 patch.vpp_pc 还原成官方原版，汉化全部丢失。


【文件清单】
见 FILELIST.txt
"""

fl = [
  "patch.vpp_pc,%d,%s,%s" % (len(b), M_FIXED, "含全部 6 项修复的汉化主包"),
  "FILELIST.txt,-,自身,校验清单",
  "README.txt,-,%s,本说明" % hashlib.md5(README.encode("utf-8")).hexdigest(),
  "_回滚用_patch_修改前.bak,%d,%s,%s" % (len(a), M_BEFORE, "修复前的原文件（回滚用）"),
]
FILELIST = "文件名,大小(bytes),md5,说明\n" + "\n".join(fl) + "\n"

os.makedirs(OUTDIR, exist_ok=True)
if os.path.exists(OUT):
    os.remove(OUT)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    z.writestr("README.txt", README.encode("utf-8"))
    z.writestr("FILELIST.txt", FILELIST.encode("utf-8"))
    z.write(FIXED, "patch.vpp_pc")
    z.write(BEFORE, "_回滚用_patch_修改前.bak")

print()
print("OK 完成:", OUT)
print("   大小: {:,} bytes".format(os.path.getsize(OUT)))
print("   md5  :", md5(OUT))
