"""定位 burger 的 NAME（显示名）。DRUG_TWIN_NAME 对应的中文显示名。
打印所有短中文记录（含 1-8 字），找出 burger 名字候选；并搜 '一模一样的半磅汉堡' 的邻居。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME=r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v=Vpp(os.path.join(GAME,"patch.vpp_pc"))
e_cl=v.find("charlist_CH","txt")
cl_lines=v.read(e_cl).decode('utf-8').split('\n')
cl={}
for i,s in enumerate(cl_lines):
    if s.strip().isdigit(): cl[i+0x20]=int(s)
def read_slots(buf,pos):
    n=len(buf); out=[]; i=pos
    while i+2<=n:
        b0,b1=buf[i],buf[i+1]
        if b0==0 and b1==0: return out
        out.append((b0<<8)|b1); i+=2
    return None
def decode(vals):
    o=[]
    for x in vals:
        if x<0x100:o.append(chr(x))
        else:
            cp=cl.get(x); o.append(chr(cp) if cp else '\ufffd')
    return ''.join(o)

# 用 hash 定位 DRUG_TWIN_NAME / burgera NAME
def rol32(v,n): return ((v<<n)|(v>>(32-n)))&0xffffffff
def GSH(s):
    h=0
    for ch in s:
        c=ord(ch)&0xffffffff
        if 0x41<=(c&0xff)<=0x5a: c+=0x20
        h=rol32(h,6)^(c&0xffffffff)
    return h

# 建 (table,off)->(lo32hash)
recs=[]  # (tbl,off,lo32,blob)
for e in v.entries():
    if e['ext']!='le_strings' or 'CH' not in e['name']: continue
    b=v.read(e)
    try: bc,count,oa,offs=file_offsets(b)
    except: continue
    seen=set()
    for off in offs:
        if off in seen: continue
        seen.add(off)
        if not(0<off<=len(b)-8): continue
        lo=struct.unpack_from('<Q',b,off)[0]&0xffffffff
        vals=read_slots(b,off+8)
        recs.append((e['name'],off,lo,decode(vals) if vals else ''))

# 找所有 hash 命中 DRUG_TWIN_NAME / DESC 的记录（跨所有 CH 表）
for key in ("DRUG_TWIN_NAME","DRUG_TWIN_DESC","burgera","burgera1","the_fist"):
    h=GSH(key)
    hits=[(t,o,s) for (t,o,lo,s) in recs if lo==h]
    print("key=%-16s hash=0x%08X -> %d hit" % (key,h,len(hits)))
    for t,o,s in hits:
        print("     [%s] %r" % (t,s[:80]))

print("\n=== 所有含『一模一样』的记录（burgera 描述）===")
for t,o,lo,s in recs:
    if '一模一样' in s:
        print("  [%s] hash=0x%08X %r" % (t,lo,s[:80]))
