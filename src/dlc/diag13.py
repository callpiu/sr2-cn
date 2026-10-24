# -*- coding: utf-8 -*-
"""诊断：DLC 中文显示空白 —— 检查译文用字是否在第三方字表内
已知实测：
  显示正常: 击杀乌托尔 / 注意 / 好
  显示空白: 已回收尸体： / 台词字幕 / 击杀[乌托尔守卫] 任务提示
"""
import sys, io, struct
sys.path.insert(0, r'F:/sr2-cn')
from sr2lib import Vpp
from rebuild4 import load, G

# ---- 1. 提取第三方字表（游戏目录 patch.vpp_pc 的 charlist_CH）----
v = Vpp(r'G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc')
e = [x for x in v.entries() if x['name'].lower() == 'charlist_ch'][0]
raw_cl = v.read(e)
# 第三方格式：纯码点行，无头
cps = [int(l) for l in raw_cl.decode('utf-8').split('\n') if l.strip().isdigit()]
cps_set = set(cps)
print('第三方字表项数:', len(cps))

# ---- 2. 已部署 DLC 表逐条检查字形覆盖 ----
raw, N, A0, T0, buckets, arr, ents = load(G + 'dlc_ch.le_strings')
du = load(G + 'dlc_us.le_strings')[-1]
du = dict(du)

def missing_chars(t):
    bad = []
    for c in t:
        o = ord(c)
        if o < 0x80:            # ASCII 一定有
            continue
        if c in '\n\t':
            continue
        if o not in cps_set:
            bad.append(c)
    return bad

ok_cnt = bad_cnt = 0
bad_list = []
for h, t in ents:
    bad = missing_chars(t)
    if bad:
        bad_cnt += 1
        bad_list.append((h, t, bad))
    else:
        ok_cnt += 1
print('零缺字条目 %d / 有缺字条目 %d / 共 %d' % (ok_cnt, bad_cnt, N))

# ---- 3. 交叉验证用户实测结果 ----
print('\n--- 用户实测对照 ---')
for label, h in [('击杀乌托尔守卫(任务提示,空白)', 0x3342D5FC),
                 ('已回收尸体：(HUD,空白)', 0x0E58435C),
                 ('台词22C8F187(字幕,空白)', 0x22C8F187),
                 ('台词19914873(字幕,空白)', 0x19914873)]:
    t = dict(ents)[h]
    print('%-32s 缺字=%s' % (label, missing_chars(t)))
    print('   文本: %s' % t[:60])

# 「击杀乌托尔」「注意」「好」在哪？
print('\n--- 定位实测正常的中文串 ---')
for h, t in ents:
    core = t.replace(' ', '')
    if '击杀乌托尔' in core.replace('[format][color:red]', '').replace('[/format]', ''):
        print('击杀乌托尔@%08X 缺字=%s 文本=%s' % (h, missing_chars(t), t[:60]))
    if core in ('注意', '好') or core.endswith('注意') or core.endswith('好'):
        print('短中文@%08X 缺字=%s 文本=%r' % (h, missing_chars(t), t))

# ---- 4. 缺字统计汇总 ----
from collections import Counter
cc = Counter()
for h, t, bad in bad_list:
    cc.update(bad)
print('\n--- 缺字频率 TOP30（共 %d 种）---' % len(cc))
for c, n in cc.most_common(30):
    print('  U+%04X %s ×%d' % (ord(c), c, n))
print('\n缺字条目示例(前12):')
for h, t, bad in bad_list[:12]:
    print('  %08X 缺%s | %s' % (h, ''.join(bad), t[:50]))
