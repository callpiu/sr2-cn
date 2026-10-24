# -*- coding: utf-8 -*-
"""
汉化 Juice 加载画面提示：Mods/city_load.lua 的 LOADING_SCREEN_TIPS 数组
只替换数组内的字符串字面量，其它内容（含 LF 换行风格）完全不动。
"""
import hashlib, re, sys

P = 'G:/SteamLibrary/steamapps/common/Saints Row 2/Mods/city_load.lua'
BASE = '934b0539e0b2dd5934a27c3484aafdef'

TIPS = [
    ("Use cover to avoid taking damage", "利用掩体躲避伤害"),
    ("Press R to pick up items from the ground", "按 R 捡起地上的物品"),
    ("Complete missions to raise your gang respect", "完成任务提升帮派声望"),
    ("Mark targets on the map to get directions", "在地图上标记目标以获取路线"),
    ("Press Shift while driving to boost", "开车时按 Shift 加速"),
    ("Buy properties for extra income", "购置产业获取额外收入"),
    ("Upgrade your weapons to increase damage", "升级武器以提升伤害"),
    ("Call your homies for backup in a fight", "打架时呼叫兄弟来支援"),
    ("Remember to save your progress", "别忘了保存游戏进度"),
    ("Knock down enemies to steal their weapons", "击倒敌人抢走他们的武器"),
    ("Drive vehicles to a garage to customize them", "把车开进车库进行改装"),
    ("Press Tab to open the map", "按 Tab 打开地图"),
    ("Watch your notoriety level around police", "留意警察附近的通缉值变化"),
    ("Use grenades against grouped enemies", "对成群敌人用手雷"),
    ("Different outfits give different bonuses", "不同服装提供不同加成"),
    ("Buy weapons and supplies at the store", "在商店购买武器和补给"),
    ("Expand gang territory by completing missions", "完成任务扩张帮派地盘"),
    ("Use the environment to win fights more easily", "善用环境能更轻松取胜"),
    ("Keep your balance while riding motorcycles", "骑摩托时注意保持平衡"),
    ("Hide in buildings when wanted by police", "被警察通缉时躲进建筑物"),
    ("Finish activities for extra rewards", "完成活动换取额外奖励"),
    ("Play with friends to complete more challenges", "和朋友一起挑战更多内容"),
    ("Pay attention to on-screen prompts", "留意屏幕上的提示"),
    ("Save often so you never lose progress", "经常保存，进展永不丢失"),
    ("Upgrade your abilities to make fights easier", "升级能力让战斗更轻松"),
    ("Store your favorite vehicles in the garage", "把爱车存进车库"),
    ("Try different weapons to find your favorite", "多试几种武器找到爱用款"),
    ("Claim your reward after finishing a mission", "完成任务后记得领取奖励"),
    ("Dodge when enemies wind up their attacks", "敌人蓄力攻击时闪避"),
    ("You can change the difficulty at any time", "难度随时可以更改"),
    ("Take the high ground for a better view", "抢占高处获得更好视野"),
    ("Money buys gear, weapons and property", "金钱能买到装备、武器和产业"),
    ("Money buys gear, weapons and property", "金钱能买到装备、武器和产业"),
    ("Park in a safe spot before getting out", "下车前先把车停在安全的地方"),
    ("Watch the time limits on timed missions", "注意限时任务的倒计时"),
    ("Each gang fights with a different style", "每个帮派都有各自的战斗风格"),
    ("Explore the city to find hidden content", "探索城市寻找隐藏内容"),
    ("Finishing missions unlocks new weapons", "完成任务可解锁新武器"),
    ("Keep moving so enemies cannot surround you", "不停移动，别被敌人包围"),
    ("Use binoculars to mark distant targets", "用望远镜标记远处目标"),
    ("Find health packs to heal after a fight", "找补血包在战斗后回复"),
    ("Use vehicles to travel across the city fast", "用载具快速穿越城市"),
    ("Weather affects how your car handles", "天气会影响车辆操控"),
    ("Store important vehicles in your garage", "把重要载具存进车库"),
    ("Finish mission chains to unlock the story", "完成任务链解锁剧情"),
    ("Open the options menu any time to adjust settings", "随时打开选项菜单调整设置"),
]

raw = open(P, 'rb').read()
assert hashlib.md5(raw).hexdigest() == BASE, 'baseline mismatch'
orig = raw

# 定位 LOADING_SCREEN_TIPS 数组区块
m = re.search(rb'LOADING_SCREEN_TIPS\s*=\s*\{', raw)
assert m, 'array not found'
start = m.end()
end = raw.find(b'}', start)
assert end > 0
block = raw[start:end]
print('数组区块: %d..%d  (%d B)' % (start, end, len(block)))

# 逐行替换
lines = block.split(b'\n')
n = 0
out_lines = []
lookup = {}
for en, cn in TIPS:
    lookup[en.encode('utf-8')] = cn.encode('utf-8')

for ln in lines:
    s = ln.strip()
    m2 = re.match(rb'^"([^"]*)",?$', s)
    if m2 and m2.group(1) in lookup:
        cn = lookup[m2.group(1)]
        indent = ln[:len(ln) - len(ln.lstrip())]
        tail = b',' if s.endswith(b',') else b''
        newln = indent + b'"' + cn + b'"' + tail
        out_lines.append(newln)
        n += 1
    else:
        out_lines.append(ln)

newblock = b'\n'.join(out_lines)
assert newblock != block

# 只替换该区块
out = raw[:start] + newblock + raw[end:]

# 断言：除该区块外完全一致
assert out[:start] == raw[:start], '前缀被改'
assert out[start + len(newblock):] == raw[end:], '后缀被改'
# 换行风格不变
assert out.count(b'\n') == raw.count(b'\n'), '换行数变了'
assert out.count(b'\r') == raw.count(b'\r')
# 数组结构不变
assert out.count(b'LOADING_SCREEN_TIPS') == raw.count(b'LOADING_SCREEN_TIPS')
assert out.count(b'LAST_MISSION_NAMES') == raw.count(b'LAST_MISSION_NAMES')

open(P, 'wb').write(out)
print()
print('已汉化提示:', n, '条')
print('size', len(raw), '->', len(out))
print('new md5', hashlib.md5(out).hexdigest())

# 回读校验
txt = out.decode('utf-8')
i = txt.index('LOADING_SCREEN_TIPS')
j = txt.index('}', i)
arr = txt[i:j]
zh = len(re.findall(r'[\u4e00-\u9fff]', arr))
en_left = re.findall(r'"([A-Za-z][A-Za-z0-9 ,.\'-]{10,})"', arr)
print()
print('区块内中文字符数:', zh)
print('残留长英文句:', en_left if en_left else '无')