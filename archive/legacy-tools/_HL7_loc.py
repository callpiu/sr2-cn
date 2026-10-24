# -*- coding: utf-8 -*-
import os, sys, re, struct, glob
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G  = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

def cl_from(buf): return [int(x) for x in re.findall(rb'\d+', buf)]
def parse(data):
    if len(data) < 12: return []
    ver, buckets, count = struct.unpack_from("<HHI", data, 4)
    off = 12 + buckets * 8
    if off + count*4 > len(data): return []
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

print("=== 1. 各 vpp 的 ext 统计 (只看含 string 的) ===")
for f in sorted(glob.glob(os.path.join(G, "*.vpp_pc"))):
    try: v = Vpp(f)
    except Exception as ex: print("  !!", os.path.basename(f), ex); continue
    from collections import Counter
    c = Counter(e['ext'].lower() for e in v.entries())
    s = {k:n for k,n in c.items() if 'string' in k or k in ('gsi','lua','vint_doc')}
    if s: print("  %-22s %s" % (os.path.basename(f), s))

cn = Vpp(os.path.join(G, "patch.vpp_pc"))
LC = cl_from(cn.read(cn.find("charlist_CH", "txt")))
def dec(slots):
    o=[]
    for w in slots:
        if w < 0x20: o.append('·'); continue
        i=w-0x20; o.append(chr(LC[i]) if i<len(LC) else '?')
    return ''.join(o)

print("\n=== 2. 找 你的弟兄们 连续槽位 [0x193,0x74c,0x42b,0x1c6,0x16c] ===")
PAT=[0x193,0x74c,0x42b,0x1c6,0x16c]
def sub(seq,pat):
    for k in range(len(seq)-len(pat)+1):
        if seq[k:k+len(pat)]==pat: return k
    return -1
for e in cn.entries():
    if e['ext'].lower()!='le_strings': continue
    nm=e['name']+'.'+e['ext']
    for h,s in parse(cn.read(e)):
        k=sub(s,PAT)
        if k>=0:
            print("  [%s] %08X len=%d @%d" % (nm,h,len(s),k))
            print("     %s" % dec(s)[:90])
            print("     slots:", [hex(x) for x in s])
print("done")
