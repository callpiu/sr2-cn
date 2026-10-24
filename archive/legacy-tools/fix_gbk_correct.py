"""正确地把 Lua 里的中文转成 GBK。

上次的错误
    用了 Python 的默认文本编码（在中文 Windows 上是 GBK）去读 UTF-8 文件：
        open(p, encoding='utf-8', errors='replace')   # ← 我写的是这个，但读回来时
        open(p, 'rb').read().decode('utf-8')          #   这一步是对的
    真正的问题在后面 apply() 里 —— 它先 decode('utf-8') 失败后 fallback 到
    decode('latin1')，于是把 UTF-8 字节原样搬进 str，
    再 encode('gbk') 时就把每个字节当成一个 Latin-1 字符编码成 GBK 双字节
    → 二次损坏（"善用" 变成 B9BA C2F0 而不是 C9C6 D3C3）

本版做法
    * 全部用二进制读写，显式 utf-8 / gbk 编解码
    * 从 .utf8 备份（正确的 UTF-8 中文版）出发
    * 写完后按字节复验：GBK 编码结果必须等于 原文.encode('gbk')
"""
import os, re, shutil

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
M = os.path.join(G, 'Mods')

FILES = {
    'pause_menu.lua':     '.utf8',
    'main_menu.lua':      '.utf8',
    'sui_main_menu.lua':  '.utf8',
    'hud.lua':            '.utf8',
}


def load_utf8(path):
    """显式按 UTF-8 读；失败则报错而不是猜。"""
    b = open(path, 'rb').read()
    return b.decode('utf-8'), b


print('=== 从 .utf8 备份重新转 GBK ===')
print('%-24s %-10s %-10s %s' % ('文件', 'UTF-8字节', 'GBK字节', '校验'))
print('-' * 60)
ok = True
for fn, suf in FILES.items():
    src = os.path.join(M, fn + suf)
    dst = os.path.join(M, fn)
    if not os.path.exists(src):
        print('%-24s 缺少 %s' % (fn, suf))
        ok = False
        continue
    txt, raw = load_utf8(src)
    nonascii = sorted({c for c in txt if ord(c) > 0x7F})
    try:
        out = txt.encode('gbk')
    except UnicodeEncodeError as e:
        print('%-24s GBK 编码失败: %s' % (fn, e))
        ok = False
        continue
    open(dst, 'wb').write(out)
    # 复验：读回来必须与 txt 完全一致
    back = open(dst, 'rb').read().decode('gbk')
    same = (back == txt)
    print('%-24s %-10d %-10d %s' % (fn, len(raw), len(out), 'OK' if same else '不一致!'))
    if not same:
        ok = False

# city_load.lua：它是在 UTF-8 阶段替换了 SUI_TIPS_*
print()
print('=== city_load.lua（含 46 条加载提示）===')
p = os.path.join(M, 'city_load.lua')
bak = os.path.join(M, 'city_load.lua.utf8')
if os.path.exists(bak):
    # .utf8 是 GBK 阶段之前的版本 → 需要重新做 tips 替换
    TIPS = [
        '善用掩体可以减少受伤','按 R 可以捡起地上的物品','完成任务可以提升帮派声望',
        '在地图上标记目标可以指引方向','驾驶时按 Shift 可以加速','购买房产可以获得额外收入',
        '升级武器可以提升威力','召唤小弟可以协助战斗','完成任务时注意保存进度',
        '击倒敌人后可以抢夺他们的武器','车辆可以开到车库进行改装','按 Tab 可以查看地图',
        '遇到警察时注意通缉等级','使用手雷可以对付聚集的敌人','不同的服装可以获得不同效果',
        '在商店可以购买武器和补给','帮派地盘可以通过完成任务扩张','多利用环境可以更轻松取胜',
        '骑摩托车时注意保持平衡','被通缉时可以躲进建筑物','完成小游戏可以获得额外奖励',
        '和朋友一起玩可以完成更多挑战','注意屏幕上的提示信息','保存游戏可以避免进度丢失',
        '升级角色能力可以让战斗更轻松','在车库里可以保存你喜欢的车辆','多尝试不同的武器找到适合自己的',
        '完成任务后记得领取奖励','注意敌人的攻击前摇及时闪避','可以随时调整难度设置',
        '利用高处可以获得视野优势','金钱可以用来购买装备和房产','把车停在安全的地方再下车',
        '注意任务提示中的时间限制','不同的帮派有不同的战斗风格','在城市中探索可以发现隐藏内容',
        '完成任务可以获得新的武器解锁','保持移动可以避免被敌人包围','使用望远镜可以标记远处的目标',
        '受伤后可以寻找医疗包恢复','多利用车辆快速移动','注意天气对驾驶的影响',
        '把重要的车辆存进车库','完成任务链可以解锁新的剧情','随时可以打开选项调整设置',
    ]
    txt, raw = load_utf8(bak)
    n = 0
    for i, tip in enumerate(TIPS, 1):
        pat = '"SUI_TIPS_%d"' % i
        if pat in txt:
            n += txt.count(pat)
            txt = txt.replace(pat, '"%s"' % tip)
    out = txt.encode('gbk')
    open(p, 'wb').write(out)
    back = open(p, 'rb').read().decode('gbk')
    print('  SUI_TIPS_* 替换 %d 处, %d -> %d 字节, 复验 %s' % (
        n, len(raw), len(out), 'OK' if back == txt else '不一致!'))
    if back != txt:
        ok = False

print()
print('=== 关键验证：字节必须等于 GBK 编码结果 ===')
tests = {'pause_menu.lua': '音效选项', 'pause_menu.lua#2': '武器切换音效',
         'city_load.lua': '善用掩体可以减少受伤', 'hud.lua': '你死了',
         'main_menu.lua': '正在载入游戏...'}
for k, s in tests.items():
    fn = k.split('#')[0]
    p = os.path.join(M, fn)
    b = open(p, 'rb').read()
    want = s.encode('gbk')
    got = want in b
    print('  %-22s %-24s 期望字节 %s  %s' % (fn, s, want.hex(' '), '命中 OK' if got else '★ 未命中'))
    if not got:
        ok = False

print()
print('全部通过' if ok else '★ 有问题')
