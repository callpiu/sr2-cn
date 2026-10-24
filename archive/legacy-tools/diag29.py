# -*- coding: utf-8 -*-
# diff broken exp file vs clean v532: what exactly changed?
import sys, struct
sys.path.insert(0, 'F:/sr2-cn')

V532 = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc.v532_before_exp.bak'
BRK  = r'F:\sr2-cn\_broken_exp1.vpp_pc'

a = open(V532, 'rb').read()
b = open(BRK, 'rb').read()
print('sizes:', len(a), len(b), 'delta:', len(b) - len(a))

# find differing regions in common prefix
n = min(len(a), len(b))
regions = []
i = 0
while i < n:
    if a[i] != b[i]:
        j = i
        while j < n and (a[j] != b[j] or (j - i) < 16):
            j += 1
        # extend while differing within small gaps
        regions.append((i, j))
        i = j
    else:
        i += 1
print('differing regions in common prefix:', len(regions))
for s, e in regions[:20]:
    print(f'  0x{s:08X}..0x{e:08X}  len={e-s}')
    print('    v532:', a[s:s+32].hex())
    print('    brok:', b[s:s+32].hex())

# tail beyond v532 size
if len(b) > len(a):
    tail = b[len(a):]
    print('tail len:', len(tail), 'head hex:', tail[:64].hex())
