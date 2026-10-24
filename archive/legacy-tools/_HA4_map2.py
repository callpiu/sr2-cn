# -*- coding: utf-8 -*-
import os, sys, re, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp

G  = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
PR = r"F:/sr2-cn/pristine/patch.vpp_pc"

class CL:
    def __init__(self, body):
        self.body = list(body); self.rev = {}
        for i, cp in enumerate(self.body): self.rev.setdefault(cp, i)
    def decode(self, units):
        out = []
        for u in units:
            if u < 0x100: out.append(chr(u))
            elif u < len(self.body): out.append(chr(self.body[u]))
            else: return None
        return ''.join(out)

def cl_from(buf):
    nums = [int(x) for x in re.findall(rb'\d+', buf)]
    if nums and nums[0] == len(nums) - 1: nums = nums[1:]
    return CL(nums)

def records(data):
    magic, ver, buckets, count = struct.unpack_from('<IHHI', data, 0)
    assert magic == 0xA84C7F73
    off_at = 12 + buckets * 8
    offs = [struct.unpack_from('<I', data, off_at + i*4)[0] for i in range(count)]
    out, seen = [], set()
    n = len(data)
    for off in offs:
        if off in seen or not (0 <= off <= n - 14): continue
        seen.add(off)
        L = struct.unpack_from('<I', data, off + 8)[0]
        base = off + 12
        if not (0 <= L <= 20000) or base + L*2 + 2 > n: continue
        if data[base + L*2: base + L*2 + 2] != b'\x00\x00': continue
        raw = data[base: base + L*2]
        units = []
        for k in range(L):
            b0, b1 = raw[2*k], raw[2*k+1]
            units.append(b1 if b0 == 0 else ((b0 << 8) | b1))
        out.append((off, units))
    return out, count, buckets

cn = Vpp(os.path.join(G, "patch.vpp_pc"))
cl2795 = cl_from(cn.read(cn.find("charlist_CH", "txt")))
cands = {"CH2795": cl2795}
for nm in ["charlist_JP","charlist_CZ","charlist_PL","charlist_RU","charlist_SK"]:
    e = cn.find(nm, "txt")
    if e: cands[nm] = cl_from(cn.read(e))
pv = Vpp(PR)
cands["CH2838off"] = cl_from(pv.read(pv.find("charlist_CH", "txt")))
print({k: len(v.body) for k, v in cands.items()})

recs = []
for e in cn.entries():
    if e['ext'].lower() != 'le_strings': continue
    nm = e['name'] + '.' + e['ext']
    rs, cnt, nb = records(cn.read(e))
    print(f"  {nm}: count={cnt} buckets={nb} parsed={len(rs)}")
    for off, units in rs:
        recs.append((nm, off, units))
print("total records =", len(recs))
print()
for k, c in cands.items():
    hits = []
    for nm, off, units in recs:
        d = c.decode(units)
        if d and "任璨" in d: hits.append((nm, off, d, cl2795.decode(units)))
    print(f"### {k}: hits={len(hits)}")
    for nm, off, d, t in hits[:4]:
        print(f"   [{nm}@{off:#x}]\n    显示: {d[:70]}\n    正确: {(t or '?')[:70]}")
