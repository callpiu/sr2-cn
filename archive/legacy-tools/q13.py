# -*- coding: utf-8 -*-
"""全盘字节级搜索：『斯蒂尔沃特大学学生会』的 slot 序列（大端 u16）。"""
import sys, os, struct, glob
sys.path.insert(0, r"F:/sr2-cn")
sys.path.insert(0, r"F:/sr2-cn/stub")
import sr2lib
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
vp = sr2lib.Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(l) for l in vp.read(vp.find("charlist_CH")).decode("utf-8").split("\n")
       if l.strip().isdigit()]
slot = {}
for i, cp in enumerate(cps):
    slot.setdefault(cp, i + 0x20)


def enc(t):
    out = b""
    for c in t:
        if c == "\n":
            out += struct.pack(">H", 10)
        else:
            s = slot.get(ord(c))
            if s is None:
                return None
            out += struct.pack(">H", s)
    return out


pats = {
    "斯蒂尔沃特大学学生会": enc("斯蒂尔沃特大学学生会"),
    "学生会": enc("学生会"),
}
for k, v in pats.items():
    print("%-14s -> %s" % (k, v.hex(" ") if v else "含缺字"))
targets = [(k, v) for k, v in pats.items() if v]


def search_buf(data):
    hits = []
    for k, pat in targets:
        start = 0
        while True:
            i = data.find(pat, start)
            if i < 0:
                break
            hits.append((k, i))
            start = i + 2
    return hits


skip_ext = {".exe", ".dll", ".zip", ".wav", ".mp3", ".ogg", ".bik"}
print("\n=== 散文件 ===")
found_loose = False
for root, dirs, files in os.walk(G):
    dirs[:] = [d for d in dirs if d.lower() not in ("juiced", "cache")]
    for fn in files:
        p = os.path.join(root, fn)
        if os.path.splitext(fn)[1].lower() in skip_ext:
            continue
        try:
            if os.path.getsize(p) > 400_000_000:
                continue
            data = open(p, "rb").read()
        except Exception:
            continue
        for k, i in search_buf(data):
            found_loose = True
            print("   %-40s off=0x%08X  %s" % (os.path.relpath(p, G), i, k))
if not found_loose:
    print("   (无)")

print("\n=== vpp 容器内资源 ===")
found = False
for path in sorted(glob.glob(os.path.join(G, "*.vpp_pc"))):
    try:
        v2 = sr2lib.Vpp(path)
    except Exception:
        continue
    raw = bytes(v2.data)
    hs = search_buf(raw)
    if not hs:
        continue
    ents = sorted(v2.entries(), key=lambda e: e["body"])
    for k, off in hs:
        owner = "?"
        for e in ents:
            p = v2.data_start + e["body"]
            if p <= off < p + e["size"]:
                owner = "%s.%s" % (e["name"], e["ext"])
                break
        found = True
        print("   %-16s off=0x%08X  %-30s %s"
              % (os.path.basename(path), off, owner, k))
if not found:
    print("   (无)")