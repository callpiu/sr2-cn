# -*- coding: utf-8 -*-
"""SR2 简体汉化补丁 · 整合修复包 v534（拆车厂 → 弹药填料，共 12 项有效修复）

底基  = v532（641e5df5，已含 v522~v531 全部修复 + le_strings 哈希桶镜像重建）
新增  = v534：武器店「弹药」标签 →「填料」
回滚件 = v407（b430930f，拆车厂崩溃修复之前的状态）
附带  = 昨天手动恢复的两类文件：DLC 汉化 982 条、Juiced 简体菜单
"""
import os, zipfile, hashlib, datetime, shutil

SRC = r'G:/SteamLibrary/steamapps/common/Saints Row 2'
DST = r'F:/sr2-cn/_发布包'
NAME = '黑道圣徒2简体汉化_整合修复包_12项_20261012'
ZIP  = os.path.join(DST, NAME + '.zip')

PATCH_MD5_EXPECT = '2fd6a5e9d517971e2135c5a34c6daf68'   # v534
ROLLBACK_MD5_EXPECT = 'b430930fd03a2106e7fa810722ab2f29' # v407

def md5(p):
    h = hashlib.md5()
    with open(p,'rb') as f:
        for b in iter(lambda: f.read(1<<20), b''):
            h.update(b)
    return h.hexdigest()

ITEMS = [
    # (包内相对路径, 源文件绝对路径, 说明)
    ('patch.vpp_pc', os.path.join(SRC,'patch.vpp_pc'),
     '★汉化主包 v534：拆车厂崩溃修复起全部 12 项修复 + 哈希表重建 + 弹药→填料'),
    ('DLC/Text/dlc_ch.le_strings', os.path.join(SRC,'DLC/Text','dlc_ch.le_strings'),
     '★DLC 全部 982 条简体汉化（slot 编码终版；误用"码点版"会实机空白）'),
    ('Mods/JUICED - Strings/juiced_CH.cxt', os.path.join(SRC,'Mods/JUICED - Strings','juiced_CH.cxt'),
     '★Juiced 模组简体菜单（1856B/53键/CRLF 行尾，必须 rb/wb 读写）'),
    ('Mods/JUICED - Strings/juiced_CH.le_strings', os.path.join(SRC,'Mods/JUICED - Strings','juiced_CH.le_strings'),
     '★Juiced 模组简体菜单字符串表'),
    ('_回滚用/patch_修复前_v407.vpp_pc', os.path.join(SRC,'patch.vpp_pc.beforescrapyardfix.bak'),
     '回滚件：拆车厂崩溃修复之前的 v407 原状态（需要回退时改回此文件名覆盖）'),
]

README = """黑道圣徒2 · 简体汉化整合修复包（12 项）
生成时间：2026-10-12

════════════════════════════════════════════════════════
一、适用前提
════════════════════════════════════════════════════════
· 已安装简体汉化（游戏根目录有 patch.vpp_pc）且 Juiced 模组能正常启动
· 本机游戏目录：G:/SteamLibrary/steamapps/common/Saints Row 2/
· 本包为【增量补丁】，只覆盖 patch.vpp_pc + DLC 汉化 + Juiced 简体菜单，
  不含 common/textures/SR2_pc.exe 等大文件（那些文件本轮未改动）

════════════════════════════════════════════════════════
二、安装步骤
════════════════════════════════════════════════════════
1) 关闭游戏。
2) 先备份你当前的 patch.vpp_pc（本包 _回滚用/ 里是 v407 旧版，不是你的当前版）。
3) 把本包内下列文件复制到游戏目录，覆盖同名文件：
     patch.vpp_pc                                -> 游戏根目录
     DLC\\Text\\dlc_ch.le_strings                 -> DLC\\Text\\
     Mods\\JUICED - Strings\\juiced_CH.cxt         -> Mods\\JUICED - Strings\\
     Mods\\JUICED - Strings\\juiced_CH.le_strings  -> Mods\\JUICED - Strings\\
4) 启动游戏验证：进武器店看弹药标签应显示「填料」；
   接一个拆车厂（Scrapyard）任务交付车辆，应不再崩溃。

⚠ 千万不要点 Steam 的「验证游戏文件完整性」——
   它会把 patch.vpp_pc 还原成官方英文原版，汉化与全部修复都会丢失。
   万一点了，重新执行上面第 3 步即可恢复。

════════════════════════════════════════════════════════
三、本包包含的有效修复（12 项，均经实机确认）
════════════════════════════════════════════════════════
 1. 【崩溃】拆车厂交付车辆崩溃修复
    根因：中文把 %ls 调到 %d/%i 之前，引擎按英文占位符顺序读参，
          把整数当指针 → 崩溃。改回 (d,d,ls) / 把 $%i 提到 %ls 之前。
 2. 专名与用语修正（Maero=马洛 等口径统一 + 格式修正）
 3. 地名与术语修正（第 2 批）
 4. 地名双「区」修复（地图界面会在地名后自动追加「区」，故地名末字不能是「区」）
 5. 地图地名「圣徒街」→「圣徽街」（4 条）
 6. 任务列表「兄弟会任务 N」→「兄弟帮任务 N」（8 条）
 7. 武器名「霰弹枪」→「散筒枪」（3 条）
 8. 「子弹」→「火料」（7 条）
 9. 界面「兄弟会」→「兄弟帮」（5 条）
10. 武器店分类「已扔出」→「投掷类」（2 条）
11. 任务完成界面「等待主机玩家」→「等候主机玩家」（1 条）
12. 【本轮新增】武器店购买界面标签「弹药」→「填料」（1 条）

★ 附带的重要底层修复（v532）：
   修复了大量任务提示显示 "!!unrecognized hash value" 的问题。
   根因是中文 le_strings 表的哈希桶分配被早年的重建工具搞坏
   （12250 条记录只塞进 32/2450 个桶），已按美版桶结构镜像重建，
   桶数与桶内顺序逐条对齐美版，中文文本逐字节沿用。

★ 附带的恢复件（2026-10-11 手动恢复，本包已一并收入）：
   · DLC\\Text\\dlc_ch.le_strings —— DLC 全部 982 条简体汉化
     （注意：必须是 slot 编码版；网上流传的"真 CJK 码点版"实机会显示空白）
   · Mods\\JUICED - Strings\\juiced_CH.cxt / .le_strings —— Juiced 模组简体菜单
     （重装 Juice 安装包会把这两个文件覆盖回旧版导致菜单缺字，用本包覆盖即可恢复）

════════════════════════════════════════════════════════
四、尚未解决（已知问题，不在本包范围内）
════════════════════════════════════════════════════════
· 直升机突击（Helicopter Assault）联机活动第二级的任务提示仍显示乱码。
  已确认：磁盘上的中文数据完全正确，乱码发生在渲染期——
  活动 HUD 用的字形排序与字表 charlist_CH 不一致（你→任、的→璨、弟→偶…）。
  单机与联机都会出现。排查交接文档：F:/sr2-cn/_交接_活动字幕乱码_20261012.md

════════════════════════════════════════════════════════
五、回滚
════════════════════════════════════════════════════════
把 _回滚用\\patch_修复前_v407.vpp_pc 改名为 patch.vpp_pc 覆盖游戏根目录同名文件，
即回到「拆车厂崩溃修复之前」的 v407 状态（本包 1~12 项全部撤销）。
注意：v407 仍带有 "!!unrecognized hash value" 问题。

════════════════════════════════════════════════════════
六、文件校验（md5）
════════════════════════════════════════════════════════
"""

# ---- 校验 + 打包 ----
assert md5(os.path.join(SRC,'patch.vpp_pc')) == PATCH_MD5_EXPECT, 'patch 不是 v534'
assert md5(os.path.join(SRC,'patch.vpp_pc.beforescrapyardfix.bak')) == ROLLBACK_MD5_EXPECT, '回滚件不是 v407'

os.makedirs(DST, exist_ok=True)
if os.path.exists(ZIP): os.remove(ZIP)

lines = []
with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for rel, src, desc in ITEMS:
        assert os.path.exists(src), 'MISSING '+src
        m = md5(src); sz = os.path.getsize(src)
        lines.append(f'{m}  {sz:>10d}  {rel}\n    {desc}\n')
        print(f'  + {rel}  {sz}  {m}')
        z.write(src, rel)
    # FILELIST
    filelist = ''.join(lines)
    z.writestr('FILELIST.txt', filelist)
    z.writestr('README.txt', README + '\n' + filelist)

# ---- 打包后自检 ----
with zipfile.ZipFile(ZIP) as z:
    bad = z.testzip()
    assert bad is None, 'ZIP 损坏: '+str(bad)
    names = z.namelist()
    assert not any(n.endswith(('.bak','.new','.orig')) for n in names), '包内混入了备份文件: '+str(names)
    data = z.read('patch.vpp_pc')
    assert hashlib.md5(data).hexdigest() == PATCH_MD5_EXPECT, '包内 patch md5 不符'

print('\nZIP:', ZIP)
print('大小:', os.path.getsize(ZIP), '字节')
print('条目:', len(names))
for n in names: print('   ', n)
print('包 md5:', md5(ZIP))
print('自检通过')
