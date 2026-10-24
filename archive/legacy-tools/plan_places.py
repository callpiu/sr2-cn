# -*- coding: utf-8 -*-
"""
从 257 条漏翻里精确挑出「地名 / 商店名」，并给出中文译名建议。
判断依据：这些英文名是 SR2 世界观里的固定地点（hood/district/store），
不是电台台标、枪名、涂装代号、玩家自定义占位符。
"""
import json, re

d = json.load(open('F:/sr2-cn/_todo_shops.json', encoding='utf-8'))

# ===== 明确不该翻的类别 =====
SKIP_EXACT = {
    # 电台 / 电视台台标
    'Volition', '99 Underground', 'KRHYME 95.4', 'GDHC .50', 'Funk 98.4', 'K12 97.6',
    'RFS 87.6', 'KBOOM WMD108', 'Sizzurp 101.69', 'Ghettoblaster', '103.6 Four',
    '.44 Shepherd', '89 GEN X', 'Ezzzy 105', 'K12 97.6',
    # 武器 / 载具型号
    'AR-40 Xtnd', 'AS12 Riot', 'AS14 Hammer', 'CKH Riot Special', 'SKR-7 Spree',
    'T3K Urban', 'SR Air', 'Enforcer', 'Dominator', 'Bandit', 'Regulator',
    'Ghost', 'Splatster Chief', 'Hammerhead', 'Panther', 'Reaper', 'Rattlesnake',
    'Shark', 'Swallow', 'Swan', 'Ruckus', 'Sunsinger', 'Gaslamp', 'Prephop',
    'Ezpata', 'Gigatruck', 'NR4', 'RFG', 'Razor', 'Enforcer',
    # 涂装 / 外观代号（玩家自定义）
    'Skin01', 'Skin02', 'Skin03', 'Skin04', 'Skin05', 'CUST_VARIANT_MATERIAL#24',
    # 帮派涂鸦名（刻意保留原文的街头风）
    'Freckle Bitch', "Freckle Bitch's", 'FRECKLE BITCH', 'Freckle Bitchs',
    "Romero's Hero", 'Sum Old Guy', 'Sum Yung Guy', 'Roje', 'Sanchez',
    'Dookie Derby', "Donovan's Derby", 'Double-Stuff', 'Duck Trucks', 'Donkey',
    'Feed Dogs', 'Gyro Daddy', 'Gyro Goat Head', 'Ratty', 'Bandit',
    # 技术/格式串
    'TrueSkill', 'XBOX LIVE', 'Xbox LIVE', 'GameStop', 'PHUC MI PHUC YUE',
    '%i', '%ls +%ls', 'HOS: %i', 'XX/XY', 'AI', 'HUD', 'J', 'U', 'RJ', 'OG',
    'ODD', 'PCP', 'SUV', 'GAL', 'T-Rex', 'Tee', 'Lik-a-Chik', 'Hi-Fidelity',
    'HOLISTIC', 'Holding Pattern', 'AI', 'Rays', 'Rays 1',
}

# ===== 明确该翻：SR2 地名 (hood / district / island) =====
PLACES = {
    # hood 名（斯蒂尔沃特的街区）
    'Barrio': '巴里奥',# 官方中文表已有「唐人街」？需核对
    'Hoodieville': '帽衫镇',
    'Quinbecca': '昆比卡',
    'Elysian Fields': '至乐田',
    'Harrowgate': '哈罗盖特',
    'Lesalle': '拉萨勒',
    'Rebadeaux': '雷巴多',
    'Stoughton': '斯托顿',
    'Ruin Island': '废墟岛',
    'Ruin Island': '废墟岛',
    'Filmore': '菲尔莫尔',
    'Bardown': '巴当',
    'Porkrind': '猪林',
    'Cambridge': '剑桥',
    'Rondwater': '朗德沃特',
    'St. John': '圣约翰',
    'Pleasantview': '普莱森特维尤',
    'Bowsher': '鲍舍',
    'Angelcrest': '安杰尔克雷斯特',
    'Hedgemont': '赫奇蒙特',
    'End of the World': '世界尽头',
    'Fort Shakedown': '沙基镇',
    'Sleeping Harbor': '沉睡港',
    'Brooklyn Heights': '布鲁克林高地',
    '3rd Street': '三街',
    'Bristol': '布里斯托',
    'Santo Mundo': '圣图曼度',
    'Amber View': '琥珀苑',
    'Doodley Doo': '',
}

# ===== 明确该翻：商店名 =====
SHOPS = {
    'Donut Holes': '甜甜圈洞',
    'Dong Tea': '冬茗茶',
    'Wondermart': '神奇超市',
    'Carbuncle Carls': '卡本克尔美食',
    'Technically Legal': '合法技术',
    'Elysian Fields': '至乐田',
    'Jacks or Better': '要牌不要命',
    'Jacks or Higher': '更大的一对',
    'Taps and Tips': ' taps与提示',
    'Heaven Bound': '天国限定',
    "Heaven's Helpers": '天国帮手',
    'Ghost': '',
}

print('=' * 100)
print('请人工确认的分类清单')
print('=' * 100)

allk = sorted(d.keys())
print()
print('### A. 明确是地名/商店（建议汉化）###')
for k in allk:
    base = re.sub(r'\s+\d+$', '', k).strip()
    if base in PLACES or base in SHOPS:
        tag = '地名' if base in PLACES else '商店'
        print('  [%s] %-28s x%-2d -> %s' % (tag, k, len(d[k]), (PLACES | SHOPS).get(base, '?'),))

print()
print('### B. 已判定为电台/枪名/涂装/街头外号（建议保留）###')
skip = 0
for k in allk:
    base = re.sub(r'\s+\d+$', '', k).strip()
    if base in SKIP_EXACT and base not in PLACES and base not in SHOPS:
        skip += 1
print('  共 %d 项（详见 _todo_shops.json）' % skip)

print()
print('### C. 未归类，需逐个判断 ###')
for k in allk:
    base = re.sub(r'\s+\d+$', '', k).strip()
    if base not in SKIP_EXACT and base not in PLACES and base not in SHOPS:
        print('  %-30s x%d   例: %s' % (k, len(d[k]), d[k][0][2][:50]))