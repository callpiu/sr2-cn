# -*- coding: utf-8 -*-
import sys, struct, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

MAGIC_VPP = bytes([0xCE, 0x0A, 0x89, 0x51, 0x04])
ROOT = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
KEYS = ('fnt_chinese', 'fnt_body_n', 'nobdr', 'charlist', 'platform_PC_CH')
for dp, dn, fn in os.walk(ROOT):
    for f in fn:
        if not f.lower().endswith('.vpp_pc'):
            continue
        p = os.path.join(dp, f)
        try:
            d = bytearray(open(p, 'rb').read())
        except Exception:
            continue
        if d[:5] != MAGIC_VPP:
            continue
        o = 5 + 0x14F
        num, cs, lo, lf, le = struct.unpack_from('<iiiii', d, o)
        names_at = ((0x800 + lo) & 0xFFFFF800) + 0x800
        ext_at = ((names_at + lf) & 0xFFFFF800) + 0x800
        data_start = ((ext_at + le) & 0xFFFFF800) + 0x800
        def strz(base, pos):
            e = d.find(b'\x00', base + pos)
            return d[base + pos:e].decode('ascii', 'replace')
        for i in range(num):
            e = 0x800 + i*28
            a, b, c, dd, ln, m1, z = struct.unpack_from('<IIiiiii', d, e)
            nm = strz(names_at, a); ex = strz(ext_at, b) if b else ''
            full = (nm + '.' + ex).lower()
            if any(k in full for k in KEYS):
                print("%-16s %4d %-22s %-10s %d" % (os.path.basename(p), i, nm, ex, ln))
