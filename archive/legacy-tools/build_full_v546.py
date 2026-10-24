# -*- coding: utf-8 -*-
"""
构建「黑道圣徒2 简体中文 v546 + Juice 9.3.1 + DLC 1.0.1」整合包
（原地刷新版：不删除目录，只覆盖 + 清理，避免被安全策略拦截）
★ 覆盖顺序：Juice → DLC → 汉化（汉化必须最后）
★ juiced.ini 用当前游戏目录那份（含用户自定义优化项）
"""
import zipfile, hashlib, os, shutil

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
JUICE_ZIP = 'D:/下载/Compressed/SR2_JUICED_2.zip'
DLC_ZIP = 'D:/下载/Compressed/DLC 1.0.1.zip'
OUT_DIR = 'F:/sr2-cn/_发布包/黑道圣徒2_简体中文_Juice9.3.1_DLC1.0.1_整合包/'


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


os.makedirs(OUT_DIR, exist_ok=True)

print('解包 Juice 9.3.1 ...')
with zipfile.ZipFile(JUICE_ZIP) as z:
    z.extractall(OUT_DIR)
print('  完成')

print('解包 DLC 1.0.1 ...')
with zipfile.ZipFile(DLC_ZIP) as z:
    z.extractall(OUT_DIR)
print('  完成')

print('覆盖汉化文件 ...')
HANS = [
    (G + 'patch.vpp_pc', 'patch.vpp_pc', '汉化主体 v545（22 项修复）'),
    (G + 'DLC/Text/dlc_ch.le_strings', 'DLC/Text/dlc_ch.le_strings', 'DLC 简体中文'),
    (G + 'Mods/dialog_box.lua', 'Mods/dialog_box.lua', '等待玩家界面 SUI 标签修复'),
    (G + 'Mods/dialog_box.lua.sui.bak', 'Mods/dialog_box.lua.sui.bak', '原始 mod 备份（可回滚）'),
    (G + 'Mods/JUICED - Strings/juiced_CH.cxt', 'Mods/JUICED - Strings/juiced_CH.cxt', 'Juice 菜单中文'),
    (G + 'Mods/JUICED - Strings/juiced_CH.le_strings', 'Mods/JUICED - Strings/juiced_CH.le_strings',
     'Juice 菜单表 v546（OpenSpy 重译）'),
    (G + 'Mods/city_load.lua', 'Mods/city_load.lua', '加载画面提示（保持英文，见说明）'),
]
for src, rel, note in HANS:
    dst = os.path.join(OUT_DIR, rel.replace('/', os.sep))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print('   %-46s %s  %s' % (rel, md5(dst), note))

shutil.copy2(G + 'juiced.ini', os.path.join(OUT_DIR, 'juiced.ini'))
print('   %-46s %s  (用当前配置)' % ('juiced.ini', md5(os.path.join(OUT_DIR, 'juiced.ini'))))

print('清理 ...')
removed = 0
for root, dirs, files in os.walk(OUT_DIR):
    for fn in files:
        fp = os.path.join(root, fn)
        if fn.lower().endswith('.pdb'):
            os.remove(fp)
            removed += 1
for junk in ['Juiced/logs', 'Juiced/CrashDumps']:
    p = os.path.join(OUT_DIR, junk.replace('/', os.sep))
    if os.path.exists(p):
        for fn in os.listdir(p):
            fp = os.path.join(p, fn)
            if os.path.isfile(fp) and fn not in ('LOGSHERE', 'DMPSHERE'):
                os.remove(fp)
                removed += 1
for root, dirs, files in os.walk(OUT_DIR):
    for fn in files:
        if fn.lower().endswith(('.bak', '.orig', '.orig_ascii')):
            if fn != 'dialog_box.lua.sui.bak':
                os.remove(os.path.join(root, fn))
                removed += 1
print('   清理 %d 个文件' % removed)
print('目录刷新完成')
