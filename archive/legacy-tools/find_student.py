# -*- coding: utf-8 -*-
"""全盘搜索「学生伙」「斯蒂尔沃特大学学生」等 slot 字节序列（所有容器+散文件）。"""
import sys, os, struct, glob
sys.path.insert(0, r"F:/sr2-cn")
sys.path.insert(0, r"F:/sr2-cn/stub")
import sr2lib
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
vp0 = sr2lib.Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(l) for l in vp0.read(vp0.find("charlist_CH")).decode("utf-8").split("\n")
       if l.strip().isdigit()]
slot_of = {}
for i, cp in enumerate(cps):
    slot_of.setdefault(cp, i + 0x20)

def enc(s):
    out = []
    for ch in s:
        if ch == "\n":
            out.append(0x0A)
        else:
            sl = slot_of.get(ord(ch))
            if sl is None:
                return None
            out.append(sl)
    return b"".join(struct.pack(">H", x) for x in out)

QUERIES = ["斯蒂尔沃特大学学生伙", "斯蒂尔沃特大学学生会", "学生伙", "学生联",
           "斯蒂尔沃特大学学生", "大学生伙"]
pats = {}
for q in QUERIES:
    b = enc(q)
    if b:
        pats[q] = b
    print("%s -> %s" % (q, b.hex() if b else "含缺字"))

def scan_bytes(data, label):
    for q, pat in pats.items():
        off = 0
        while True:
            i = data.find(pat, off)
            if i < 0:
                break
            print("  [%s] %r @ 0x%X" % (label, q, i))
            off = i + 1

print("\n=== 容器资源级搜索 ===")
for path in sorted(glob.glob(os.path.join(G, "*.vpp_pc"))):
    name = os.path.basename(path)
    try:
        vp = sr2lib.Vpp(path)
    except Exception:
        continue
    for e in vp.entries():
        try:
            d = vp.read(e)
        except Exception:
            continue
        scan_bytes(d, "%s::%s.%s" % (name, e["name"], e["ext"]))

print("\n=== 散文件搜索（Mods / DLC / 根目录）===")
for root in (os.path.join(G, "Mods"), os.path.join(G, "DLC"), G):
    for dirpath, _, files in os.walk(root):
        for fn in files:
            p = os.path.join(dirpath, fn)
            if p.lower().endswith(".vpp_pc"):
                continue
            try:
                d = open(p, "rb").read()
            except Exception:
                continue
            scan_bytes(d, p)
print("完成")
