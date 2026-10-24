# -*- coding: utf-8 -*-
"""检查待改记录的字数与可用余量"""
import struct, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))
IDX = {}
for i, cp in enumerate(CL):
    IDX.setdefault(cp, i)

def D(sl):
    return ''.join(chr(CL[x - 0x20]) if 0x20 <= x - 0x20 < len(CL) else '^%02X' % x for x in sl)

def scan(b):
    res = []; i = 0; n = len(b)
    while i + 2 <= n:
        j = i; out = []
        while j + 2 <= n:
            x = struct.unpack_from('>H', b, j)[0]
            if x == 0: break
            out.append(x); j += 2
            if len(out) > 600: break
        if out: res.append((i, out)); i = j + 2
        else: i += 2
    return res

v = Vpp(G + 'patch.vpp_pc')
CH = scan(v.read(v.find('static_CH', 'le_strings')))

# (ID, 现中文, 新中文)
PLAN = [
    (0x7B506169, '大飞燕', '大杯可乐'),   # Big Swallow = 可乐
    (0xAA0A5EB8, '拳头',   '巨无霸'),     # The Fist = 巨型汉堡
    (0xDC924324, '鸡胸',   '鸡米花'),     # Chicken Bazooms = 炸鸡块
    (0x8BC04EFE, 'Swallow', '燕子'),     # 载具名
]

print('=== 字表可用性 ===')
for _, _, cn in PLAN:
    miss = [c for c in cn if ord(c) not in IDX]
    print('  %-10s %s' % (cn, 'OK' if not miss else '★缺字:' + ''.join(miss)))

print()
print('=== 记录定位与余量 ===')
for h, old, new in PLAN:
    rows = [(off, o) for off, o in CH if len(o) > 2 and ((o[0] << 16) | o[1]) == h]
    for off, o in rows:
        txt = D(o[2:])
        n = len(o) - 2
        # 余量：文本后面还有多少 slot 直到 0000 之后的空隙
        # 记录是紧凑排列的，term 紧跟 0000
        delta = len(new) - len(old)
        flag = '缩短%d' % (-delta) if delta < 0 else ('等长' if delta == 0 else '★需扩容 %d' % delta)
        print('  %08X ID=%08X slot=%-3d %-10r -> %-10r  %s'
              % (off, h, n, txt[:14], new, flag))
    if not rows:
        print('  ID=%08X ★未找到' % h)