import os, sys, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SD = os.path.join(G,"Mods","JUICED - Strings")
v = Vpp(os.path.join(G,"patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(cn)}
MAGIC = 0xA84C7F73
def parse(path):
    d = open(path,"rb").read()
    magic, ver, buckets, count = struct.unpack_from("<IHHI", d, 0)
    print("  magic=0x%08X ver=%d buckets=%d count=%d  (%d 字节)" % (magic,ver,buckets,count,len(d)))
    if magic != MAGIC:
        print("  前 64 字节: %s" % d[:64].hex(" "))
        print("  前 200 字节文本: %r" % d[:200])
        return
    off_at = 16 + buckets*8
    offs = [struct.unpack_from("<I", d, off_at+k*4)[0] for k in range(count)]
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d)-10): continue
        vals = []
        i = off+8
        while i+1 < len(d):
            b0,b1 = d[i], d[i+1]
            if b0==0 and b1==0: break
            vals.append((b0<<8)|b1); i += 2
        t = "".join(S.get(x,"·") for x in vals)
        print("    @%-6d %r" % (off, t[:70]))
for fn in ("patch_ch.le_strings","patch_us.le_strings","static_FR.cxt","platform_PC_FR.cxt"):
    p = os.path.join(SD, fn)
    if not os.path.exists(p): 
        print("=== %s 不存在 ===" % fn); continue
    print("=== %s ===" % fn)
    parse(p)
    print()
