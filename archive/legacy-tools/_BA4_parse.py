# -*- coding: utf-8 -*-
import sys, struct, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from _vpp import Vpp

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
gv = Vpp(GAME)

def parse_charlist(buf):
    out=[]; 
    for ln in buf.decode('latin-1').splitlines():
        s=ln.strip()
        if not s or s.startswith('//'): continue
        if s.startswith('count'): continue
        try: out.append(int(s))
        except: pass
    return out

cl = parse_charlist(gv.read(gv.find('charlist_CH')))
print('charlist items', len(cl))

def parse_records(buf):
    magic, ver, buckets, count = struct.unpack_from('<IHHI', buf, 0)
    assert magic == 0xA84C7F73
    offs=[]
    for i in range(buckets):
        c,off=struct.unpack_from('<II',buf,0x0C+i*8)
        for j in range(c):
            offs.append(struct.unpack_from('<I',buf,off+j*4)[0])
    offs.sort()
    recs=[]
    for k,o in enumerate(offs):
        end = offs[k+1] if k+1 < len(offs) else len(buf)
        body = buf[o:end]
        h = struct.unpack_from('>I', body, 0)[0]
        h2 = struct.unpack_from('<I', body, 0)[0]
        n = (len(body)-4)//2
        slots = list(struct.unpack_from('>%dH'%n, body, 4))
        recs.append((h,h2,slots))
    return recs

recs = parse_records(gv.read(gv.find('static_CH')))
print('records', len(recs))

def dec(slots, base=32):
    out=''
    for s in slots:
        if s == 0: continue
        if s < 0x100: out += chr(s)
        else:
            i = s - base
            out += chr(cl[i]) if 0 <= i < len(cl) else '<?%d>'%s
    return out

# 找 hash
for want in (0xF284ED87, 0x87ED84F2):
    for h,h2,s in recs:
        if h==want or h2==want:
            print('HIT hash', hex(want), 'len', len(s))
            print('  raw', s)
            print('  dec32:', dec(s))

# 找含 [format] 且中文字符多的记录
FMT = [91,102,111,114,109,97,116,93]
cands=[]
for h,h2,s in recs:
    for i in range(len(s)-7):
        if s[i:i+8]==FMT:
            cands.append((h,h2,s))
            break
print('records containing [format]:', len(cands))
for h,h2,s in cands[:12]:
    print('  ', hex(h), '->', dec(s)[:70])
