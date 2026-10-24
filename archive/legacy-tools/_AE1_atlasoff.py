# -*- coding: utf-8 -*-
import sys, struct, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp
from _img import dxt3_decode, crop_png, write_png

OFF = Vpp(r"F:\sr2-cn\_backup_E\textures.official_20261013_174215.vpp_pc")
NEW = Vpp(r"G:\SteamLibrary\steamapps\common\Saints Row 2\textures.vpp_pc")

def atlas(v, name='fnt_chinese'):
    for e in v.entries():
        if e['name'] == name and e['size'] == 4194304:
            return v.read(e)
    return None

ao = atlas(OFF)
an = atlas(NEW)
print("official atlas md5-ish:", len(ao))
pxo = dxt3_decode(ao, 2048, 2048)
pxn = dxt3_decode(an, 2048, 2048)

P = 65
IDX = [403, 371, 336, 1868, 1067, 454, 364]
for tag, px in (('OFF', pxo), ('NEW', pxn)):
    for i in IDX:
        x, y = 1 + 31 * (i % P), 1 + 31 * (i // P)
        crop_png(px, 2048, 2048, x, y, 30, 30, 5, r'F:\sr2-cn\_OFC_%s_%04d.png' % (tag, i))
print("done crops")
