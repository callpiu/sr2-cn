"""把 Lua 菜单里【未定义的 SUI_* key】替换成【英文字面量】。

背景
    Juice 的 pause_menu.lua / main_menu.lua / sui_main_menu.lua / hud.lua /
    city_load.lua 引用了大量 SUI_* key，但这些 key 在游戏字符串表里没有定义
    （Juice 的本地化包只覆盖 J_* 命名空间）。
    结果：菜单和加载界面显示原始 key（"SUI_OPTIONS_TITLE"、"SUI_TIPS_45"）。

为什么用英文而不是中文
    Lua 字符串走的是「每字节 = 1 个码点」的单字节路径，
    单字节最大 255，无法表示 CJK（≥0x4E00）。实测 GBK/UTF-8 都是乱码。
    所以只能写 ASCII。

只替换【会被当作文本显示】的位置：
    * label = "SUI_XXX"
    * 数组/表格字面量里的 "SUI_XXX"（如 LOADING_SCREEN_TIPS、RANDOM_LOADING_MESSAGES）
不碰用于内部追踪的 key（如 event_tracking_interface_tab_change_string）。
"""
import os, re, shutil

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
M = os.path.join(G, 'Mods')

# ---------- 替换表：SUI key -> 英文 ----------
REPL = {
    # 音频/控制/显示 子菜单标题
    'SUI_OPTIONS_TITLE':                'Audio Options',
    'SUI_OPTIONS_WEAPON_SWITCH_SOUND':  'Weapon Switch Sound',
    'SUI_OPTIONS_FAST_WEAPON_SWITCH':   'Fast Weapon Switch',
    # HUD 相关
    'SUI_OPTIONS_HUD_MESSAGES':         'HUD Messages',
    'SUI_OPTIONS_HUD_LAYOUT':           'HUD Layout',
    'SUI_OPTIONS_HUD_LAYOUT_CLASSIC':   'Classic',
    'SUI_OPTIONS_HUD_LAYOUT_MODERN':    'Modern',
    'SUI_OPTIONS_HUD_AUTOHIDE':         'HUD Auto-hide',
    'SUI_OPTIONS_HUD_ZOMBIE':           'Zombie HUD',
    'SUI_OPTIONS_HUD_ZOMBIE_ORIGINAL':  'Original',
    'SUI_OPTIONS_HUD_ZOMBIE_NORMAL':    'Normal',
    'SUI_OPTIONS_SCREEN_EDGE_SHADOW':   'Screen Edge Shadow',
    'SUI_NO_RIPPLE_WAVE_EFFECT_ON_PAUSE': 'No Ripple Effect on Pause',
    # 杂项
    'SUI_MINIMUM':                      'Minimum',
    'SUI_STOPWATCH_TEST':               'Stopwatch Test',
    'SUI_STOPWATCH_DESC':               'Stopwatch Test',
    'SUI_DEATH_1':                      'You Died',
    'SUI_MULTIPLAYER_NAKED_WARNING':    'Nudity is shown in multiplayer',
    'SUI_PLATFORM':                     'PC',
    'SUI_AUTO_CONTINUE':                'Auto Continue',
    'SUI_VERSION':                      'Version',
    'SUI_PAGE1':                        'Profile',
    'SUI_PAGE2':                        'Settings',
    'SUI_WARNING_SR2_OLD':              'This save is from an older version',
    'SUI_WARNING_SR2_RERELEASE':        'This save is from a different release',
    'SUI_GAMEPLAY_CRC_AMBULANCE':       'Ambulance',
    'SUI_GAMEPLAY_CRC_DRIVEBY':         'Drive-by',
    'SUI_GAMEPLAY_CRC_FIRETRUCK':       'Fire Truck',
    'SUI_GAMEPLAY_CRC_FLASHING':        'Flashing',
    'SUI_GAMEPLAY_CRC_STREAKING':       'Streaking',
    'SUI_GAMEPLAY_CRC_TAXI':            'Taxi',
    'SUI_GAMEPLAY_CRC_TOWTRUCK':        'Tow Truck',
    'SUI_CASH_TINT_DOWN':               'Cash Tint Down',
    'SUI_CASH_TINT_UP':                 'Cash Tint Up',
}

# 加载提示 / 加载消息
TIPS = [
    'Use cover to avoid taking damage',
    'Press R to pick up items from the ground',
    'Complete missions to raise your gang respect',
    'Mark targets on the map to get directions',
    'Press Shift while driving to boost',
    'Buy properties for extra income',
    'Upgrade your weapons to increase damage',
    'Call your homies for backup in a fight',
    'Remember to save your progress',
    'Knock down enemies to steal their weapons',
    'Drive vehicles to a garage to customize them',
    'Press Tab to open the map',
    'Watch your notoriety level around police',
    'Use grenades against grouped enemies',
    'Different outfits give different bonuses',
    'Buy weapons and supplies at the store',
    'Expand gang territory by completing missions',
    'Use the environment to win fights more easily',
    'Keep your balance while riding motorcycles',
    'Hide in buildings when wanted by police',
    'Finish activities for extra rewards',
    'Play with friends to complete more challenges',
    'Pay attention to on-screen prompts',
    'Save often so you never lose progress',
    'Upgrade your abilities to make fights easier',
    'Store your favorite vehicles in the garage',
    'Try different weapons to find your favorite',
    'Claim your reward after finishing a mission',
    'Dodge when enemies wind up their attacks',
    'You can change the difficulty at any time',
    'Take the high ground for a better view',
    'Money buys gear, weapons and property',
    'Park in a safe spot before getting out',
    'Watch the time limits on timed missions',
    'Each gang fights with a different style',
    'Explore the city to find hidden content',
    'Finishing missions unlocks new weapons',
    'Keep moving so enemies cannot surround you',
    'Use binoculars to mark distant targets',
    'Find health packs to heal after a fight',
    'Use vehicles to travel across the city fast',
    'Weather affects how your car handles',
    'Store important vehicles in your garage',
    'Finish mission chains to unlock the story',
    'Open the options menu any time to adjust settings',
]
LOADS = ['Loading game...', 'Reading save...', 'Preparing city...', 'Loading resources...',
         'Initializing...', 'Loading map...', 'Preparing vehicles...', 'Loading audio...',
         'Please wait...']
for i, t in enumerate(TIPS, 1):
    REPL['SUI_TIPS_%d' % i] = t
for i, t in enumerate(LOADS, 1):
    REPL['SUI_LOADING_%d' % i] = t

# 成就描述/统计：按 key 名还原成可读英文
for k in list(k for k in []) :
    pass
ACHIEVE_NAMES = {
    'ALL_CITY': 'Complete all City Takeover',
    'AMBULANCE_CHASER': 'Complete all Ambulance diversions',
    'AWW_NUTS': 'Destroy 100 vehicles',
    'A_BETTER_LIFE': 'Complete all missions',
    'A_BRIGHTER_FUTURE': 'Complete all activities',
    'BLUE_COLLAR': 'Complete all Chop Shop lists',
    'BROTHERS_KEEPER': 'Complete all Hitman lists',
    'BUT_IT_SURE_IS_FUN': 'Complete all Mayhem diversions',
    'CRIME_LORD': 'Complete all Activities',
    'DEMOLITION_MAN': 'Complete all Demolition Derby',
    'DO_NOT_TALK_ABOUT_IT': 'Complete all Fight Club',
    'DUKE_OF_STILWATER': 'Complete all Escort',
    'GOING_THE_DISTANCE': 'Complete all Racing',
    'HELIGOOD': 'Complete all Helicopter Assault',
    'HELLO_47': 'Complete all Hitman',
    'HIFEDELITY': 'Complete all Audio Collections',
    'IM_NOT_ADDICTED': 'Complete all Drug Trafficking',
    'LOVE_THY_NEIGHBOR': 'Complete all Neighbor',
    'MAVERICK_GOOSE': 'Complete all Trail Blazing',
    'PURPLE_HAZE': 'Complete all Drug Trafficking',
    'QUICK_AND_PISSED': 'Complete all Escort',
    'REALITY_STAR': 'Complete all Reality Show',
    'REMIND_ME_BABE': 'Complete all Escort',
    'ROMEROS_HERO': 'Complete all Zombie Uprising',
    'SEPPUKU': 'Complete all Ronin missions',
    'SPLATSTER_CHIEF': 'Complete all Septic Avenger',
    'STILL_ADDICTED_TO_THA_ROW': 'Complete all Saints missions',
    'STILWATER_WELCOMING_COM': 'Complete all Welcome',
    'STUNTMAN': 'Complete all Stunt Jumps',
    'SURFSUP': 'Complete all Surf',
    'TRASH_TALKER': 'Complete all Trash',
    'TRICKSTER': 'Complete all Trail Blazing',
    'VELVET_ROPE': 'Complete all Crowd Control',
    'VENGEANCE': 'Complete all Vengeance',
    'WELCOME_BACK': 'Complete all Welcome Back',
    'WHERES_MY_CAR': 'Complete all Tow Truck',
    'WRECKING_CREW': 'Complete all Mayhem',
    'SR2_A_BETTER_LIFE': 'A Better Life',
    'SR2_STILL_ADDICTED_TO_THA_ROW': 'Still Addicted to tha Row',
}
for k, v in ACHIEVE_NAMES.items():
    REPL['SUI_ACHIEVE_DESC_%s' % k] = v
    REPL['SUI_ACHIEVE_%s' % k] = v
STAT_NAMES = {
    'BH_MISSIONS_COMPLETED': 'Brotherhood missions completed',
    'RN_MISSIONS_COMPLETED': 'Ronin missions completed',
    'SS_MISSIONS_COMPLETED': 'Sons of Samedi missions completed',
    'TOTAL_MONEY_GAMBLED': 'Total money gambled',
}
for k, v in STAT_NAMES.items():
    REPL['SUI_STAT_%s' % k] = v

print('替换表共 %d 项' % len(REPL))
print()

FILES = ['pause_menu.lua', 'main_menu.lua', 'sui_main_menu.lua', 'hud.lua', 'city_load.lua']

# 只替换出现在文本位置的 key。安全做法：
#   全文件扫描 "SUI_XXX" 字面量，如果在替换表里就换掉。
#   不在表里的保持原样（避免误伤内部追踪 key）。
print('%-24s %-10s %-12s %s' % ('文件', '替换数', '剩余SUI', '备份'))
print('-' * 66)
total = 0
for fn in FILES:
    p = os.path.join(M, fn)
    if not os.path.exists(p):
        continue
    raw = open(p, 'rb').read()
    try:
        txt = raw.decode('ascii')
    except UnicodeDecodeError:
        print('%-24s ★ 文件含非 ASCII 字节，跳过（请先回退）' % fn)
        continue
    n = 0
    out = txt
    for k, v in REPL.items():
        pat = '"%s"' % k
        if pat in out:
            n += out.count(pat)
            out = out.replace(pat, '"%s"' % v)
    if n == 0:
        print('%-24s %-10d %-12d %s' % (fn, 0, len(set(re.findall(r'"SUI_[A-Z0-9_]+"', out))), '-'))
        continue
    bak = p + '.orig_ascii'
    if not os.path.exists(bak):
        shutil.copy2(p, bak)
    ob = out.encode('ascii')
    open(p, 'wb').write(ob)
    left = len(set(re.findall(r'SUI_[A-Z0-9_]+', out)))
    total += n
    print('%-24s %-10d %-12d %s' % (fn, n, left, 'OK' if os.path.exists(bak) else '失败'))

print()
print('总计替换 %d 处' % total)
print()
print('=== 复验 ===')
for fn in FILES:
    p = os.path.join(M, fn)
    if not os.path.exists(p):
        continue
    b = open(p, 'rb').read()
    try:
        t = b.decode('ascii')
        enc = 'ASCII'
    except UnicodeDecodeError:
        enc = '★ 有非ASCII'
    left = sorted(set(re.findall(r'SUI_[A-Z0-9_]+', t)))[:6]
    print('  %-24s %-10s 剩余 SUI 引用(前6): %s' % (fn, enc, ' '.join(left) if left else '无'))
print()
print('=== 抽查 ===')
t = open(os.path.join(M, 'pause_menu.lua'), 'rb').read().decode('ascii')
for m in list(re.finditer(r'.{0,20}(Audio Options|Weapon Switch Sound).{0,20}', t))[:4]:
    print('  ...%s...' % m.group(0).replace('\n', ' '))
t2 = open(os.path.join(M, 'main_menu.lua'), 'rb').read().decode('ascii')
for m in list(re.finditer(r'.{0,15}(Loading game|Please wait).{0,15}', t2))[:3]:
    print('  ...%s...' % m.group(0).replace('\n', ' '))
