import sys, os, re
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
for nm in ("HUD_text","MissionText"):
    d = bytes(v.read(v.find(nm)))
    s = d.decode("utf-8","replace")
    print("=== %s (%d 字节) ===" % (nm, len(d)))
    print(s[:500])
    tags = sorted(set(re.findall(r'<([A-Za-z_]+)>', s)))
    print("  标签: %s" % tags)
    vals = re.findall(r'<[A-Za-z_]+>([^<>\r\n]{2,60})</[A-Za-z_]+>', s)
    nonascii = [x for x in vals if any(ord(c)>0x7F for c in x)]
    print("  非 ASCII 内容 %d 个: %s" % (len(nonascii), nonascii[:5]))
    print()
