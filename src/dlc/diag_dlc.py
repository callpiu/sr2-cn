# -*- coding: utf-8 -*-
"""DLC 文本结构诊断：解析 le_strings / 列举 cutscene vpp"""
import struct, sys, os

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'

def hexd(b, n=64, off=0):
    out = []
    for i in range(0, min(n, len(b) - off), 16):
        row = b[off + i: off + i + 16]
        out.append('%08X  %s  |%s|' % (
            off + i,
            ' '.join('%02x' % c for c in row).ljust(47),
            ''.join(chr(c) if 32 <= c < 127 else '.' for c in row)))
    return '\n'.join(out)

def parse_lestrings(path):
    """DLC 格式：假设 [u32 BE hash] + UTF-16BE 文本 + 0x0000，逐条扫描"""
    raw = open(path, 'rb').read()
    o = 0
    ents = []
    while o + 4 <= len(raw):
        hid = struct.unpack_from('>I', raw, o)[0]
        o += 4
        cps = []
        while o + 2 <= len(raw):
            u = struct.unpack_from('>H', raw, o)[0]
            o += 2
            if u == 0:
                break
            cps.append(u)
        ents.append((hid, ''.join(chr(c) for c in cps)))
        if o >= len(raw):
            break
    return raw, ents

def vpp_entries(path):
    raw = open(path, 'rb').read()
    base = 5 + 0x14F
    num, csize, len_off, len_names, len_ext = struct.unpack_from('<5i', raw, base)
    names_at = ((0x800 + len_off) & ~0x7FF) + 0x800
    ext_at = ((names_at + len_names) & ~0x7FF) + 0x800
    data_start = ((ext_at + len_ext) & ~0x7FF) + 0x800
    out = []
    for i in range(num):
        f = struct.unpack_from('<7i', raw, 0x800 + i * 28)
        n = raw[names_at + f[0]: raw.index(b'\0', names_at + f[0])].decode('latin1')
        e = raw[ext_at + f[1]: raw.index(b'\0', ext_at + f[1])].decode('latin1') if f[1] else ''
        out.append((n, e, f[3], f[4]))
    return num, csize, out

if __name__ == '__main__':
    what = sys.argv[1]
    if what == 'us':
        raw, ents = parse_lestrings(G + 'DLC/Text/dlc_us.le_strings')
        print('size', len(raw), 'entries', len(ents))
        print(hexd(raw, 96))
        hits = [(i, h, t) for i, (h, t) in enumerate(ents)
                if 'recover' in t.lower() or 'kill the ultor' in t.lower()
                or 'MSN_DLC01' in t or 'bodies' in t.lower()]
        print('--- 目标 key 命中 ---')
        for i, h, t in hits[:30]:
            print(i, '0x%08X' % h, repr(t[:90]))
    elif what == 'cmp':
        ru, eu = parse_lestrings(G + 'DLC/Text/dlc_us.le_strings')
        rc, ec = parse_lestrings(G + 'DLC/Text/dlc_ch.le_strings')
        print('us', len(ru), len(eu), ' ch', len(rc), len(ec))
        hu = [h for h, t in eu]
        hc = [h for h, t in ec]
        print('hash 序列相同?', hu == hc)
        print('us 独有', len(set(hu) - set(hc)), ' ch 独有', len(set(hc) - set(hu)))
        du = {h: t for h, t in eu}
        dc = {h: t for h, t in ec}
        n_same = sum(1 for h in du if du[h] == dc.get(h))
        print('文本仍相同(未译)条数', n_same, '/', len(du))
    elif what == 'cut':
        num, csize, es = vpp_entries(G + 'DLC/Cutscenes/dlc_cutscenes.vpp_pc')
        print('vpp entries', num, 'size', csize)
        from collections import Counter
        print(Counter(e for n, e, b, s in es))
        for n, e, b, s in es[:30]:
            print(n, e, s)
    elif what == 'dump':
        raw, ents = parse_lestrings(G + 'DLC/Text/dlc_ch.le_strings')
        for i, (h, t) in enumerate(ents[:20]):
            print(i, '0x%08X' % h, repr(t[:80]))
