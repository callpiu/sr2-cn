"""穷尽核查：全游戏所有 vpp 的 _CH le_strings 解码，找『胞』『胎』『双胞胎』任意组合。
并输出所有含『胞』或『胎』的记录全文。"""
import sys, os, struct, glob
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME=r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v0=Vpp(os.path.join(GAME,"patch.vpp_pc"))
e_cl=v0.find("charlist_CH","txt")
cl_lines=v0.read(e_cl).decode('utf-8').split('\n')
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

hits=0
for path in glob.glob(os.path.join(GAME,"*.vpp_pc")):
    try: v=Vpp(path)
    except: continue
    for e in v.entries():
        if e['ext']!='le_strings': continue
        if '_CH' not in e['name']: continue
        b=v.read(e)
        try: bc,count,oa,offs=file_offsets(b)
        except: continue
        seen=set()
        for off in offs:
            if off in seen: continue
            seen.add(off)
            if not(0<off<=len(b)-24): continue
            vals=read_slots(b,off+8)
            if not vals: continue
            s=decode(vals)
            if '胞' in s or '胎' in s:
                print("[%s|%s] %r"%(os.path.basename(path),e['name'],s[:100]))
                hits+=1
print("含『胞』或『胎』的记录数:", hits)
