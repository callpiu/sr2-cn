"""两步修：
   1. 把我加进 .lua 的中文从 UTF-8 重新编码为 GBK（游戏按单字节处理 Lua 字符串）
   2. 把未定义的 SUI_TIPS_* / SUI_LOADING_* 换成中文字面量

为什么用 GBK
    之前写入 UTF-8，"音效选项" 显示成 "đ³ āĐ□e□□ē¡" ——
    每个汉字被拆成 2 个 Latin 字符，正是 UTF-8 字节被当单字节读的典型表现。
    简体中文 Windows 游戏的 ANSI 代码页是 GBK，所以 Lua 里的中文要用 GBK 字节。
"""
import os, re, shutil

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
M = os.path.join(G, 'Mods')

# ---------- 1. 把已改的 UTF-8 中文转成 GBK ----------
FILES = ['pause_menu.lua', 'main_menu.lua', 'sui_main_menu.lua', 'hud.lua', 'city_load.lua']

print('=== 第 1 步：UTF-8 -> GBK ===')
for fn in FILES:
    p = os.path.join(M, fn)
    if not os.path.exists(p):
        continue
    raw = open(p, 'rb').read()
    # 备份（若还没有 GBK 前的版本）
    bak = p + '.utf8'
    if not os.path.exists(bak):
        shutil.copy2(p, bak)
    try:
        txt = raw.decode('utf-8')
    except UnicodeDecodeError as e:
        print('  %-24s UTF-8 解码失败: %s' % (fn, e))
        continue
    # 只转换非 ASCII 部分
    nonascii = sum(1 for c in txt if ord(c) > 0x7F)
    if nonascii == 0:
        print('  %-24s 无非 ASCII 字符，跳过' % fn)
        continue
    try:
        out = txt.encode('gbk')
    except UnicodeEncodeError as e:
        print('  %-24s GBK 编码失败（有 GBK 不支持的字符）: %s' % (fn, e))
        continue
    open(p, 'wb').write(out)
    print('  %-24s %d 个非 ASCII 字符 -> GBK, %d -> %d 字节' % (fn, nonascii, len(raw), len(out)))

# ---------- 2. 加载提示 ----------
print()
print('=== 第 2 步：加载提示 ===')
TIPS = [
    '善用掩体可以减少受伤',
    '按 R 可以捡起地上的物品',
    '完成任务可以提升帮派声望',
    '在地图上标记目标可以指引方向',
    '驾驶时按 Shift 可以加速',
    '购买房产可以获得额外收入',
    '升级武器可以提升威力',
    '召唤小弟可以协助战斗',
    '完成任务时注意保存进度',
    '击倒敌人后可以抢夺他们的武器',
    '车辆可以开到车库进行改装',
    '按 Tab 可以查看地图',
    '遇到警察时注意通缉等级',
    '使用手雷可以对付聚集的敌人',
    '不同的服装可以获得不同效果',
    '在商店可以购买武器和补给',
    '帮派地盘可以通过完成任务扩张',
    '多利用环境可以更轻松取胜',
    '骑摩托车时注意保持平衡',
    '被通缉时可以躲进建筑物',
    '完成小游戏可以获得额外奖励',
    '和朋友一起玩可以完成更多挑战',
    '注意屏幕上的提示信息',
    '保存游戏可以避免进度丢失',
    '升级角色能力可以让战斗更轻松',
    '在车库里可以保存你喜欢的车辆',
    '多尝试不同的武器找到适合自己的',
    '完成任务后记得领取奖励',
    '注意敌人的攻击前摇及时闪避',
    '可以随时调整难度设置',
    '利用高处可以获得视野优势',
    '金钱可以用来购买装备和房产',
    '把车停在安全的地方再下车',
    '注意任务提示中的时间限制',
    '不同的帮派有不同的战斗风格',
    '在城市中探索可以发现隐藏内容',
    '完成任务可以获得新的武器解锁',
    '保持移动可以避免被敌人包围',
    '使用望远镜可以标记远处的目标',
    '受伤后可以寻找医疗包恢复',
    '多利用车辆快速移动',
    '注意天气对驾驶的影响',
    '把重要的车辆存进车库',
    '完成任务链可以解锁新的剧情',
    '随时可以打开选项调整设置',
]
LOAD = ['正在载入游戏...', '正在读取存档...', '正在准备城市...', '正在载入资源...',
        '正在初始化...', '正在载入地图...', '正在准备车辆...', '正在载入音效...', '请稍候...']

def apply(fn, mapping):
    p = os.path.join(M, fn)
    if not os.path.exists(p):
        return 0
    s = open(p, 'rb').read()
    try:
        txt = s.decode('utf-8')
    except UnicodeDecodeError:
        txt = s.decode('latin1')
    n = 0
    for k, v in mapping.items():
        pat = '"%s"' % k
        if pat in txt:
            n += txt.count(pat)
            txt = txt.replace(pat, '"%s"' % v)
    if n:
        open(p, 'wb').write(txt.encode('gbk', 'replace'))
    return n

tips_map = {'SUI_TIPS_%d' % (i + 1): TIPS[i] for i in range(len(TIPS))}
load_map = {'SUI_LOADING_%d' % (i + 1): LOAD[i] for i in range(len(LOAD))}

for fn in ('city_load.lua',):
    n = apply(fn, tips_map)
    print('  %-24s SUI_TIPS_* 替换 %d 处' % (fn, n))
for fn in ('main_menu.lua', 'sui_main_menu.lua'):
    n = apply(fn, load_map)
    print('  %-24s SUI_LOADING_* 替换 %d 处' % (fn, n))

print()
print('=== 3. 复验 ===')
for fn in FILES:
    p = os.path.join(M, fn)
    if not os.path.exists(p):
        continue
    b = open(p, 'rb').read()
    try:
        t = b.decode('gbk')
        enc = 'GBK'
    except UnicodeDecodeError:
        t = b.decode('utf-8', 'replace'); enc = 'UTF-8'
    left = sorted(set(re.findall(r'SUI_(?:TIPS|LOADING)_[A-Z0-9_]*[0-9]+', t)))
    na = sum(1 for c in t if ord(c) > 0x7F)
    print('  %-24s %-6s 非ASCII %3d 个  剩余 SUI_TIPS/LOADING: %s' % (
        fn, enc, na, ' '.join(left) if left else '无 OK'))
print()
print('=== 抽查（GBK 读回）===')
t = open(os.path.join(M, 'pause_menu.lua'), 'rb').read().decode('gbk', 'replace')
for m in list(re.finditer(r'.{0,25}(音效选项|武器切换音效).{0,25}', t))[:4]:
    print('  ...%s...' % m.group(0).replace('\n', ' '))
