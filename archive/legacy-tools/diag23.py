"""diag23: manually parse the VPP entry array (bypass Vpp class) and list EVERY
entry whose name contains 'static'/'voice', with raw body offset + size, to
detect DUPLICATE static_CH entries (game may read a different one than find()).
Also dump raw 28-byte entry fields for static_CH in current vs v532 backup."""
import sys, struct, os
sys.path.insert(0, r'F:\sr2-cn')

MAGIC_VPP = bytes([0xCE, 0x0A, 0x89, 0x51, 0x04])

def load(path):
    d = bytearray(open(path, 'rb').read())
    assert d[:5] == MAGIC_VPP
    o = 5 + 0x14F
    num, csize, lo, lf, le = struct.unpack_from('<iiiii', d, o)
    names_at = ((0x800 + lo) & 0xFFFFF800) + 0x800
    ext_at = ((names_at + lf) & 0xFFFFF800) + 0x800
    data_start = ((ext_at + le) & 0xFFFFF800) + 0x800
    return d, num, names_at, ext_at, data_start

def strz(d, base, pos):
    e = d.find(b'\x00', base + pos)
    return d[base + pos:e].decode('ascii', 'replace')

def entries(d, num, names_at, ext_at):
    out = []
    for i in range(num):
        e = 0x800 + i * 28
        a, b, c, body, size, m1, z = struct.unpack_from('<IIiiiii', d, e)
        out.append((i, strz(d, names_at, a), strz(d, ext_at, b) if b else '',
                    c, body, size, m1, z, e))
    return out

for label, path in [('CURRENT(exp)', r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'),
                    ('v532_before_exp', r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc.v532_before_exp.bak')]:
    d, num, names_at, ext_at, data_start = load(path)
    ents = entries(d, num, names_at, ext_at)
    print('\n===== %s  (num entries=%d, data_start=%d, filesize=%d) =====' % (label, num, data_start, len(d)))
    sc = [x for x in ents if 'static_ch' in x[1].lower() or 'voice_script_ch' in x[1].lower()]
    print('static/voice entries found:', len(sc))
    for (i, name, ext, c, body, size, m1, z, eoff) in sc:
        absoff = data_start + body
        print('  idx=%-4d %-18s ext=%-11s c=%-3d body=%-10d absOff=%-10d size=%-8d m1=%-3d z=%-3d'
              % (i, name, ext, c, body, absoff, size, m1, z))
    # dump raw 28 bytes of each static_CH entry
    for (i, name, ext, c, body, size, m1, z, eoff) in sc:
        if name.lower() == 'static_ch':
            raw = bytes(d[eoff:eoff+28])
            print('  RAW static_CH entry bytes:', raw.hex())
