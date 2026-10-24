# -*- coding: utf-8 -*-
"""生成 FILELIST + 打包 zip + 完整校验"""
import os, hashlib, zipfile

OUT_DIR = 'F:/sr2-cn/_发布包/黑道圣徒2_简体中文_Juice9.3.1_DLC1.0.1_整合包/'
OUT_ZIP = 'F:/sr2-cn/_发布包/黑道圣徒2_简体中文_Juice9.3.1_DLC1.0.1_整合包.zip'

def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

# ===== 收集文件 =====
files = []
for root, dirs, fns in os.walk(OUT_DIR):
    for fn in fns:
        p = os.path.join(root, fn)
        rel = os.path.relpath(p, OUT_DIR).replace('\\', '/')
        files.append((rel, p))
files.sort()
print('文件数:', len(files))

# ===== FILELIST =====
lines = ['黑道圣徒2 简体中文 + Juice 9.3.1 + DLC 1.0.1 整合包',
         '生成时间: 2026-10-20',
         '汉化版本: v545 (22 项修复)',
         '共 %d 个文件' % len(files),
         '=' * 78, '']
total = 0
for rel, p in files:
    if rel.startswith('_先读我'):
        continue
    sz = os.path.getsize(p)
    total += sz
    lines.append('%-62s %10d  %s' % (rel, sz, md5(p)))
lines += ['', '总大小: %.1f MB' % (total / 1048576)]
with open(OUT_DIR + 'FILELIST.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('FILELIST.txt 已生成')

# ===== 打包 =====
if os.path.exists(OUT_ZIP):
    os.replace(OUT_ZIP, OUT_ZIP + '.old')
with zipfile.ZipFile(OUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
    for rel, p in files:
        if rel == 'FILELIST.txt':
            continue
        z.write(p, rel)
    z.write(OUT_DIR + 'FILELIST.txt', 'FILELIST.txt')
print()
print('打包完成')
print('  size %.1f MB' % (os.path.getsize(OUT_ZIP) / 1048576))
print('  md5', md5(OUT_ZIP))

# ===== 校验 =====
print()
print('=== 包内校验 ===')
with zipfile.ZipFile(OUT_ZIP) as z:
    assert z.testzip() is None
    nl = z.namelist()
    print('  entries', len(nl))
    MUST = {
        'patch.vpp_pc': '8d82233053e1231337eeb84c82d1933b',
        'DFEngine.dll': '68e176c1c0bc17f8b4c19bd0072a11f9',
        'DLC/Text/dlc_ch.le_strings': 'eedbc779ffbef51c4200aafa73892039',
        'Mods/dialog_box.lua': 'f89645e132f3e65bf9284e68ce7de2cc',
        'Mods/JUICED - Strings/juiced_CH.cxt': 'adf2d39861802a52a0898b7527e1300c',
        'Mods/JUICED - Strings/juiced_CH.le_strings': 'ea20ee64f30cfe9847aa83b6946c1cda',
        'Mods/city_load.lua': '934b0539e0b2dd5934a27c3484aafdef',
        '_先读我.txt': None,
        'FILELIST.txt': None,
    }
    for n, exp in MUST.items():
        assert n in nl, '★缺失 ' + n
        if exp:
            h = hashlib.md5(z.read(n)).hexdigest()
            assert h == exp, '%s 期望 %s 实际 %s' % (n, exp, h)
            print('  OK  %-46s %s' % (n, h))
        else:
            print('  OK  %-46s (%d B)' % (n, len(z.read(n))))
    # DLC 内容抽查
    dlc = [n for n in nl if n.startswith('DLC/')]
    print('  DLC 条目数:', len(dlc))
    juice = [n for n in nl if n.startswith('Mods/') or n.startswith('Juiced/')]
    print('  Mods+Juiced 条目数:', len(juice))
    # 不能有 pdb / 日志
    bad = [n for n in nl if n.lower().endswith(('.pdb', '.bak', '.orig')) and 'sui.bak' not in n]
    assert not bad, bad
    print('  无 pdb/多余备份文件 ✓')
    # DLC 关键内容
    for k in ['DLC/Missions', 'DLC/Cutscenes', 'DLC/Unlockables/dlc_unlockables.xtbl']:
        assert any(n.startswith(k) for n in nl), '★DLC 缺 ' + k
    print('  DLC 关键目录齐全 ✓')

print()
print('=== 顶层结构 ===')
with zipfile.ZipFile(OUT_ZIP) as z:
    for n in sorted(z.namelist()):
        if '/' not in n:
            print('  %-32s %10d' % (n, z.getinfo(n).file_size))