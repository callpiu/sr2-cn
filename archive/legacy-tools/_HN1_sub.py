# -*- coding: utf-8 -*-
# 在所有 le_strings 里找这条字幕的源记录
import os, sys, re, struct
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

cn = Vpp(os.path.join(G, "patch.vpp_pc"))
LC = cl_from(cn.read(cn.find("charlist_CH", "txt")))
def dec(slots, off=0x20):
    o=[]
    for w in slots:
        if w < off: o.append('·'); continue
        i=w-off; o.append(chr(LC[i]) if 0<=i<len(LC) else '?')
    return ''.join(o)

KEYS = ["你的弟兄", "弟兄们", "需要你的保护", "保护"]
allrec = []
for e in cn.entries():
    if e['ext'].lower()!='le_strings': continue
    nm = e['name']+'.'+e['ext']
    rs = parse(cn.read(e))
    for h, s in rs: allrec.append((nm, h, s))
print("总记录", len(allrec))

print("\n=== 含「弟兄」的所有记录 ===")
for nm,h,s in allrec:
    t = dec(s)
    if "弟兄" in t:
        print("  [%s] %08X len=%d" % (nm,h,len(s)))
        print("     %s" % t[:90])
        print("     slots:", [hex(x) for x in s])

print("\n=== voice_script_CH 中含「保护」的记录 ===")
k=0
for nm,h,s in allrec:
    if 'voice' not in nm.lower(): continue
    t = dec(s)
    if "保护" in t:
        print("  %08X len=%d  %s" % (h,len(s),t[:80])); k+=1
        if k>=8: break
print("  voice 含保护 =", k)

print("\n=== 含「们需要」的记录 ===")
for nm,h,s in allrec:
    t = dec(s)
    if "们需要" in t or "需要你" in t:
        print("  [%s] %08X len=%d  %s" % (nm,h,len(s),t[:80]))
