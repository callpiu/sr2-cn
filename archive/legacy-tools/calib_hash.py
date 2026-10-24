"""校准 GetStringHash：验证 le_strings 的哈希算法。
方法：取 le_strings 中一条 ascii-only 记录（文本全 ASCII），把它当 key 反查：
如果 le_strings 存的 hash == GetStringHash(该文本本身)，说明存的是文本哈希；
如果 le_strings 用 ASCII key 哈希，则 key 与文本不同。
先扫描：找 hash==GetStringHash(text) 的记录比例。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

def rol32(v,n): return ((v<<n)|(v>>(32-n)))&0xffffffff
def GetStringHash(s):
    h=0
    for ch in s:
        c=ord(ch)&0xffffffff
        if 0x41<=(c&0xff)<=0x5a: c+=0x20
        h=rol32(h,6)^(c&0xffffffff)
    return h

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

# 建 lo32 -> text 索引（仅 static_US，英文）
e=v.find("static_US","le_strings")
b=v.read(e)
bc,count,oa,offs=file_offsets(b)
lo2txt={}
for off in offs:
    if not(0<off<=len(b)-8): continue
    h=struct.unpack_from('<Q',b,off)[0]
    vals=read_slots(b,off+8)
    if not vals: continue
    txt=decode(vals)
    lo2txt[h&0xffffffff]=(txt,off)

# 测试：hash(自身文本) 是否等于存的 hash
match_self=0; total=0
for lo,(txt,off) in lo2txt.items():
    if len(txt)<3 or any(ord(c)>0x2000 for c in txt):  # 纯 ASCII 短串
        pass
    total+=1
    if GetStringHash(txt)==lo: match_self+=1
print("static_US: hash(文本自身)==存储hash 的比例: %d/%d"%(match_self,total))

# 也测试：小写化文本
match_lower=0
for lo,(txt,off) in lo2txt.items():
    if GetStringHash(txt.lower())==lo: match_lower+=1
print("static_US: hash(小写文本)==存储hash 的比例: %d/%d"%(match_lower,total))

# 打印几条 static_US 的 hash 与文本，观察
print("\n样例（static_US 存储hash vs 文本自身hash）：")
for lo,(txt,off) in list(lo2txt.items())[:12]:
    print("  lo=0x%08X self=0x%08X  %r"%(lo, GetStringHash(txt), txt[:50]))
