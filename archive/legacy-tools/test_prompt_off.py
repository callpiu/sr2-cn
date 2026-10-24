"""测试 4：关闭 Juiced 的「动态输入提示」系统。

线索链
    1. 崩溃在 UTF-16 strlen，坏指针值 = 1（转储实测）
    2. 崩溃前后正在处理含 map_mp_bor_chopshop 的字符串
    3. Juiced 的 Input.cpp 有一个【静态环形缓冲区】：
           static wchar_t prompt_image_buffer[10000];
       它在 index > 9500 时绕回 0，然后 wsprintf 写入，
       最后 return &prompt_image_buffer[start_index];
       —— 返回的是缓冲区【内部】指针
    4. 游戏若保存该指针、稍后再用，而期间缓冲区被后续调用覆盖
       → 悬空指针 → strlen16 读到坏数据 → 正是本次崩溃

    该函数构造的字符串形如：
        [format][scale:1.0][image:map_mp_bor_chopshop][/format]
    —— 与崩溃时的字符串内容吻合

本测试关闭相关开关（只改 juiced.ini）：
    EnableDynamicPrompts=0        关闭动态提示（= 不走那条环形缓冲区路径）
    ForceInputPrompt=0
    ForcedControllerPrompts=0

同时把上一个测试（内存池）恢复原状，避免混淆变量。
"""
import os, shutil, re

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
INI = os.path.join(G, 'juiced.ini')
BAK_POOL = os.path.join(G, 'juiced.ini.before_pooltest')

# ---- 1. 先恢复内存池（回到上一个测试之前的状态）----
if os.path.exists(BAK_POOL):
    shutil.copy2(BAK_POOL, INI)
    print('已恢复内存池设置（从 juiced.ini.before_pooltest）')

# ---- 2. 备份当前状态 ----
BAK = os.path.join(G, 'juiced.ini.before_prompttest')
if not os.path.exists(BAK):
    shutil.copy2(INI, BAK)
    print('已备份 -> juiced.ini.before_prompttest')

# ---- 3. 关闭动态提示 ----
TARGETS = {
    'EnableDynamicPrompts': '0',
    'ForceInputPrompt': '0',
    'ForcedControllerPrompts': '0',
}
text = open(INI, 'rb').read().decode('utf-8')
lines = text.split('\n')
out = []
changed = []
for ln in lines:
    st = ln.strip()
    m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$', st)
    if m and m.group(1) in TARGETS and not st.startswith(';'):
        key = m.group(1)
        indent = ln[:len(ln) - len(ln.lstrip())]
        out.append('%s%s=%s' % (indent, key, TARGETS[key]))
        changed.append((key, m.group(2), TARGETS[key]))
    else:
        out.append(ln)
open(INI, 'wb').write('\n'.join(out).encode('utf-8'))

print()
print('已修改 %d 项：' % len(changed))
for k, old, new in changed:
    print('  %-26s %s -> %s' % (k, old, new))
if not changed:
    print('  （无匹配项，可能已改过）')

print()
print('=== 当前生效的 Input/Modding 相关项 ===')
c = open(INI, encoding='utf-8').read().split('\n')
for i, l in enumerate(c):
    if re.match(r'^\s*(EnableDynamicPrompts|ForceInputPrompt|ForcedControllerPrompts|TagHook|BetterChat|UsePS3)\s*=', l):
        print('  L%-4d %s' % (i+1, l.strip()))

print()
print('=== 内存池已恢复（应看到之前的放大值）===')
for i, l in enumerate(c):
    if re.match(r'^\s*(interface_gpu_multi|permanent|Bitmap_Image_Names|perm_mesh_cpu|animation)\s*=', l):
        print('  L%-4d %s' % (i+1, l.strip()))
