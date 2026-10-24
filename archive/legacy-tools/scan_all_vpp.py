"""扫描游戏目录全部 *.vpp_pc：查找 双胞胎槽位相邻(双胞/胞胎) 与 ascii twins/twin/double（全语种）。"""
import sys, os, glob, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v0 = Vpp(os.path.join(GAME,"patch.vpp_pc"))
e_cl = v0.find("charlist_CH","txt")
cl_lines = v0.read(e_cl).decode('utf-8').split('\n')
cl = {}
for i,s in enumerate(cl_lines):
    if s.strip().isdigit(): cl[i+0x20] = int(s)
SLOT = {cl.get(c):c for c in ['双','胞','胎'] if cl.get(c)}

def read_slots(buf, pos):
    n=len(buf); out=[]; i=pos
    while i+2<=n:
        b0,b1=buf[i],buf[i+1]
        if b0==0 and b1==0: return out
        out.append((b0<<8)|b1); i+=2
    return None

def decode_mixed(vals):
    out=[]
    for x in vals:
        if x<0x100: out.append(chr(x))
        else:
            cp=cl.get(x); out.append(chr(cp) if cp else '\ufffd')
    return ''.join(out)

found=0
for path in glob.glob(os.path.join(GAME,"*.vpp_pc")):
    try:
        v=Vpp(path)
    except Exception:
        continue
    for e in v.entries():
        if e['ext']!='le_strings': continue
        b=v.read(e)
        try:
            bc,count,oa,offs=file_offsets(b)
        except Exception:
            continue
        seen=set()
        for off in offs:
            if off in seen: continue
            seen.add(off)
            if not (0<off<=len(b)-24): continue
            vals=read_slots(b,off+8)
            if not vals: continue
            # 槽位相邻
            for a,c in ((SLOT.get('双'),SLOT.get('胞')),(SLOT.get('胞'),SLOT.get('胎')),(SLOT.get('双'),SLOT.get('胎'))):
                if a and c and a in vals and c in vals:
                    print("[%s|%s] 槽位相邻 双/胞/胎: %r" % (os.path.basename(path),e['name'],decode_mixed(vals)[:100]))
                    found+=1
            # ascii twins/double
            asc=''.join(chr(x) for x in vals if x<0x100).lower()
            if 'twin' in asc or 'double' in asc:
                print("[%s|%s] twins/double: %r" % (os.path.basename(path),e['name'],decode_mixed(vals)[:100]))
                found+=1
print("\n命中总数:", found)
