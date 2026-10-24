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
inv={}
for i,c in enumerate(cl): inv.setdefault(c,i)
def parse_records(buf):
    magic, ver, buckets, count = struct.unpack_from('<IHHI', buf, 0)
    offs=[]
    for i in range(buckets):
        c,off=struct.unpack_from('<II',buf,0x0C+i*8)
        for j in range(c):
            offs.append(struct.unpack_from('<I',buf,off+j*4)[0])
    offs.sort(); recs={}
    for k,o in enumerate(offs):
        end = offs[k+1] if k+1 < len(offs) else len(buf)
        body = buf[o:end]
        h = struct.unpack_from('>I', body, 0)[0]
        n = (len(body)-4)//2
        recs[h]=list(struct.unpack_from('>%dH'%n, body, 4))
    return recs
recs = parse_records(gv.read(gv.find('static_CH')))

def report(h, label):
    s = recs.get(h)
    print(f'=== {label} hash=0x{h:08X}')
    print('   slots:', s)
    txt=''
    for x in s:
        if x==0: continue
        if x<0x100: txt+=chr(x)
        else: txt += chr(cl[x-32]) if 0<=x-32<len(cl) else '?'
    print('   dec32:', txt)
    # 逐字: 槽位 vs 该字在 charlist 的索引
    chars=[c for c in txt if c not in '[]' and not ('a'<=c<='z') and not ('0'<=c<='9') and c!=':']
    print('   detail:')
    for x in s:
        if x<0x100: continue
        ch = chr(cl[x-32]) if 0<=x-32<len(cl) else '?'
        print(f'      slot={x:5d}  idx=slot-32={x-32:5d}  char={ch}  inv[{ch}]={inv.get(ord(ch),-1)}')

report(0x5a5aa49a, '直升机突击')
report(0x1738de48, '已完成停靠')
report(0xfb2e8de7, '面包车耐久')
report(0x38632770, '迷雾巷')
report(0xf284ed87, '字幕-需要你的保护')
report(0xaf10621e, '字幕-要出去谈几笔生意')
