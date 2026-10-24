# -*- coding: utf-8 -*-
import sys, struct
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from _vpp import Vpp
G = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
gv = Vpp(G)
def parse_charlist(buf):
    out=[]
    for ln in buf.decode('latin-1').splitlines():
        s=ln.strip()
        if not s or s.startswith('//') or s.startswith('count'): continue
        try: out.append(int(s))
        except: pass
    return out
cl = parse_charlist(gv.read(gv.find('charlist_CH')))
def parse_records(buf):
    magic, ver, buckets, count = struct.unpack_from('<IHHI', buf, 0)
    offs=[]
    for i in range(buckets):
        c,off=struct.unpack_from('<II',buf,0x0C+i*8)
        for j in range(c):
            offs.append(struct.unpack_from('<I',buf,off+j*4)[0])
    offs.sort(); recs=[]
    for k,o in enumerate(offs):
        end = offs[k+1] if k+1 < len(offs) else len(buf)
        body = buf[o:end]
        h = struct.unpack_from('>I', body, 0)[0]
        n = (len(body)-4)//2
        recs.append((h, list(struct.unpack_from('>%dH'%n, body, 4))))
    return recs
def dec(slots, base=32):
    out=''
    for s in slots:
        if s==0: continue
        if s<0x100: out+=chr(s)
        else:
            i=s-base
            out+= chr(cl[i]) if 0<=i<len(cl) else '<?>'
    return out
recs = parse_records(gv.read(gv.find('static_CH')))
print('records', len(recs))
for kw in ['直升机突击','已完成停靠','面包车耐久','迷雾巷','弟兄们','你的']:
    hits=[(h,dec(s)) for h,s in recs if kw in dec(s)]
    print(f'--- "{kw}": {len(hits)} hits')
    for h,t in hits[:6]:
        print('    ',hex(h), t[:60])
