# -*- coding: utf-8 -*-
"""关键验证：同一 hash 在 static_US 与 static_CH 中的 unit 序列对比。
US 是英文原文（ASCII），CH 应是中文。若 CH 的 unit 值 == US 的 unit 值，
说明 CH 表根本没翻译；若 CH unit 用同一 charlist 解出乱码，则 charlist 不匹配。
"""
import sys, struct, os
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp
from sr2strings import CharList

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v = Vpp(G + '/patch.vpp_pc')
txt = v.read(v.find('charlist_CH', 'txt')).decode()
ns = [int(t) for t in txt.split() if t.lstrip('-').isdigit()]
if ns and ns[0] == len(ns) - 1:
    ns = ns[1:]
CL = CharList(ns)

def recs_units(raw):
    magic, ver, buckets, count = struct.unpack_from('<IHHI', raw, 0)
    off_at = 16 + buckets * 8
    d = {}
    for i in range(count):
        o = struct.unpack_from('<I', raw, off_at + i * 4)[0]
        if not (0 <= o < len(raw) - 4):
            continue
        h = struct.unpack_from('<H', raw, o)[0]
        p = o + 4
        units = []
        while p + 1 < len(raw):
            u = struct.unpack_from('>H', raw, p)[0]
            p += 2
            if u == 0:
                break
            units.append(u)
            if len(units) > 800:
                break
        d.setdefault(h, units)
    return d

US = recs_units(open(G + '/Mods/static_US.le_strings', 'rb').read())
CH = recs_units(v.read(v.find('static_CH', 'le_strings')))
print('US recs=%d  CH recs=%d' % (len(US), len(CH)))

common = [h for h in US if h in CH]
print('共有 hash=%d' % len(common))

def dec_cp(units):
    # 纯 ASCII 视角（unit 即为 codepoint）
    return ''.join(chr(u) if u < 0x100 else '.' for u in units)

def dec_cl(units, cl):
    return ''.join(chr(u) if u < 0x100 else (chr(cl.body[u]) if u < len(cl.body) else '?') for u in units)

shown = 0
for h in common:
    us, ch = US[h], CH[h]
    if len(us) < 6:
        continue
    print('h=%04X' % h)
    print('   US(ascii) %-50r  units=%s' % (dec_cp(us)[:50], us[:10]))
    print('   CH(cl)    %-50r  units=%s' % (dec_cl(ch, CL)[:50], ch[:10]))
    shown += 1
    if shown >= 8:
        break
