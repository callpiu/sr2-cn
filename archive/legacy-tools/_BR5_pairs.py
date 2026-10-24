# -*- coding: utf-8 -*-
import os, sys, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _vpp import Vpp
GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def load_charlist(path):
    v = Vpp(path); e = v.find('charlist_CH')
    b = v.read(e).decode('utf-8', 'replace')
    out = []
    for ln in b.replace('\r\n', '\n').split('\n'):
        ln = ln.strip()
        if not ln or ln.startswith('//') or '=' in ln: continue
        out.append(int(ln))
    return out

CL = load_charlist(os.path.join(GAME, 'patch.vpp_pc'))
inv = {c: i for i, c in enumerate(CL)}
print("CL len", len(CL), " 升序?", all(CL[i] < CL[i+1] for i in range(len(CL)-1)))

def parse(buf):
    magic, ver, buckets, count = struct.unpack_from('<IHHI', buf, 0)
    offs = []
    for i in range(buckets):
        c, off = struct.unpack_from('<II', buf, 0x0C + i * 8)
        for j in range(c):
            offs.append(struct.unpack_from('<I', buf, off + j * 4)[0])
    offs.sort()
    d = {}
    for k, o in enumerate(offs):
        end = offs[k + 1] if k + 1 < len(offs) else len(buf)
        body = buf[o:end]
        if len(body) < 6: continue
        h = struct.unpack_from('>I', body, 0)[0]
        slots = []; p = 4
        while p + 1 < len(body):
            v = struct.unpack_from('>H', body, p)[0]; p += 2
            if v == 0: break
            slots.append(v)
        d[h] = slots
    return d

v = Vpp(os.path.join(GAME, 'patch.vpp_pc'))
R = parse(v.read(v.find('static_CH')))

def dec(slots):
    s = ''
    for x in slots:
        if x < 0x100: s += chr(x)
        elif x - 32 < len(CL): s += chr(CL[x - 32])
        else: s += '?'
    return s

for h in (0xF284ED87, 0xAF10621E):
    sl = R.get(h)
    print("\n=== %08X ===" % h)
    if sl is None:
        print("  not found"); continue
    print("  slots:", sl)
    print("  text :", dec(sl))
    cjk = [(s, s - 32, inv.get(CL[s-32])) for s in sl if s >= 0x100 and (s-32) < len(CL)]
    print("  槽位 -> 源字 -> 源索引:")
    for s, x, i in cjk:
        print("    slot=%-5d idx=%-5d char=%s" % (s, x, chr(CL[x])))
