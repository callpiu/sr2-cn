# -*- coding: utf-8 -*-
import os, sys, re, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

def load_cl(buf):
    nums = [int(x) for x in re.findall(rb'\d+', buf)]
    if nums and nums[0] == len(nums) - 1: nums = nums[1:]
    return nums

def parse(data):
    ver, buckets, count = struct.unpack_from("<HHI", data, 4)
    off = 12 + buckets * 8
    ptrs = [struct.unpack_from("<I", data, off + i*4)[0] for i in range(count)]
    out = []; n = len(data)
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
body = load_cl(cn.read(cn.find("charlist_CH", "txt")))
def dec(s):
    o = []
    for w in s:
        if w < 0x20: o.append('·'); continue
        i = w - 0x20
        if i >= len(body): return None
        o.append(chr(body[i]))
    return ''.join(o)

e = cn.find("static_CH", "le_strings")
recs = parse(cn.read(e))
print("static_CH:", len(recs))

KEY = ["面包车","停靠","耐久","突击","保护","弟兄","标记","地点","载具"]
print("\n--- 11 槽 / 23 槽 且含活动相关词的记录 ---")
for h, s in recs:
    if len(s) not in (11, 23): continue
    t = dec(s)
    if not t: continue
    if any(k in t for k in KEY):
        print(f"  {h:08X} [{len(s)}槽] {t}")

print("\n--- 全部 23 槽记录（前 40 条）---")
n = 0
for h, s in recs:
    if len(s) != 23: continue
    t = dec(s)
    if not t: continue
    print(f"  {h:08X} {t}")
    n += 1
    if n >= 40: break
print("23槽总数统计完毕")
