import sys, os
import re
sys.path.insert(0, r"F:/sr2-cn/pylibs"); sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
d=bytes(v.read(v.find("static_US","le_strings")))
b,c,oa,offs=file_offsets(d)
seen=set()
for off in dict.fromkeys(offs):
    if not (0<off<=len(d)-10): continue
    u,_=read_units(d,off+8)
    if not u: continue
    t="".join(chr(x) for x,_ in u)
    if len(t)<=30 and re.search(r"(?i)\b(three|3)\b.*king|king.*\b(three|3)\b", t):
        if t not in seen:
            seen.add(t); print("  @%-8d %r" % (off,t))
print("--- 含 'Kings' 的短文本 ---")
for off in dict.fromkeys(offs):
    if not (0<off<=len(d)-10): continue
    u,_=read_units(d,off+8)
    if not u: continue
    t="".join(chr(x) for x,_ in u)
    if 0<len(t)<=16 and "king" in t.lower() and t not in seen:
        seen.add(t); print("  @%-8d %r" % (off,t))
