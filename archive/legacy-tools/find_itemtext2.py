"""找 DRUG_TWIN_DESC 的译文所在：遍历 patch 全部条目，
- 找 Items_text / *_text 类条目；
- 在所有 le_strings 里解码，找含 '双胞胎' 或与 burger/hamburger 相关的；
- 也列出所有以 Items 开头的条目名。"""
import sys, os, struct
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

print("=== 所有含 'Item' 或 'Drug' 的条目名 ===")
for e in v.entries():
    if 'item' in e['name'].lower() or 'drug' in e['name'].lower() or 'liquor' in e['name'].lower() or 'food' in e['name'].lower():
        print("  %s  ext=%s size=%d" % (e['name'], e['ext'], e['size']))

print("\n=== 所有 _CH le_strings 里含 '双胞胎' 的（按槽位解码）===")
for e in v.entries():
    if e['ext']!='le_strings' or 'CH' not in e['name']: continue
    b=v.read(e)
    try: bc,count,oa,offs=file_offsets(b)
    except: continue
    seen=set()
    for off in offs:
        if off in seen: continue
        seen.add(off)
        if not (0<off<=len(b)-24): continue
        vals=read_slots(b,off+8)
        if not vals: continue
        s=decode(vals)
        if '双胞胎' in s:
            print("  [%s] %r" % (e['name'], s[:120]))
print("(若上面为空，说明双胞胎确实不在任何 le_strings)")
