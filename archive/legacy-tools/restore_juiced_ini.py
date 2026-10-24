"""把 juiced.ini 恢复到测试之前的原始状态。"""
import os, shutil

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
INI = os.path.join(G, 'juiced.ini')

# 优先用最早的备份（before_pooltest 是最初的状态）
for name in ('juiced.ini.before_pooltest', 'juiced.ini.before_prompttest'):
    p = os.path.join(G, name)
    if os.path.exists(p):
        shutil.copy2(p, INI)
        print('已恢复 juiced.ini（来自 %s, %d 字节）' % (name, os.path.getsize(p)))
        break
else:
    print('未找到备份')

# 确认关键项回到原值
import re
c = open(INI, encoding='utf-8').read().split('\n')
print()
print('=== 恢复后的关键项 ===')
KEY = ('EnableDynamicPrompts', 'ForceInputPrompt', 'ForcedControllerPrompts',
       'interface_gpu_multi', 'permanent', 'Bitmap_Image_Names',
       'perm_mesh_cpu', 'animation')
found = 0
for i, l in enumerate(c):
    m = re.match(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$', l)
    if m and m.group(1) in KEY:
        print('  %-28s = %s' % (m.group(1), m.group(2)))
        found += 1
if not found:
    print('  （全部为空 —— 说明恢复了默认）')
