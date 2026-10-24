# -*- coding: utf-8 -*-
"""官方 charlist vs 汉化 charlist 对照 + le_strings 双解码"""
import struct, sys, os
sys.path.insert(0, r'F:\sr2-cn')
from _vpp import Vpp

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2'

def parse_charlist_bytes(b):
    txt = b.decode('latin1')
    codes, count = [], None
    for line in txt.replace('\r\n', '\n').split('\n'):
        line = line.strip()
        if not line or line.startswith('/'):
            continue
        if line.startswith('count='):
            count = int(line.split('=')[1]); continue
        codes.append(int(line))
    return codes, count

def build(codes):
    c2u, u2c, nxt = {}, {}, 0x100
    for u in codes:
        if u < 256:
            c2u[u] = u; u2c[u] = u
        else:
            c2u[nxt] = u; u2c[u] = nxt; nxt += 1
    return c2u, u2c, nxt

def get_charlist(path, vppname):
    v = Vpp(path)
    for e in v.entries():
        if e['name'].lower() == 'charlist_ch':
            return v.read(e)
    return None

mod_b = get_charlist(os.path.join(GAME, 'patch.vpp_pc'), 'patch')
off_b = get_charlist(r'F:\sr2-cn\vpp_backup\patch.vpp_pc.orig', 'orig')
mod_codes, mod_cnt = parse_charlist_bytes(mod_b)
off_codes, off_cnt = parse_charlist_bytes(off_b)
print("modder charlist: %d entries (declared %s)" % (len(mod_codes), mod_cnt))
print("official charlist: %d entries (declared %s)" % (len(off_codes), off_cnt))

mc2u, mu2c, mnext = build(mod_codes)
oc2u, ou2c, onext = build(off_codes)
print("modder compressed 0x100..0x%X ; official 0x100..0x%X" % (mnext-1, onext-1))

# 两个表的差异
same = 0
diffs = []
for i in range(min(len(mod_codes), len(off_codes))):
    if mod_codes[i] == off_codes[i]:
        same += 1
    else:
        diffs.append(i)
print("\n前 %d 项中相同的: %d, 不同的: %d" % (min(len(mod_codes), len(off_codes)), same, len(diffs)))
print("第一个不同的下标:", diffs[:5])
for i in diffs[:10]:
    print("   idx %-5d official=U+%04X %s   modder=U+%04X %s" %
          (i, off_codes[i], chr(off_codes[i]) if off_codes[i] > 31 else '?',
           mod_codes[i], chr(mod_codes[i]) if mod_codes[i] > 31 else '?'))

def parse_lestrings(data):
    magic, ver, buckets, count = struct.unpack_from('<IHHI', data, 0)
    assert magic == 0xA84C7F73
    recs = []
    for b in range(buckets):
        o = 0x0C + b * 8
        bc, boff = struct.unpack_from('<II', data, o)
        for k in range(bc):
            roff = struct.unpack_from('<I', data, boff + k * 4)[0]
            h = struct.unpack_from('>I', data, roff)[0]
            slots, p = [], roff + 4
            while True:
                val = struct.unpack_from('>H', data, p)[0]; p += 2
                if val == 0: break
                slots.append(val)
            recs.append((h, slots, roff))
    return recs

v = Vpp(os.path.join(GAME, 'patch.vpp_pc'))
e = [x for x in v.entries() if x['name'].lower() == 'static_ch'][0]
recs = parse_lestrings(v.read(e))

def dec(slots, c2u):
    return ''.join(chr(c2u[s]) if s in c2u else ('<%d>' % s) for s in slots)

print("\n=== 关键记录 双解码 ===")
for h, slots, roff in recs:
    if h in (0xF284ED87, 0x5A5AA49A, 0x1738DE48, 0xFB2E8DE7, 0xDC68A710):
        print("hash=%08X" % h)
        print("   slots      = %s" % slots[:45])
        print("   modder解码 = %r" % dec(slots, mc2u))
        print("   official解码= %r" % dec(slots, oc2u))

print("\n=== 渲染字符在两张表中的压缩值 ===")
for ch in '任璨偶巧位雄衡伪该直升机突击面包车已完成停靠耐久':
    m = mu2c.get(ord(ch)); o = ou2c.get(ord(ch))
    print("   %s  modder=%-5s official=%-5s" % (ch, m, o))

print("\n=== 源字符在两张表中的压缩值 ===")
for ch in '你的弟兄们需要保护':
    m = mu2c.get(ord(ch)); o = ou2c.get(ord(ch))
    print("   %s  modder=%-5s official=%-5s" % (ch, m, o))
