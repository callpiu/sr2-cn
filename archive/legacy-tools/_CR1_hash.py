import os, re, struct, sys, glob
sys.path.insert(0, r"F:\sr2-cn")
from _vpp import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
HASH = 0xF284ED87

def parse_charlist(txt):
    m = re.search(r"count\s*=\s*(\d+)", txt)
    body = txt[m.end():] if m else txt
    return [int(x) for x in re.findall(r"\d+", body)]

vp = Vpp(os.path.join(G, "patch.vpp_pc"))
CL = parse_charlist(vp.read(vp.find("charlist_CH", "txt")).decode("utf-8", "replace"))
print("charlist = %d 项, max slot = %d" % (len(CL), len(CL) - 1 + 32))

def decode(slots):
    out = []
    for s in slots:
        if s < 0x100:
            out.append(chr(s))
        else:
            i = s - 32
            out.append(chr(CL[i]) if 0 <= i < len(CL) else "<%d>" % s)
    return "".join(out)

def scan_ls(data, tag):
    if len(data) < 12: return
    magic, ver, buckets, count = struct.unpack_from("<IHHI", data, 0)
    if magic != 0xA84C7F73:
        return
    hits = []
    for i in range(count):
        off = struct.unpack_from("<I", data, 12 + buckets * 8 + i * 4)[0]
        if off + 4 > len(data): continue
        h = struct.unpack_from(">I", data, off)[0]
        if h != HASH: continue
        p = off + 4; slots = []
        while p + 2 <= len(data):
            v = struct.unpack_from(">H", data, p)[0]; p += 2
            if v == 0: break
            slots.append(v)
        hits.append((off, decode(slots)))
    if hits:
        for off, txt in hits:
            print("  ★命中 %-34s off=0x%X  %s" % (tag, off, txt[:80]))
    else:
        print("  无    %-34s (count=%d)" % (tag, count))

print("\n=== VPP 内 le_strings ===")
for vpp in ("patch.vpp_pc", "common.vpp_pc", "textures.vpp_pc"):
    try:
        v = Vpp(os.path.join(G, vpp))
    except Exception as ex:
        print("  skip", vpp, ex); continue
    for e in v.entries():
        if e["ext"] in ("le_strings",) or "le_strings" in e["ext"]:
            try:
                scan_ls(v.read(e), vpp + "::" + e["name"] + "." + e["ext"])
            except Exception as ex:
                print("  err", e["name"], ex)

print("\n=== Mods 下松散 le_strings ===")
for p in glob.glob(os.path.join(G, "Mods", "**", "*.le_strings"), recursive=True):
    scan_ls(open(p, "rb").read(), os.path.relpath(p, G))

print("\n=== Mods 下 .cxt 文本里搜关键串 ===")
for p in glob.glob(os.path.join(G, "Mods", "**", "*.cxt"), recursive=True):
    raw = open(p, "rb").read()
    if b"OpenSpy" in raw or b"\xe4\xbd\xa0" in raw or "弟兄".encode("utf-8") in raw:
        print("  %s  (%d 字节)" % (os.path.relpath(p, G), len(raw)))
