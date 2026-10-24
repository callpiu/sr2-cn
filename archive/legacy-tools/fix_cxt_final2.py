import sys, re, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
W = r"F:\sr2-cn"; G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
J = os.path.join(G,"Mods","JUICED - Strings")
OUT = os.path.join(W,"_juice_fix","out4")
ch_raw = open(os.path.join(J,"juiced_CH.cxt"),"rb").read()
us_raw = open(os.path.join(J,"juiced_US.cxt"),"rb").read()
ch = ch_raw.decode("utf-8"); us = us_raw.decode("utf-8")
def blocks(s):
    return {m.group(1): m.group(2) for m in
            re.finditer(r'\[([A-Za-z0-9_]+)\]\r?\n(.*?)(?=\r?\n\[|\Z)', s, re.S)}
bc, bu = blocks(ch), blocks(us)
missing = [k for k in bu if k not in bc]
print("CH 缺 key: %s" % missing)
TR = {"J_MOUSEFOV":"随FOV缩放鼠标灵敏度","J_FINEAIMONLY":"仅精确瞄准时","J_FOVMULT":"FOV倍率"}
v = Vpp(os.path.join(W,"_juice_fix","patch.vpp_pc"))
CPS = set(int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit())
for k,val in TR.items():
    m=[c for c in val if ord(c)>0x100 and ord(c) not in CPS]
    assert not m, (k, "".join(m))
add = ""
for k in missing:
    add += "[%s]\r\n%s\r\n\r\n" % (k, TR.get(k, bu[k].strip("\r\n")))
idx = ch.find("[MP_SERVER_IP]")
assert idx > 0
new = ch[:idx] + add + ch[idx:]
new = new.replace("\r\n","\n").replace("\n","\r\n")
if ch_raw.endswith(b"\r\n") and not new.endswith("\r\n"): new += "\r\n"
nb = new.encode("utf-8")
open(os.path.join(OUT,"juiced_CH.cxt"),"wb").write(nb)
print("写出 %d 字节, CR=%d LF=%d, CRLF结尾=%s" % (len(nb), nb.count(b"\r"), nb.count(b"\n"), nb.endswith(b"\r\n")))
s=nb.decode("utf-8")
print("key 数 %d" % len(re.findall(r'\[([A-Za-z0-9_]+)\]', s)))
for k in missing + ["MP_SERVER_IP"]:
    m = re.search(r'\[%s\]\r\n(.*?)\r\n' % k, s, re.S)
    print("   [%s] = %r" % (k, m.group(1) if m else "?"))
