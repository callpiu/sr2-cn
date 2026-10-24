"""用 twins/twin 定位「双胞胎」来源。
1) patch.vpp_pc 所有 le_strings（全语种）ascii 部分搜 twins/twin；
2) juiced US/CH cxt 搜 twins/twin/double/food/buy；
3) 尝试用 patch 字表解码 juiced le_strings 各 record，看是否含 双胞胎/双份 等。"""
import sys, os, glob, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(GAME,"patch.vpp_pc"))
e_cl = v.find("charlist_CH","txt")
cl_lines = v.read(e_cl).decode('utf-8').split('\n')
cl = {}
for i,s in enumerate(cl_lines):
    if s.strip().isdigit(): cl[i+0x20] = int(s)

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

print("==== patch.vpp_pc 所有 le_strings 搜 twins/twin（ascii 部分）====")
for e in v.entries():
    if e['ext']!='le_strings': continue
    b=v.read(e)
    bc,count,oa,offs=file_offsets(b)
    seen=set()
    for off in offs:
        if off in seen: continue
        seen.add(off)
        if not (0<off<=len(b)-24): continue
        vals=read_slots(b,off+8)
        if not vals: continue
        asc=''.join(chr(x) for x in vals if x<0x100).lower()
        if 'twin' in asc or 'double' in asc:
            print("  [%s] %r" % (e['name'], decode_mixed(vals)[:100]))

print("\n==== juiced cxt 搜 twins/twin/double/food/buy ====")
base=r"F:\sr2-cn\juicedsrc\Saints-Row-2-Juiced-Patch-main\Mods\JUICED - Strings"
for lang in ('US','CH'):
    f=os.path.join(base,"juiced_%s.cxt"%lang)
    txt=open(f,'rb').read().decode('utf-8',errors='replace')
    for kw in ('twin','double','food','buy','order','meal','份','双'):
        for ln in txt.split('\n'):
            if kw.lower() in ln.lower():
                print("  [%s] %r" % (lang, ln[:100]))

print("\n==== 用 patch 字表解码 juiced le_strings 各 record ====")
jl=os.path.join(GAME,"Mods","JUICED - Strings","juiced_CH.le_strings")
if os.path.exists(jl):
    buf=open(jl,'rb').read()
    magic,ver,buckets,count=struct.unpack_from('<IHHI',buf,0)
    off_at=16+buckets*8
    offs=[struct.unpack_from('<I',buf,off_at+k*4)[0] for k in range(count)]
    for k,off in enumerate(offs):
        if off+8>len(buf): 
            print("  rec%d off=0x%X 越界(len=%d)"%(k,off,len(buf))); continue
        h=struct.unpack_from('<Q',buf,off)[0]
        vals=read_slots(buf,off+8)
        print("  rec%d hash=0x%016X -> %r" % (k,h, decode_mixed(vals)[:80] if vals else "None"))
else:
    print("  juiced le_strings 不在游戏 Mods，找 source")
    for f in glob.glob(r"F:\sr2-cn\**\juiced_CH.le_strings", recursive=True):
        buf=open(f,'rb').read()
        magic,ver,buckets,count=struct.unpack_from('<IHHI',buf,0)
        off_at=16+buckets*8
        offs=[struct.unpack_from('<I',buf,off_at+k*4)[0] for k in range(count)]
        print("  file %s count=%d" % (f,count))
        for k,off in enumerate(offs):
            if off+8>len(buf): print("    rec%d 越界"%k); continue
            h=struct.unpack_from('<Q',buf,off)[0]
            vals=read_slots(buf,off+8)
            print("    rec%d -> %r" % (k, decode_mixed(vals)[:80] if vals else "None"))
        break
