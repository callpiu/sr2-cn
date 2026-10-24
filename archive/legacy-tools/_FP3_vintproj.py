"""FP3: dump sr2.vint_proj font aliases from the INSTALLED common.vpp_pc,
and compare with the fixed copy at F:\\sr2-cn\\_sr2.vint_proj.
"""
import sys, os, re, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
COMMON = os.path.join(G, "common.vpp_pc")

v = Vpp(COMMON)
ent = v.find("sr2", "vint_proj")
print("entry:", ent["name"], ent["ext"], ent["size"])
raw = v.read(ent)
print("installed md5:", hashlib.md5(raw).hexdigest(), "size", len(raw))

txt = raw.decode("utf-8", "replace")
# print every font_info block
for m in re.finditer(r"<font_info.*?</font_info>", txt, re.S):
    print("----")
    print(m.group(0)[:400])

print()
print("== all <filename> values ==")
for m in re.finditer(r"<filename(?:_overlay)?>(.*?)</filename(?:_overlay)?>", txt, re.S):
    print("   ", m.group(0))

print()
print("== any mention of thin_overlay / thin ==")
for m in re.finditer(r".{0,120}thin.{0,120}", txt, re.S):
    print("   ", repr(m.group(0)))

print()
fixed = r"F:\sr2-cn\_sr2.vint_proj"
if os.path.isfile(fixed):
    fr = open(fixed, "rb").read()
    print("fixed  md5:", hashlib.md5(fr).hexdigest(), "size", len(fr))
    print("identical to installed:", fr == raw)
    ft = fr.decode("utf-8", "replace")
    for m in re.finditer(r"<font_info.*?</font_info>", ft, re.S):
        print("FIXED ----")
        print(m.group(0)[:400])
