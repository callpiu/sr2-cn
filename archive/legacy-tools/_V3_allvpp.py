# -*- coding: utf-8 -*-
import sys, struct, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

MAGIC_VPP = bytes([0xCE, 0x0A, 0x89, 0x51, 0x04])
ROOT = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
out = []
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
            body = data_start + dd
            if ln < 500 or ln > 200000:
                continue
            head = bytes(d[body:body+400])
            if b'ENDOFFILE' in head or ('charlist' in (nm+ex).lower()):
                out.append((p, nm, ex, ln))
for p, nm, ex, ln in out:
    print("%-24s %-16s %-8s %d" % (os.path.basename(p), nm, ex, ln))
print("total", len(out))
