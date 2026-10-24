import os, re, sys, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
W = r"F:\sr2-cn"
J = os.path.join(G,"Mods","JUICED - Strings")
OUT = os.path.join(W,"_juice_fix","out7"); os.makedirs(OUT, exist_ok=True)

# ---------- 1. 生成不含 MP_SERVER_IP 的 .cxt ----------
s = open(os.path.join(W,"_juice_fix","out6","juiced_CH.cxt"), encoding="utf-8").read()
# 删掉 [MP_SERVER_IP] 整块（它的值为空，会导致引擎打印 unrecognized）
s2 = re.sub(r'\[MP_SERVER_IP\]\r\n[^\[]*', '', s)
s2 = s2.rstrip()
if not s2.endswith("\r\n"): s2 += "\r\n"
nb = s2.encode("utf-8")
open(os.path.join(OUT,"juiced_CH.cxt"),"wb").write(nb)
ks = re.findall(r'\[([A-Za-z0-9_,]+)\]', s2)
print("新 .cxt: %d 字节, %d keys (删掉 MP_SERVER_IP)" % (len(nb), len(ks)))
print("  非 ASCII 字符 %d 个" % len([c for c in s2 if ord(c)>0x7F]))
print("  末 60 字节: %r" % nb[-60:])

# ---------- 2. 间距收紧一档：ASCII width 18 -> 17 ----------
SRC = os.path.join(W,"_juice_fix","patch.vpp_pc")
for wnew, tag in ((17,"out7"),):
    v = Vpp(SRC)
    vf3 = bytearray(v.read(v.find("fnt_chinese","vf3_pc")))
    for i in range(95):
        off = 0xD0 + i*16
        struct.pack_into("<h", vf3, off, wnew)
        struct.pack_into("<h", vf3, off+12, wnew)
    v.replace_body_appended(v.find("fnt_chinese","vf3_pc"), bytes(vf3))
    p = os.path.join(W,"_juice_fix",tag,"patch.vpp_pc")
    v.save(p)
    print("备选 width=%d -> %s (%d 字节)" % (wnew, p, os.path.getsize(p)))
