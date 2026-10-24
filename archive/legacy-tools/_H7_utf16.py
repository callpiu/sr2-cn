# -*- coding: utf-8 -*-
"""暴力探测：把 static_US / patch_us / juiced_CH 整文件按 UTF-16LE 解码，看可读文本。"""
import os, re

S = r'G:\SteamLibrary\steamapps\common\Saints Row 2\Mods\JUICED - Strings'
M = r'G:\SteamLibrary\steamapps\common\Saints Row 2\Mods'

for p in [
    os.path.join(M, 'static_US.le_strings'),
    os.path.join(S, 'patch_us.le_strings'),
    os.path.join(S, 'juiced_CH.le_strings'),
]:
    raw = open(p, 'rb').read()
    print('=' * 70)
    print(os.path.basename(p), 'size=', len(raw))
    t = raw.decode('utf-16-le', 'replace')
    # 取可读片段
    runs = re.findall(r'[ -~]{6,}', t)
    print('  可读 run 数=%d' % len(runs))
    for r in runs[:12]:
        print('    |', r[:90])
