# -*- coding: utf-8 -*-
import struct, hashlib, sys, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
P = G + 'patch.vpp_pc'
new = open(P, 'rb').read()
ob = open(G + 'patch.vpp_pc.before_v541.bak', 'rb').read()

print('md5', hashlib.md5(new).hexdigest())
print('size', len(new), '== old', len(ob), len(new) == len(ob))
diff = [i for i in range(len(new)) if new[i] != ob[i]]
print('diff bytes', len(diff))

CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))

def D(slots):
    out = []
    for x in slots:
        if x == 0: break
        if x < 0x20: out.append('\x01')
        elif x - 0x20 < len(CL): out.append(chr(CL[x - 0x20]))
        else: out.append('?')
    return ''.join(out)

def scan(b):
    res = []; i = 0; n = len(b)
    while i + 2 <= n:
        j = i; out = []
        while j + 2 <= n:
            x = struct.unpack_from('>H', b, j)[0]
            if x == 0: break
            out.append(x); j += 2
            if len(out) > 800: break
        if out: res.append((i, out)); i = j + 2
        else: i += 2
    return res

v = Vpp(P)
CH = scan(v.read(v.find('static_CH', 'le_strings')))
print('CH records', len(CH), '(before_v541 应为 14595)')

# 1) 目标英文应 0 残留
TARGETS = ['Barrio', '3rd Street 1', '3rd Street 2', 'Adept Way', 'Hackenshack',
           'Harrowgate', 'Hoodieville', 'Quinbecca', 'Elysian Fields', 'Lesalle',
           'Rebadeaux', 'Stoughton', 'Ruin Island', 'Filmore', 'Wondermart 1',
           'Carbuncle Carls', 'Technically Legal', 'Donut Holes', 'Dong Tea',
           'Jacks or Better', 'Jacks or Higher', 'Heaven Bound',
           "Heaven's Helpers", 'Taps and Tips', 'Fox Drive']

allt = []
for off, o in CH:
    if len(o) > 2:
        allt.append((off, (o[0] << 16) | o[1], D(o[2:])))

print()
print('=== 目标英文残留检查（CH 表内）===')
bad = 0
for t in TARGETS:
    hits = [(o, h) for o, h, x in allt if x == t]
    if hits:
        bad += 1
        print('   ★仍残留 %-22s %s' % (t, [hex(o) for o, h in hits]))
print('   残留项数:', bad, '/', len(TARGETS))

print()
print('=== 新中文译名回读 ===')
CN = ['唐人街', '三街 1', '三街 2', '环能路', '哈根沙克', '哈罗盖特', '帽衫镇',
      '昆比卡', '至乐田', '拉萨勒', '雷巴多', '斯托顿', '废墟岛', '菲尔莫尔',
      '神奇超市 1', '红宝石卡尔', '法律边缘', '甜甜圈洞', '凉茶', '好牌优于一切',
      '更大的对子', '天堂限定', '天堂助手', '啤酒与小费', '狼径']
for c in CN:
    hits = [(o, x) for o, h, x in allt if x == c]
    print('   %-14s %d 条  %s' % (c, len(hits), [hex(o) for o, x in hits][:3]))

print()
print('=== v538/v539 回归 ===')
for kw, lo in [('市郊', 30), ('霰弹枪', 10), ('弹药', 10), ('三街圣徒', 10),
               ('兄弟会', 10), ('主城区', 10), ('父亲', 15), ('注意', 2), ('取消', 5)]:
    n = sum(1 for o, h, x in allt if kw in x)
    flag = 'OK' if n >= lo else '★★低于预期'
    print('   %-8s %-5d %s' % (kw, n, flag))

print()
print('=== 其它语言表完整性（US/DK/SE/FR/JP 等应仍为英文原文）===')
v2 = Vpp('F:/sr2-cn/_ref_第三方补丁/原始基准/patch_第三方原版.vpp_pc')
us = v2.read(v2.find('static_US', 'le_strings'))
usl = bytes(us)
for t in ['Barrio', 'Elysian Fields', 'Technically Legal', 'Wondermart 1']:
    n = new.count(t.encode('utf-16-be'))
    print('   整文件 %-22s slot 命中 %d（US 表内应为 %d）' % (t, n, usl.count(t.encode('utf-16-be'))))

# 精确断言：其它语言表的 byte 区间与基线一致
v3 = Vpp(P)
ds = v3.data_start if hasattr(v3, 'data_start') else 0x9000
obuf = ob
changed_entries = set()
for e in v3.entries():
    a = ds + e['body']; b = a + e['size']
    if new[a:b] != obuf[a:b]:
        changed_entries.add(e['name'] + '.' + e['ext'])
print()
print('★ 实际被修改的条目:', sorted(changed_entries))