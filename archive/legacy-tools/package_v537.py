# -*- coding: utf-8 -*-
"""SR2 简体汉化补丁 · 整合修复包 v537（2026-10-14）

底基链：v532(哈希桶镜像重建) → v534(弹药→填料) →外部修复(count=补全) →
       v536(城郊→市郊) → v537(弹药类三项回滚)
本轮新增 = v537：
  · 散筒枪 → 霰弹枪 (6处)
  · 火料   → 弹药   (14 处)
  · 填料   → 弹药   (1 处)
★关键底层修复（外部修复版已含）：charlist_CH.txt 补回count=2795 首行。
  此前该首行缺失 → 引擎 loadcharlist 读count 失败 → 整张字符表为空
  → 所有汉字按固定假映射渲染，即历史上那8 个「坏字位」与活动字幕乱码的共同根因。
"""
import os, zipfile, hashlib

SRC = r'G:/SteamLibrary/steamapps/common/Saints Row 2'
DST = r'F:/sr2-cn/_发布包'
NAME = '黑道圣徒2简体汉化_整合修复包_15项_20261014'
ZIP  = os.path.join(DST, NAME + '.zip')

PATCH_MD5_EXPECT   = 'bc88168fafe2e514ea7ba26e30c8201f'   # v537
ROLLBACK_MD5_EXPECT = 'b430930fd03a2106e7fa810722ab2f29' # v407

def md5(p):
    h = hashlib.md5()
    with open(p,'rb') as f:
        for b in iter(lambda: f.read(1<<20), b''):
            h.update(b)
    return h.hexdigest()

ITEMS = [
    ('patch.vpp_pc', os.path.join(SRC,'patch.vpp_pc'),
     '★汉化主包 v537：字符表 count= 修复 + 全部 15 项有效修复'),
    ('DLC/Text/dlc_ch.le_strings', os.path.join(SRC,'DLC/Text','dlc_ch.le_strings'),
     '★DLC 全部 982 条简体汉化（slot 编码终版；误用"码点版"会实机空白）'),
    ('Mods/JUICED - Strings/juiced_CH.cxt', os.path.join(SRC,'Mods/JUICED - Strings','juiced_CH.cxt'),
     '★Juiced 模组简体菜单（1856B/53键/CRLF 行尾，必须 rb/wb 读写）'),
    ('Mods/JUICED - Strings/juiced_CH.le_strings', os.path.join(SRC,'Mods/JUICED - Strings','juiced_CH.le_strings'),
     '★Juiced 模组简体菜单字符串表'),
    ('_回滚用/patch_修复前_v407.vpp_pc', os.path.join(SRC,'patch.vpp_pc.beforescrapyardfix.bak'),
     '回滚件：拆车厂崩溃修复之前的 v407 原状态（改回此文件名覆盖即完成回滚）'),
]

README = """黑道圣徒2 · 简体汉化整合修复包（15 项）
生成时间：2026-10-14

════════════════════════════════════════════════════���═══════════
一、适用前提
════════════════════════════════════════════════════════════
· 已安装简体汉化（游戏根目录有 patch.vpp_pc）且 Juiced 模组能正常启动
· 本机游戏目录：G:/SteamLibrary/steamapps/common/Saints Row 2/
· 本包为【增量补丁】，只覆盖 patch.vpp_pc + DLC 汉化 + Juiced 简体菜单。
  不含 common/textures/SR2_pc.exe 等大文件（那些文件本轮未改动）。

════════════════════════════════════════════════════════════
二、安装步骤
════════════════════════════════════════════════════════════
1) 关闭游戏。
2) 先备份你当前的 patch.vpp_pc（本包 _回滚用/ 里是 v407 旧版，不是你的当前版）。
3) 把本包内下列文件复制到游戏目录，覆盖同名文件：
     patch.vpp_pc                                -> 游戏根目录
     DLC\\Text\\dlc_ch.le_strings                 -> DLC\\Text\\
     Mods\\JUICED - Strings\\juiced_CH.cxt         -> Mods\\JUICED - Strings\\
     Mods\\JUICED - Strings\\juiced_CH.le_strings  -> Mods\\JUICED - Strings\\
4) 启动游戏验证：
   · 武器库里应显示「霰弹枪」（不再是「散筒枪」）
   · 弹药类条目名应统一为「弹药」（不再是「火料」「填料」）
   · Suburbs 区域地名应为「市郊/市郊区」（不再是「城郊」「城区」）

⚠ 千万不要点 Steam 的「验证游戏文件完整性」——
   它会把 patch.vpp_pc 还原成官方英文原版，汉化与全部修复都会丢失。
   万一点了，重新执行上面第 3 步即可恢复。

════════════════════════════════════════════════════════════
三、★本轮最重要的底层修复：字符表 count= （务必确认已生效）
════════════════════════════════════════════════════════════
patch.vpp_pc 内的 charlist_CH.txt 此前缺少首行 `count=2795`。
引擎 loadcharlist 用 sscanf("count=%u") 读取该行，缺失时 count=0 →
malloc(0) → 循环零次 → **整张字符表为空**。

后果：所有汉字都按一套固定假映射渲染，表现为
  · 八个「坏字位」：三→丈、会→伙、律→延、徒→建、得→开、
    心→引、必→弗、联→伙（无论填哪个字都显示成这些错字）
  · 「你的弟兄们需要你的保护」显示为「任璨偶巧位雄衡…」
  · 直升机突击等联机活动字幕乱码
本包已补回count=2795，上述问题应全部消失。
若游戏里仍看到旧错字，说明 patch.vpp_pc 没被正确覆盖。

════════════════════════════════════════════════════════════
四、本包包含的有效修复（15 项）
════════════════════════════════════════════════════════════
 1. 【崩溃】拆车厂交付车辆崩溃修复
    根因：中文把 %ls 调到 %d/%i 之前，引擎按英文占位符顺序读参，
          把整数当指针 → 崩溃。
 2. 专名与用语修正（Maero=马洛 等口径统一 + 格式修正）
 3. 地名与术语修正（第 2 批）
 4. 地名双「区」修复（地图界面会在地名后自动追加「区」，故地名末字不能是「区」）
 5. 地图地名「圣徒街」→「圣徽街」
 6. 任务列表「兄弟会任务 N」→「兄弟帮任务 N」
 7. ★「3rdS」→「三街圣徒」（当年为绕开坏字位做的英文折中，现已能正常显示）
 8. ★「兄弟帮」→「兄弟会」全部回滚（28 处）
 9. ★「指定辩护人」→「指定辩护律师」回滚（4 处）
10. ★「3王」→「三王」回滚（4 处）
11. 武器店分类「已扔出」→「投掷类」
12. 任务完成界面「等待主机玩家」→「等候主机玩家」
13. ★★ Suburbs 区域名「城郊」→「市郊」（32 条记录 / 64 处）
    考证：官方英文表 static_US 里Suburb=32 次、Outskirt=0 次，
    故 SR2 官方用词是 Suburbs，对应中文「城郊」；Downtown=25 次对应「主城区」。
    因本体表为定长槽位、32 条中 30 条无余量可加字，采用等长替换
    「市郊」；地图界面由引擎自动补「区」字，故显示为「市郊区」。
14. ★★【本轮】武器名「散筒枪」→「霰弹枪」（6 处）
15. ★★【本轮】弹药类折中译名回滚：「火料」→「弹药」（14 处）、
    「填料」→「弹药」（1 处）
    说明：「填药」经全表核查为0 处（不存在），实际是「填料」；
    「火料」按译名一致性统一为「弹药」而非「子弹」。

★ 底层修复（v532）：修复大量任务提示显示 "!!unrecognized hash value"。
  根因是中文 le_strings 的哈希桶分配被早年重建工具搞坏
  （12250 条只塞进 32/2450 个桶），已按美版桶结构镜像重建。

════════════════════════════════════════════════════════════
五、已知遗留问题
════════════════════════════════════════════════════════════
· 地图暂停界面的区域名（district/hood）由引擎 C++ 侧从地图数据读取，
  不经过 le_strings 表。若该处仍显示「城区」而非「市郊区」，
  属另一条数据通路，需另行处理（本包未覆盖）。

════════════════════════════════════════════════════════════
六、回滚
════════════════════════════════════════════════════════════
把 _回滚用\\patch_修复前_v407.vpp_pc 改名为 patch.vpp_pc 覆盖游戏根目录，
即回到「拆车厂崩溃修复之前」的 v407 状态（本包 1~15 项全部撤销）。
注意：v407 仍带有 "!!unrecognized hash value" 与坏字位问题。

════════════════════════════════════════════════════════════
七、文件校验（md5）
════════════════════════════════════════════════════════════
"""

# ---- 前置硬断言 ----
assert md5(os.path.join(SRC,'patch.vpp_pc')) == PATCH_MD5_EXPECT, '★ patch 不是 v537'
assert md5(os.path.join(SRC,'patch.vpp_pc.beforescrapyardfix.bak')) == ROLLBACK_MD5_EXPECT, '★ 回滚件不是 v407'
print('✓ 前置断言通过（patch=v537, 回滚件=v407）')

os.makedirs(DST, exist_ok=True)
if os.path.exists(ZIP): os.remove(ZIP)

lines = []
with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for rel, src, desc in ITEMS:
        assert os.path.exists(src), 'MISSING '+src
        m = md5(src); sz = os.path.getsize(src)
        lines.append(f'{m}  {sz:>10d}  {rel}\n    {desc}\n')
        print('  + %-52s %10d  %s'%(rel, sz, m))
        z.write(src, rel)
    filelist = ''.join(lines)
    z.writestr('FILELIST.txt', filelist)
    z.writestr('README.txt', README + '\n' + filelist)

# ---- 打包后自检 ----
with zipfile.ZipFile(ZIP) as z:
    assert z.testzip() is None, 'ZIP 损坏'
    names = z.namelist()
    assert not any(n.endswith(('.bak','.new','.orig')) for n in names), '包内混入备份文件: '+str(names)
    assert hashlib.md5(z.read('patch.vpp_pc')).hexdigest() == PATCH_MD5_EXPECT, '包内 patch md5 不符'

print('\nZIP     :', ZIP)
print('大小    :', os.path.getsize(ZIP), '字节')
print('条目    :', len(names))
for n in names: print('   ', n)
print('包 md5  :', md5(ZIP))
print('自检通过')