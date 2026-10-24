"""SR2 GetStringHash 还原实现 + 定位 DRUG_TWIN_* 记录。
算法: eax=0; for c in str: if 'A'<=c<='Z': c+=0x20; eax = rol32(eax,6) ^ c
"""
import sys, os, struct, glob
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

def rol32(v, n):
    return ((v << n) | (v >> (32 - n))) & 0xffffffff

def GetStringHash(s):
    h = 0
    for ch in s:
        c = ord(ch) & 0xFFFFFFFF
        # movsx ecx, byte: 符号扩展，但 ASCII <128 不受影响
        if 0x41 <= (c & 0xff) <= 0x5A:  # 'A'..'Z' -> cmp esi=(c-'A'),ja 25
            c += 0x20
        h = rol32(h, 6) ^ (c & 0xffffffff)
    return h

# 验证：hash 应能在 le_strings 里找到
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

# 收集 patch 全部 le_strings 的 (hash32 lo, table, off)
index = {}
for e in v.entries():
    if e['ext']!='le_strings': continue
    b=v.read(e)
    try: bc,count,oa,offs=file_offsets(b)
    except: continue
    for off in offs:
        if 0<off<=len(b)-8:
            h=struct.unpack_from('<Q',b,off)[0]
            lo=h & 0xffffffff
            index.setdefault(lo, []).append((e['name'], off, b))

for key in ("DRUG_TWIN_NAME","DRUG_TWIN_DESC","burgera1","burgera"):
    h = GetStringHash(key)
    print("GetStringHash(%-16s) = 0x%08X" % (key, h))
    if h in index:
        for name,off,b in index[h]:
            vals=read_slots(b,off+8)
            print("    命中 [%s] @0x%X -> %r" % (name, off, decode(vals) if vals else None))
    else:
        print("    未命中 le_strings（可能未翻译/走英文兜底）")
