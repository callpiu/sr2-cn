# -*- coding: utf-8 -*-
import os, sys, re, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp

G  = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
PR = r"F:/sr2-cn/pristine/patch.vpp_pc"

class CL:
    def __init__(self, body):
        self.body = list(body)
    def dec(self, slots):
        out = []
        for w in slots:
            if w < 0x20:
                out.append(None); continue
            i = w - 0x20
            if i >= len(self.body):
                return None
            out.append(chr(self.body[i]))
        return ''.join(c if c else '' for c in out)

def cl_from(buf):
    nums = [int(x) for x in re.findall(rb'\d+', buf)]
    if nums and nums[0] == len(nums) - 1: nums = nums[1:]
    return CL(nums)

def parse(data):
    ver, buckets, count = struct.unpack_from("<HHI", data, 4)
    off = 12 + buckets * 8
    ptrs = [struct.unpack_from("<I", data, off + i*4)[0] for i in range(count)]
    out = []
    n = len(data)
    for p in ptrs:
        if p == 0 or p >= n - 4: continue
        id1, id2 = struct.unpack_from("<HH", data, p)
        q = p + 4; slots = []
        while q + 2 <= n:
            w = struct.unpack_from(">H", data, q)[0]
            if w == 0: break
            slots.append(w); q += 2
        out.append(((id1 << 16) | id2, slots))
    return out

cn = Vpp(os.path.join(G, "patch.vpp_pc"))
cl2795 = cl_from(cn.read(cn.find("charlist_CH", "txt")))
cands = {"CH2795": cl2795}
for nm in ["charlist_JP","charlist_CZ","charlist_PL","charlist_RU","charlist_SK"]:
    e = cn.find(nm, "txt")
    if e: cands[nm] = cl_from(cn.read(e))
pv = Vpp(PR)
cands["CH_official"] = cl_from(pv.read(pv.find("charlist_CH", "txt")))
print({k: len(v.body) for k, v in cands.items()})

recs = []
for e in cn.entries():
    if e['ext'].lower() != 'le_strings': continue
    nm = e['name'] + '.' + e['ext']
    rs = parse(cn.read(e))
    print(f"  {nm}: {len(rs)} 条")
    for h, s in rs: recs.append((nm, h, s))
print("total =", len(recs))

# sanity: 面板文字
print("\n--- 用 CH2795 解码，含「直升机突击」的记录 ---")
k = 0
for nm, h, s in recs:
    t = cl2795.dec(s)
    if t and "直升机突击" in t:
        print(f"  [{nm}] {h:08X}: {t[:60]}"); k += 1
print("  hits =", k)

print("\n--- 各候选字形表反查「任璨」 ---")
for name, c in cands.items():
    hit = []
    for nm, h, s in recs:
        t = c.dec(s)
        if t and "任璨" in t:
            hit.append((nm, h, t, cl2795.dec(s)))
    print(f"### {name}: {len(hit)}")
    for nm, h, d, t in hit[:3]:
        print(f"   [{nm}] {h:08X}\n     该表显示: {d[:70]}\n     2795 正确: {(t or '?')[:70]}")
