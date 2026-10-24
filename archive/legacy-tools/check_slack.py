# -*- coding: utf-8 -*-
"""检查每条待改记录后方的可用余量（缩短改法可行性的前提）"""
import struct, sys, json
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
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

v = Vpp(G + 'patch.vpp_pc')
blob = v.read(v.find('static_CH', 'le_strings'))

plan = json.load(open('F:/sr2-cn/_plan_places.json', encoding='utf-8'))

print('%-8s %-8s %-22s %-14s %s' % ('offset', '现slot', '英文', '中文', '判定'))
print('-' * 110)
ok = 0
for off, h, en, cn, ln, dup, miss in plan:
    # 记录起点 = off, 记录 = [ID 2slot][文本 ln slot][0000]
    text_at = off + 4
    term_at = text_at + ln * 2
    # 前置断言
    assert blob[term_at:term_at + 2] == b'\x00\x00', (hex(off), blob[term_at:term_at + 2])
    # 后一条记录起点（= 下一个 0000 之后）
    nxt = term_at + 2
    # 往后找下一个记录 ID：跳过 0000，然后应是 2 slot ID + 文本
    # 判断余量：新文本更短 => 可以把多余 slot 填成 0000 提前终止
    delta = ln - len(cn)
    if delta > 0:
        verdict = '缩短%d slot：尾部填0000即可（不改表结构）' % delta
        ok += 1
    else:
        verdict = '★需扩容 %d slot' % (-delta)
    print('%-8X %-8d %-22s %-14s %s' % (off, ln, repr(en)[:20], cn, verdict))

print()
print('可缩短的:', ok, '/', len(plan))

# 确认这些记录是否在表外松散区也有副本（双副本陷阱）
print()
print('=== 双副本检查（整文件字节搜索）===')
def S(ch):
    for i, cp in enumerate(CL):
        if cp == ord(ch):
            return struct.pack('>H', i + 0x20)
    raise KeyError(ch)

def pack(s):
    return b''.join(S(c) for c in s)

seen = {}
for off, h, en, cn, ln, dup, miss in plan:
    pat = pack(en) + b'\x00\x00'
    idx = blob.count(pat)
    if idx > 1:
        seen.setdefault(en, idx)
if seen:
    for k, n in seen.items():
        print('  %-22s 在表内出现 %d 次（需全改）' % (repr(k)[:22], n))
else:
    print('  无同文多副本（每条英文在 static_CH 内唯一出现）')