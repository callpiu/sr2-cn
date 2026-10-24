"""diag27.py -- 从 v532 备份还原被误改的捷克/波兰表记录 (29823632, 37646448)"""
import sys, struct
sys.path.insert(0, r'F:\sr2-cn')

P   = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
BAK = P + '.v532_before_exp.bak'

cur = bytearray(open(P, 'rb').read())
bak = open(BAK, 'rb').read()
print('cur size', len(cur), 'bak size', len(bak))

# (blob_base, rec_abs, hash) to restore from bak
RESTORE = [
    (29823632, 29914216, 0x84F287ED),
    (29823632, 29914354, 0x10AF1E62),
    (37646448, 37740028, 0x10AF1E62),
]

def rec_len(buf, ra):
    o = ra + 4; n = 0; g = 0
    while o + 2 <= len(buf) and g < 8000:
        u = struct.unpack_from('>H', buf, o)[0]; o += 2; n += 2; g += 1
        if u == 0: break
    return 4 + n

for base, ra, h in RESTORE:
    L = rec_len(bak, ra)
    orig = bak[ra:ra + L]
    cur[ra:ra + L] = orig
    print('restored rec@%d (blob@%d) hash=%08X len=%d' % (ra, base, h, L))

open(P, 'wb').write(bytes(cur))
print('written, md5 =', __import__('hashlib').md5(bytes(cur)).hexdigest())

# 验证: 用 direct-decode 看外国块是否恢复为捷克/波兰
def direct(rec_abs):
    o = rec_abs + 4; s = ''; g = 0
    while o + 2 <= len(cur) and g < 4000:
        u = struct.unpack_from('>H', cur, o)[0]; o += 2; g += 1
        if u == 0: break
        s += chr(u) if u < 0x10000 else '?'
    return s
for base, ra, h in RESTORE:
    print('rec@%d -> %r' % (ra, direct(ra)))
