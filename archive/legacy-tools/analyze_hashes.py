"""分析 OpenSpy le_strings 的哈希结构：
US hash = 0x6E004500C6EC1896  -> 'ter OpenSpy ID'
高32位 0x6E004500 = 'n' 'E' ' ' 交错? 0x6E='n',0x00,0x45='E',0x00 -> "n\0E\0"
尝试：用已知 OpenSpy 字符串反推 key 名。
Juiced 里 OpenSpy 界面的 key 应该是什么？搜源码或 cxt 里的 OpenSpy 相关 key。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2patch import file_offsets

def rol32(v,n): return ((v<<n)|(v>>(32-n)))&0xffffffff
def GSH(s):
    h=0
    for ch in s:
        c=ord(ch)&0xffffffff
        if 0x41<=(c&0xff)<=0x5a: c+=0x20
        h=rol32(h,6)^(c&0xffffffff)
    return h

base=r"F:\sr2-cn\juicedsrc\Saints-Row-2-Juiced-Patch-main\Mods\JUICED - Strings"
b=open(os.path.join(base,"juiced_US.le_strings"),'rb').read()
magic,ver,buckets,count=struct.unpack_from('<IHHI',b,0)
off_at=16+buckets*8
offs=[struct.unpack_from('<I',b,off_at+k*4)[0] for k in range(count)]
def read_slots(buf,pos):
    n=len(buf); out=[]; i=pos
    while i+2<=n:
        x,y=buf[i],buf[i+1]
        if x==0 and y==0: return out
        out.append((x<<8)|y); i+=2
    return None

print("=== 记录哈希分解 ===")
for k,off in enumerate(offs):
    if off+8>len(b): continue
    h=struct.unpack_from('<Q',b,off)[0]
    lo=h&0xffffffff; hi=(h>>32)&0xffffffff
    vals=read_slots(b,off+8)
    txt=''.join(chr(x) if x<0x100 else '?' for x in vals) if vals else ''
    print(" rec%d lo=0x%08X hi=0x%08X hi_ascii=%r  %r"%(k,lo,hi,
        bytes([(hi>>24)&0xff,(hi>>16)&0xff,(hi>>8)&0xff,hi&0xff]), txt))

# 用 GSH 试各种 OpenSpy 相关的 key 名
print("\n=== 试算可能的 OpenSpy key ===")
cands=["OPENSPY_NAME","OPENSPY_ID","OPENSPY_PASSWORD","OPENSPY_EMAIL",
 "OPENSPY_ENTER_NAME","OPENSPY_DISCONNECTED","OPENSPY_CONNECTION_LOST",
 "OPENSpy Name","OpenSpy Name","OPENSPY_E_MAIL",
 "MENU_OPENSPY","LOGIN_OPENSPY",
 "Enter OpenSpy ID","Enter OpenSpy Name"]
for c in cands:
    print("  GSH(%-24r) = 0x%08X" % (c, GSH(c)))