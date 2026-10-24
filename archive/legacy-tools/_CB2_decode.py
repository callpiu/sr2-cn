# -*- coding: utf-8 -*-
"""解析 charlist_CH + le_strings，解码字幕记录"""
import struct, sys, os, json
sys.path.insert(0, r'F:\sr2-cn')
from _vpp import Vpp

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2'

# ---------- charlist ----------
def parse_charlist(path):
    txt = open(path, 'rb').read().decode('latin1')
    codes = []
    count = None
    for line in txt.replace('\r\n', '\n').split('\n'):
        line = line.strip()
        if not line or line.startswith('/'):
            continue
        if line.startswith('count='):
            count = int(line.split('=')[1])
            continue
        codes.append(int(line))
    return codes, count

codes, cnt = parse_charlist(r'F:\sr2-cn\_fontdump\charlist_CH.txt')
print("charlist entries parsed: %d  (declared count=%s)" % (len(codes), cnt))

# unicode -> compressed
uni2comp = {}
comp2uni = {}
nxt = 0x100
for u in codes:
    if u < 256:
        uni2comp[u] = u
        comp2uni[u] = u
    else:
        uni2comp[u] = nxt
        comp2uni[nxt] = u
        nxt += 1
print("compressed range: 0x100 .. 0x%X  (%d CJK entries)" % (nxt - 1, nxt - 0x100))

print("\ncharlist 前 8 个 >=256 的条目:")
n = 0
for i, u in enumerate(codes):
    if u >= 256:
        print("   file_index=%d  uni=U+%04X %s  -> compressed 0x%X" % (i, u, chr(u), uni2comp[u]))
        n += 1
        if n >= 8:
            break

# ---------- le_strings ----------
def parse_lestrings(data):
    magic, ver, buckets, count = struct.unpack_from('<IHHI', data, 0)
    assert magic == 0xA84C7F73, hex(magic)
    recs = []
    for b in range(buckets):
        o = 0x0C + b * 8
        bc, boff = struct.unpack_from('<II', data, o)
        if bc == 0:
            continue
        for k in range(bc):
            roff = struct.unpack_from('<I', data, boff + k * 4)[0]
            h = struct.unpack_from('>I', data, roff)[0]
            slots = []
            p = roff + 4
            while True:
                v = struct.unpack_from('>H', data, p)[0]
                p += 2
                if v == 0:
                    break
                slots.append(v)
            recs.append((h, slots, roff))
    return dict(ver=ver, buckets=buckets, count=count, recs=recs)

def decode(slots, comp2uni):
    out = []
    for s in slots:
        if s < 256:
            out.append(chr(s))
        else:
            u = comp2uni.get(s)
            out.append(chr(u) if u else '<%d?>' % s)
    return ''.join(out)

v = Vpp(os.path.join(GAME, 'patch.vpp_pc'))
for entname in ('static_CH', 'voice_script_CH', 'platform_pc_CH'):
    e = None
    for x in v.entries():
        if x['name'].lower() == entname.lower():
            e = x
            break
    if e is None:
        continue
    body = v.read(e)
    ls = parse_lestrings(body)
    print("\n=== %s : %d records, buckets=%d, ver=%d ===" % (entname, len(ls['recs']), ls['buckets'], ls['ver']))
    # 找含「你的」的记录
    hit = [r for r in ls['recs'] if 0xF284ED87 in (r[0],) ]
    for h, slots, roff in hit:
        print("   hash=%08X off=0x%X  decoded=%r" % (h, roff, decode(slots, comp2uni)))
        print("   slots=%s" % slots[:40])
    # 找「直升机突击」
    for h, slots, roff in ls['recs']:
        t = decode(slots, comp2uni)
        if '直升机突击' in t or '停靠' in t or '面包车' in t:
            print("   [HUD] hash=%08X off=0x%X decoded=%r" % (h, roff, t))
            print("        slots=%s" % slots[:40])
