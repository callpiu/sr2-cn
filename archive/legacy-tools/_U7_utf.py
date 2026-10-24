# -*- coding: utf-8 -*-
import sys, struct, io, re, bisect
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(GAME + r"\patch.vpp_pc")
rawcl = pv.read(pv.find("charlist_CH", "txt"))
m = re.search(rb'count=(\d+)\r?\n', rawcl)
cl = [int(x) for x in re.findall(rb'\d+', rawcl[m.end():])]
srt = sorted(cl)
inc = all(srt[i] < srt[i+1] for i in range(len(srt)-1))
print("cl sorted strictly increasing:", inc)
print("cl[0:8]", cl[:8], "cl[100:108]", cl[100:108], "min", min(cl), "max", hex(max(cl)))

raw = pv.read(pv.find("static_CH"))
i = raw.find(bytes.fromhex('f284ed87'))
sl = []
o = i + 4
while True:
    v = struct.unpack_from('>H', raw, o)[0]; o += 2
    if v == 0:
        break
    sl.append(v)
print("slots:", sl)

def find_cp(cp):
    try:
        return cl.index(cp)
    except ValueError:
        return None

print("--- hypothesis: slot is a UTF-16BE codepoint, look it up in charlist_ch ---")
for v in sl[:6] + sl[22:28]:
    cp = v
    idx = find_cp(cp)
    near = bisect.bisect_left(srt, cp)
    print("  U+%04X  cl.index=%s  nearest_in_cl=U+%04X at %s" %
          (cp, idx, srt[near] if near < len(srt) else -1, near))
