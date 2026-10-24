# -*- coding: utf-8 -*-
"""盘点游戏目录当前状态，与两个源包 + 汉化做三方比对"""
import hashlib, os, zipfile

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'

def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

def zip_md5(z, name):
    h = hashlib.md5()
    with z.open(name) as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

print('=' * 100)
print('=== 1. Juice 9.3.1 zip vs 游戏目录 ===')
print('=' * 100)
z = zipfile.ZipFile('D:/下载/Compressed/SR2_JUICED_2.zip')
same = diff = missing = 0
diffs = []
for n in z.namelist():
    if n.endswith('/'):
        continue
    gp = G + n.replace('/', os.sep)
    if not os.path.exists(gp):
        missing += 1
        continue
    if md5(gp) == zip_md5(z, n):
        same += 1
    else:
        diff += 1
        diffs.append(n)
print('  已装且一致: %d' % same)
print('  已装但不同: %d' % diff)
print('  未安装    : %d' % missing)
if diffs:
    print('  不同的文件:')
    for n in diffs[:20]:
        print('     ', n)

print()
print('=' * 100)
print('=== 2. DLC 1.0.1 zip vs 游戏目录 ===')
print('=' * 100)
z2 = zipfile.ZipFile('D:/下载/Compressed/DLC 1.0.1.zip')
same = diff = missing = 0
diffs = []
for n in z2.namelist():
    if n.endswith('/'):
        continue
    gp = G + n.replace('/', os.sep)
    if not os.path.exists(gp):
        missing += 1
        continue
    if md5(gp) == zip_md5(z2, n):
        same += 1
    else:
        diff += 1
        diffs.append(n)
print('  已装且一致: %d' % same)
print('  已装但不同: %d' % diff)
print('  未安装    : %d' % missing)
if diffs:
    print('  不同的文件:')
    for n in diffs[:20]:
        print('     ', n)

print()
print('=' * 100)
print('=== 3. 汉化文件当前状态 ===')
print('=' * 100)
FILES = [
    ('patch.vpp_pc', '8d82233053e1231337eeb84c82d1933b', 'v545 汉化主体'),
    ('Mods/dialog_box.lua', 'f89645e132f3e65bf9284e68ce7de2cc', 'SUI 修复'),
    ('Mods/dialog_box.lua.sui.bak', '4dc698b8eb797eeafec1c6c80a3c1ac1', '原始 mod 备份'),
    ('DLC/Text/dlc_ch.le_strings', 'eedbc779ffbef51c4200aafa73892039', 'DLC 中文'),
    ('Mods/JUICED - Strings/juiced_CH.cxt', 'adf2d39861802a52a0898b7527e1300c', 'Juice 菜单中文'),
    ('Mods/JUICED - Strings/juiced_CH.le_strings', 'ea20ee64f30cfe9847aa83b6946c1cda', 'Juice 菜单表'),
    ('Mods/city_load.lua', '934b0539e0b2dd5934a27c3484aafdef', '加载提示(英文)'),
]
for rel, exp, note in FILES:
    gp = G + rel.replace('/', os.sep)
    if not os.path.exists(gp):
        print('  %-42s ★不存在  (%s)' % (rel, note))
        continue
    h = md5(gp)
    ok = 'OK' if h == exp else '★与预期不符'
    print('  %-42s %s  %s' % (rel, h, ok))

print()
print('=== 4. DLC 目录结构（游戏里）===')
for root, dirs, files in os.walk(G + 'DLC'):
    depth = root[len(G + 'DLC'):].count(os.sep)
    if depth <= 1:
        print('  %s/  (%d files)' % (os.path.relpath(root, G), len(files)))
    if depth >= 1:
        dirs[:] = []