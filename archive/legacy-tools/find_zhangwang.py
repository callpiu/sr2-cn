# -*- coding: utf-8 -*-
"""定位并解码 patch.vpp_pc 里含「丈王」的 le_strings 记录。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(l) for l in
       v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n")
       if l.strip().isdigit()]
# 反查表：码点 -> idx
cp2idx = {}
for i, cp in enumerate(cps):
    cp2idx.setdefault(cp, i)


def dec(slots):
    out = []
    for s in slots:
        idx = s - 0x20
        if 0 <= idx < len(cps):
            out.append(chr(cps[idx]))
        else:
            out.append("<!%d>" % s)
    return "".join(out)


def seq(*v_): return b"".join(int(x).to_bytes(2, "big") for x in v_)


PAT = seq(270, 1796)          # 丈 王
print("### 在 patch.vpp_pc 全字节搜 丈王 = %s" % PAT.hex())
raw = open(os.path.join(G, "patch.vpp_pc"), "rb").read()
i = raw.find(PAT)
while i >= 0:
    print("  命中 @0x%X" % i)
    i = raw.find(PAT, i + 1)

print("\n### 逐个 le_strings 资源定位这条记录")
for en in v.entries():
    if en["ext"] != "le_strings":
        continue
    d = bytes(v.read(v.find(en["name"], en["ext"])))
    if PAT not in d:
        continue
    print("\n  == 资源 %s.%s  (%d 字节)" % (en["name"], en["ext"], len(d)))
    try:
        b, c, off_at, offs = file_offsets(d)
    except Exception as e:
        print("     解析失败:", e); continue
    print("     buckets=%d count=%d" % (b, c))
    for off in offs:
        r = read_units(d, off + 8)
        if not r or not r[0]:
            continue
        slots = [x for x, _ in r[0]]
        txt = dec(slots)
        if "丈王" in txt or "三王" in txt:
            rid = struct.unpack_from("<HH", d, off)
            print("     @%-8d resID=(%d,%d) slots=%s" % (off, rid[0], rid[1], slots))
            print("        文本 = %r" % txt)