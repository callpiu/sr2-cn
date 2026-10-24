# -*- coding: utf-8 -*-
"""重新干净解码：charlist_CH + static_CH 字幕记录 -> 逐字对照"""
import sys, struct, io, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from _vpp import Vpp

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
SRC  = r'F:\sr2-cn\_patchsrc\patch.vpp_pc'   # 作者原始包


def parse_charlist(buf):
    """解析 charlist 文本 -> codepoint 列表"""
    txt = buf.decode('latin-1')
    # 去掉注释行
    lines = txt.splitlines()
    out = []
    count_declared = None
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        if s.startswith('//'):
            continue
        m = re.match(r'count\s*=\s*(\d+)', s)
        if m:
            count_declared = int(m.group(1))
            continue
        try:
            out.append(int(s))
        except ValueError:
            pass
    return out, count_declared


def parse_lestrings(buf):
    magic, ver, buckets, count = struct.unpack_from('<IHHI', buf, 0)
    assert magic == 0xA84C7F73, hex(magic)
    recs = {}
    base = 0x0C + buckets * 8
    for b in range(buckets):
        c, off = struct.unpack_from('<II', buf, 0x0C + b * 8)
        p = base + off
        for i in range(c):
            h = struct.unpack_from('>I', buf, p)[0]
            p += 4
            slots = []
            while True:
                v = struct.unpack_from('>H', buf, p)[0]
                p += 2
                if v == 0:
                    break
                slots.append(v)
            recs[h] = slots
    return recs, count


def show(name, buf):
    lst, cd = parse_charlist(buf)
    print(f'--- {name}: items={len(lst)} declared={cd} size={len(buf)}')
    print('   first20:', lst[:20])
    return lst


gv = Vpp(GAME); sv = Vpp(SRC)
ent_g = gv.find('charlist_CH')
ent_s = sv.find('charlist_CH')
print('game charlist_CH size', ent_g['size'], 'src size', ent_s['size'])
cg = show('GAME charlist_CH', gv.read(ent_g))
cs = show('SRC  charlist_CH', sv.read(ent_s))

# static_CH 字幕记录
sg = gv.find('static_CH')
recs_g, cnt_g = parse_lestrings(gv.read(sg))
print('static_CH records', len(recs_g), 'count field', cnt_g)
H = 0xF284ED87
slots = recs_g.get(H)
print('record F284ED87 slots =', slots)
if slots:
    for base in (32, 31, 33, 0, 30, 34):
        s = ''
        ok = 0
        for sl in slots:
            if sl < 0x100:
                s += chr(sl)
                ok += 1
            else:
                idx = sl - base
                if 0 <= idx < len(cg):
                    s += chr(cg[idx]); ok += 1
                else:
                    s += '?'
        print(f'  base={base}: {s}')
