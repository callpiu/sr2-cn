# -*- coding: utf-8 -*-
import struct, os, sys, json
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
for vppname in ['patch.vpp_pc', 'common.vpp_pc']:
    v = Vpp(os.path.join(G, vppname))
    for fname, fext in [('charlist_CH', 'txt'), ('charlist_CH', 'cxt')]:
        e = v.find(fname, fext)
        if e:
            raw = v.read(e)
            print('=== %s :: %s.%s  size=%d ===' % (vppname, fname, fext, len(raw)))
            print('hex head:', raw[:32].hex())
            try:
                lines = raw.decode('utf-8').split('\n')
                nums = [l for l in lines if l.strip().isdigit()]
                print('lines=%d  numeric_lines=%d' % (len(lines), len(nums)))
                print('first 8:', lines[:8])
                print('idxs 0..12:', nums[:13])
                if len(nums) >= 240:
                    print('idx 220..232:', nums[220:233])
            except Exception as ex:
                print('decode err', ex)
            print()
