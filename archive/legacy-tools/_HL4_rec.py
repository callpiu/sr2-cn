# -*- coding: utf-8 -*-
# 决定性检查: 记录 F284ED87 里存的槽位 到底是 i+0x20 还是 j+0x20
import os, sys, re, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp

G  = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

def cl_from(buf):
    nums = [int(x) for x in re.findall(rb'\d+', buf)]
    return nums

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
LC = cl_from(cn.read(cn.find("charlist_CH", "txt")))
print("charlist_CH =", len(LC))

def dec(slots, off=0x20):
    o = []
    for w in slots:
        if w < off: o.append('·'); continue
        i = w - off
        o.append(chr(LC[i]) if i < len(LC) else '?')
    return ''.join(o)

TARGET = 0xF284ED87
found = 0
for e in cn.entries():
    if e['ext'].lower() != 'le_strings': continue
    nm = e['name'] + '.' + e['ext']
    rs = parse(cn.read(e))
    for h, s in rs:
        if h == TARGET:
            found += 1
            print("\n### [%s] %08X  slots=%d" % (nm, h, len(s)))
            print("   slots(hex):", [hex(x) for x in s])
            print("   slots(dec):", s)
            print("   解码(-0x20):", dec(s))
            print("   解码(-0x20,+1):", dec(s, 0x21))
print("found F284ED87 =", found)

# 对照: 面板文字所在记录
print("\n=== 对照: 含「直升机突击」的记录 ===")
k = 0
for e in cn.entries():
    if e['ext'].lower() != 'le_strings': continue
    nm = e['name'] + '.' + e['ext']
    rs = parse(cn.read(e))
    for h, s in rs:
        t = dec(s)
        if "直升机突击" in t:
            print("  [%s] %08X  %s" % (nm, h, t[:50]))
            print("     slots:", [hex(x) for x in s][:16])
            k += 1
            if k >= 3: break
    if k >= 3: break

# 反查: 显示字「任璨偶巧位雄衡任璨伪该」的槽位序列
print("\n=== 显示字「任璨偶巧位雄衡任璨伪该」对应的槽位 ===")
disp = "任璨偶巧位雄衡任璨伪该"
pos = {}
for i,c in enumerate(LC): pos.setdefault(c, i)
print("   index:", [pos.get(ord(c)) for c in disp])
print("   +0x20 :", [ (pos.get(ord(c))+0x20) if pos.get(ord(c)) is not None else None for c in disp])
