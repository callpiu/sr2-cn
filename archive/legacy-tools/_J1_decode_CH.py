# -*- coding: utf-8 -*-
"""用项目权威 sr2strings 解码 CH 表，定位直升机突击字幕记录。"""
import sys, os, struct
sys.path.insert(0, 'F:/sr2-cn')
from sr2strings import StringsFile, CharList
from sr2lib import Vpp

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v = Vpp(os.path.join(G, 'patch.vpp_pc'))

# charlist_CH.txt: 第一行是总数吗？
txt = v.read(v.find('charlist_CH', 'txt')).decode('utf-8')
nums = []
for tok in txt.split():
    if tok.lstrip('-').isdigit():
        nums.append(int(tok))
print('charlist raw nums=%d  head=%s' % (len(nums), nums[:5]))
# 第一行若是总数则跳过
if nums and nums[0] == len(nums) - 1:
    nums = nums[1:]
CL = CharList(nums)
print('CL.body len=%d  first=%s' % (len(CL.body), CL.body[:8]))

# static_CH
raw = v.read(v.find('static_CH', 'le_strings'))
sf = StringsFile(data=raw)
print('static_CH: ver=%d buckets=%d count=%d offsets_at=%d' % (sf.ver, sf.buckets, sf.count, sf.offsets_at))
recs = sf.all_records(CL)
print('可解码记录数=%d' % len(recs))

# 找含"直升机""突击""弟兄们""保护"的记录
KEYS = ['直升机', '突击', '弟兄们', '保护', '你的', '停靠', '面包车']
for i, off, t, L in recs:
    if any(k in t for k in KEYS):
        print('  [i=%5d off=%7d L=%3d] %s' % (i, off, L, t[:80]))
