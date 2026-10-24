# -*- coding: utf-8 -*-
"""
构建「黑道圣徒2 简体中文 + Juice 9.3.1 + DLC 1.0.1」一键整合包
来源：
  ① Juice 9.3.1 官方 zip（D:/下载/Compressed/SR2_JUICED_2.zip）
  ② DLC 1.0.1 官方 zip（D:/下载/Compressed/DLC 1.0.1.zip）
  ③ 汉化：patch.vpp_pc (v545) + DLC 中文 + Juice 菜单中文 + dialog_box 修复
★ 覆盖顺序：Juice → DLC → 汉化（汉化必须最后）
★ juiced.ini 用「当前游戏目录」那份（含优化/超宽屏修复等自定义项），不用官方包的原版
"""
import zipfile, hashlib, os, shutil, time

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
JUICE_ZIP = 'D:/下载/Compressed/SR2_JUICED_2.zip'
DLC_ZIP = 'D:/下载/Compressed/DLC 1.0.1.zip'
OUT_DIR = 'F:/sr2-cn/_发布包/黑道圣徒2_简体中文_Juice9.3.1_DLC1.0.1_整合包/'
OUT_ZIP = 'F:/sr2-cn/_发布包/黑道圣徒2_简体中文_Juice9.3.1_DLC1.0.1_整合包.zip'

def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

# ============ 1. 准备目录 ============
if os.path.exists(OUT_DIR):
    shutil.rmtree(OUT_DIR)
os.makedirs(OUT_DIR)

# ============ 2. 解压 Juice ============
print('解包 Juice 9.3.1 ...')
with zipfile.ZipFile(JUICE_ZIP) as z:
    z.extractall(OUT_DIR)
print('  完成')

# ============ 3. 解压 DLC ============
print('解包 DLC 1.0.1 ...')
with zipfile.ZipFile(DLC_ZIP) as z:
    z.extractall(OUT_DIR)
print('  完成')

# ============ 4. 覆盖汉化（最后一步）============
print('覆盖汉化文件 ...')
# (源, 目标相对路径, 说明)
HANS = [
    (G + 'patch.vpp_pc', 'patch.vpp_pc', '汉化主体 v545（22 项修复）'),
    (G + 'DLC/Text/dlc_ch.le_strings', 'DLC/Text/dlc_ch.le_strings', 'DLC 简体中文'),
    (G + 'Mods/dialog_box.lua', 'Mods/dialog_box.lua', '等待玩家界面 SUI 标签修复'),
    (G + 'Mods/dialog_box.lua.sui.bak', 'Mods/dialog_box.lua.sui.bak', '原始 mod 备份（可回滚）'),
    (G + 'Mods/JUICED - Strings/juiced_CH.cxt', 'Mods/JUICED - Strings/juiced_CH.cxt', 'Juice 菜单中文'),
    (G + 'Mods/JUICED - Strings/juiced_CH.le_strings', 'Mods/JUICED - Strings/juiced_CH.le_strings', 'Juice 菜单表'),
    (G + 'Mods/city_load.lua', 'Mods/city_load.lua', '加载画面提示（保持英文，见说明）'),
]
for src, rel, note in HANS:
    dst = os.path.join(OUT_DIR, rel.replace('/', os.sep))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print('   %-46s %s' % (rel, md5(dst)))

# juiced.ini 用当前目录的（含用户自定义优化项）
shutil.copy2(G + 'juiced.ini', os.path.join(OUT_DIR, 'juiced.ini'))
print('   %-46s %s (用当前配置)' % ('juiced.ini', md5(os.path.join(OUT_DIR, 'juiced.ini'))))

# ============ 5. 清理不该带的东西 ============
print('清理 ...')
removed = 0
# .pdb 调试符号（20MB，用不上）
for root, dirs, files in os.walk(OUT_DIR):
    for fn in files:
        if fn.lower().endswith('.pdb'):
            os.remove(os.path.join(root, fn))
            removed += 1
# 日志与崩溃转储
for junk in ['Juiced/logs', 'Juiced/CrashDumps']:
    p = os.path.join(OUT_DIR, junk.replace('/', os.sep))
    if os.path.exists(p):
        for fn in os.listdir(p):
            fp = os.path.join(p, fn)
            if os.path.isfile(fp) and fn != 'LOGSHERE' and fn != 'DMPSHERE':
                os.remove(fp)
                removed += 1
# 其它残留 .bak（保留我们自己的 dialog_box.lua.sui.bak）
for root, dirs, files in os.walk(OUT_DIR):
    for fn in files:
        if fn.lower().endswith(('.bak', '.orig', '.orig_ascii')):
            if fn != 'dialog_box.lua.sui.bak':
                os.remove(os.path.join(root, fn))
                removed += 1
print('   清理 %d 个文件' % removed)

print()
print('目录构建完成')
