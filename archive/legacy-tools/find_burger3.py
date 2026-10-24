"""搜 le_strings 里含『双』的短记录（2-8字），找可能的错译显示名『双胞胎』的来源。
同时搜 static_US 里含 Twin Burger / Double Burger 的英文名，看它译成了什么。"""
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

def load(tbl):
    e=v.find(tbl,"le_strings")
    if not e: return []
    b=v.read(e)
    bc,count,oa,offs=file_offsets(b)
    out=[]; seen=set()
    for off in offs:
        if off in seen: continue
        seen.add(off)
        if not(0<off<=len(b)-24): continue
        vals=read_slots(b,off+8)
        if vals: out.append((off,decode(vals)))
    return out

us=load("static_US")
ch=load("static_CH")

print("=== static_US 含 'Burger' 的记录 ===")
for off,s in us:
    if 'urger' in s:
        print("  US 0x%X %r"%(off,s[:70]))

print("\n=== static_CH 含 '汉堡' 的记录 ===")
for off,s in ch:
    if '汉堡' in s:
        print("  CH 0x%X %r"%(off,s[:70]))

print("\n=== static_US 含 'Twin'/'Double' 的记录 ===")
for off,s in us:
    if 'Twin' in s or 'Double' in s or 'double' in s:
        print("  US 0x%X %r"%(off,s[:70]))

print("\n=== static_CH 含 '双' 的短记录(<=6字) ===")
for off,s in ch:
    if '双' in s and len(s)<=6:
        print("  CH 0x%X %r"%(off,s))
