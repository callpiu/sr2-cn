"""测试 3：把 Juiced 的内存池放大改回原版默认值。

为什么做这个测试
    Juiced 默认会放大 6 个资源池：
        interface_gpu_multi           1.5     (默认 1.0)
        permanent                     12582912 (默认 8388608)
        Bitmap_Image_Names_hashtable  24000   (默认 12000)
        Bitmap_Image_Names            73728   (默认 49152)
        perm_mesh_cpu                 2228224 (默认 1114112)
        animation                     34586624(默认 17293312)

    放大内存池会改变堆的布局与资源释放时序。
    如果原版代码里有「资源已释放但引用未清」的隐患，原版的布局可能刚好掩盖它，
    而放大后就会暴露 —— 这正是「稳定复现、寄存器一字不差」的典型来源。

本脚本只改 juiced.ini（备份后注释掉这 6 行，让 Juiced 用内置默认值），
不动任何游戏数据文件。还原只需把备份覆盖回来。
"""
import os, shutil, re

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
INI = os.path.join(G, 'juiced.ini')
BAK = os.path.join(G, 'juiced.ini.before_pooltest')

TARGETS = [
    'interface_gpu_multi',
    'permanent',
    'Bitmap_Image_Names_hashtable',
    'Bitmap_Image_Names',
    'perm_mesh_cpu',
    'audio_wavebank',
    'animation',
]

if not os.path.exists(INI):
    raise SystemExit('未找到 juiced.ini')

raw = open(INI, 'rb').read()
text = raw.decode('utf-8')

if not os.path.exists(BAK):
    shutil.copy2(INI, BAK)
    print('已备份 -> juiced.ini.before_pooltest')

lines = text.split('\n')
out = []
changed = []
for ln in lines:
    stripped = ln.strip()
    m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$', stripped)
    if m and m.group(1) in TARGETS and not stripped.startswith(';'):
        key, val = m.group(1), m.group(2)
        indent = ln[:len(ln) - len(ln.lstrip())]
        out.append('%s; [池测试] %s=%s 已停用（用 Juiced 内置默认值）' % (indent, key, val))
        changed.append((key, val))
    else:
        out.append(ln)

if not changed:
    print('没有需要改的行（可能已经改过）')
else:
    new = '\n'.join(out)
    open(INI, 'wb').write(new.encode('utf-8'))
    print('已停用 %d 项：' % len(changed))
    for k, v in changed:
        print('  %-32s %s' % (k, v))

print()
print('=== 改后 [Mempool] 段 ===')
c = open(INI, encoding='utf-8').read().split('\n')
s = next((i for i, l in enumerate(c) if l.strip() == '[Mempool]'), None)
if s is not None:
    for i in range(s, min(s + 20, len(c))):
        if c[i].strip().startswith('[') and i > s:
            break
        print('  %s' % c[i])
