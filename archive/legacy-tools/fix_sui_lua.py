"""把 Juiced 自定义菜单里【未定义的 SUI_* key】替换成中文字面量。

背景
    pause_menu.lua / main_menu.lua / sui_main_menu.lua 是 Juiced 模组自带的修改版菜单。
    它们引用了 15 个 SUI_* key，但这些 key 在任何字符串表里都没有定义
    （patch.vpp_pc 的所有 le_strings、所有 .cxt、exe、DLL 全部搜过）。

    结果：游戏显示原始 key 字符串（"SUI_OPTIONS_TITLE"、"SUI_LOADING_9"）。

修法
    Lua 菜单的 label 支持字面量（模组里已有 "Not implemented yet" 等例子），
    而游戏对 Lua 里的 CJK 渲染正常（不像 Juice 的 .cxt 注入路径）。
    所以直接把 key 换成中文文本。

    只改这三个 .lua 文件，改前备份。
"""
import os, re, shutil

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
M = os.path.join(G, 'Mods')

# key -> 中文（全部字符已在第三方 charlist 里验证通过）
REPL = {
    'SUI_OPTIONS_TITLE':              '音效选项',
    'SUI_OPTIONS_WEAPON_SWITCH_SOUND': '武器切换音效',
    'SUI_OPTIONS_FAST_WEAPON_SWITCH':  '快速切换武器',
    'SUI_OPTIONS_HUD_MESSAGES':        'HUD 讯息',
    'SUI_OPTIONS_HUD_LAYOUT':          'HUD 布局',
    'SUI_OPTIONS_HUD_AUTOHIDE':        'HUD 自动隐藏',
    'SUI_OPTIONS_HUD_ZOMBIE':          '僵尸模式 HUD',
    'SUI_OPTIONS_HUD_LAYOUT_CLASSIC':  '经典',
    'SUI_OPTIONS_HUD_LAYOUT_MODERN':   '现代',
    'SUI_OPTIONS_HUD_ZOMBIE_ORIGINAL': '原始',
    'SUI_OPTIONS_HUD_ZOMBIE_NORMAL':   '普通',
    'SUI_OPTIONS_SCREEN_EDGE_SHADOW':  '屏幕边缘阴影',
    'SUI_MINIMUM':                     '最小',
    'SUI_STOPWATCH_TEST':              '秒表测试',
    'SUI_MULTIPLAYER_NAKED_WARNING':   '多人游戏中出现裸露内容警告',
    'SUI_DEATH_1':                     '你死了',
    # 加载提示（main_menu.lua / sui_main_menu.lua 的 RANDOM_LOADING_MESSAGES）
    'SUI_LOADING_1': '正在载入游戏...',
    'SUI_LOADING_2': '正在读取存档...',
    'SUI_LOADING_3': '正在准备城市...',
    'SUI_LOADING_4': '正在载入资源...',
    'SUI_LOADING_5': '正在初始化...',
    'SUI_LOADING_6': '正在载入地图...',
    'SUI_LOADING_7': '正在准备车辆...',
    'SUI_LOADING_8': '正在载入音效...',
    'SUI_LOADING_9': '请稍候...',
}

FILES = ['pause_menu.lua', 'main_menu.lua', 'sui_main_menu.lua', 'hud.lua']

print('%-24s %-10s %-10s %s' % ('文件', '替换数', '剩余SUI', '备份'))
print('-' * 62)
total = 0
for fn in FILES:
    p = os.path.join(M, fn)
    if not os.path.exists(p):
        print('%-24s (不存在)' % fn)
        continue
    raw = open(p, 'rb').read().decode('utf-8')
    orig = raw
    n = 0
    for k, v in REPL.items():
        # 只替换被引号包住的完整 key
        pat = '"%s"' % k
        if pat in raw:
            c = raw.count(pat)
            raw = raw.replace(pat, '"%s"' % v)
            n += c
    if raw == orig:
        print('%-24s %-10d %-10d %s' % (fn, 0, 0, '-'))
        continue
    bak = p + '.before_sui_cn'
    if not os.path.exists(bak):
        shutil.copy2(p, bak)
    open(p, 'wb').write(raw.encode('utf-8'))
    left = len(re.findall(r'"SUI_[A-Z0-9_]+"', raw))
    total += n
    print('%-24s %-10d %-10d %s' % (fn, n, left, 'OK' if os.path.exists(bak) else '失败'))

print()
print('总计替换 %d 处' % total)
print()
# 逐文件复验
print('=== 复验：各文件剩余的 SUI_ 引用 ===')
for fn in FILES:
    p = os.path.join(M, fn)
    if not os.path.exists(p):
        continue
    s = open(p, encoding='utf-8', errors='replace').read()
    left = sorted(set(re.findall(r'SUI_[A-Z0-9_]+', s)))
    print('  %-24s %s' % (fn, ' '.join(left) if left else '无 OK'))
print()
print('=== 抽查：pause_menu.lua 的音效选项标题 ===')
s = open(os.path.join(M, 'pause_menu.lua'), encoding='utf-8', errors='replace').read()
for m in re.finditer(r'.{0,40}(音效选项|武器切换音效).{0,40}', s):
    print('  ...%s...' % m.group(0).replace('\n', ' '))
