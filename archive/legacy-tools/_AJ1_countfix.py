# -*- coding: utf-8 -*-
"""Fix: author's charlist_CH lacks the mandatory `count=N` line.
Rebuild with proper header + count + values."""
import sys, struct, io, os, re, shutil, hashlib, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

GAME_PATCH = r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc"
AUTHOR = r"F:\sr2-cn\_patchsrc\patch.vpp_pc"
BK = r"F:\sr2-cn\_backup_L"
os.makedirs(BK, exist_ok=True)

ap = Vpp(AUTHOR)
da = ap.read(ap.find("charlist_CH", "txt"))
body = da.split(b'//ENDOFFILE')[0]
vals = [int(x) for x in re.findall(rb'\d+', body)]
print("author values:", len(vals), "first:", vals[:8], "last:", vals[-4:])

# official-style header (mirror charlist_JP / charlist_CZ structure)
header = (b"//Used character list based on file "
          b"'d:\\projects\\sr2\\main\\data\\tables\\localized_exports\\platform_pc_CH.txt'\r\n"
          b"// a list of all characters known to be used in Saint's Row.\r\n"
          b"// used to compress from 65536 Unicode\r\n")
out = bytearray(header)
out += b'count=%d\r\n' % len(vals)
out += b'\r\n'.join(str(v).encode() for v in vals)
out += b'\r\n//ENDOFFILE\r\n'
new = bytes(out)
print("new charlist size:", len(new))
print(repr(new[:230]))
print("...tail:", repr(new[-40:]))

# sanity: re-parse
m = re.search(rb'count=(\d+)\r\n', new)
print("reparsed count =", m.group(1).decode(), "vals =", len(re.findall(rb'\d+', new.split(b'//ENDOFFILE')[0])) - 3)

gp = Vpp(GAME_PATCH)
e = gp.find("charlist_CH", "txt")
bak = os.path.join(BK, "patch.before_countfix_%s.vpp_pc" % time.strftime("%Y%m%d_%H%M%S"))
shutil.copy2(GAME_PATCH, bak)
print("backup:", bak, os.path.getsize(bak))
gp.replace_body_appended(e, new)
gp.save(GAME_PATCH)
print("saved size:", os.path.getsize(GAME_PATCH))

v2 = Vpp(GAME_PATCH)
d2 = v2.read(v2.find("charlist_CH", "txt"))
print("verify identical:", d2 == new, "size", len(d2))
