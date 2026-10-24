# -*- coding: utf-8 -*-
# 交接前核查：松散文件、其它表是否含字幕文本、当前游戏包状态
import os, sys, re, struct, hashlib
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

print("=== 1. 游戏根目录松散文件 / 可能的加载器 ===")
for f in sorted(os.listdir(G)):
    p = os.path.join(G, f)
    if os.path.isdir(p):
        try:
            n = len(os.listdir(p))
        except Exception:
            n = -1
        print("  [DIR ] %-24s (%d 项)" % (f, n))
    else:
        print("  [FILE] %-24s %12d B" % (f, os.path.getsize(p)))

print("\n=== 2. 四个包当前 md5 ===")
for f in ["patch.vpp_pc", "common.vpp_pc", "textures.vpp_pc", "pegs.vpp_pc"]:
    p = os.path.join(G, f)
    print("  %-18s %s" % (f, hashlib.md5(open(p, "rb").read()).hexdigest()))

print("\n=== 3. 其它表是否含弟兄字幕文本 ===")
v = Vpp(os.path.join(G, "patch.vpp_pc"))
cl = [int(x) for x in re.findall(rb'\d+', v.read(v.find("charlist_CH", "txt")))]

def parse(data):
    magic, ver, buckets, count = struct.unpack_from("<I H H I", data, 0)
    po = 12 + buckets * 8
    out = []
    for idx in range(count):
        p = struct.unpack_from("<I", data, po + idx * 4)[0]
        id1, id2 = struct.unpack_from("<HH", data, p)
        q = p + 4; slots = []
        while q + 2 <= len(data):
            w = struct.unpack_from(">H", data, q)[0]
            if w == 0: break
            slots.append(w); q += 2
        out.append((idx, (id1 << 16) | id2, slots))
    return out

def dec(slots):
    return "".join(chr(cl[w - 0x20]) if 0 <= w - 0x20 < len(cl) else '?' for w in slots)

KEY = "弟兄们"
for tab in ["static_CH", "voice_script_CH", "platform_pc_CH"]:
    e = v.find(tab, "le_strings")
    if not e:
        print("  %-18s 不存在" % tab); continue
    rows = parse(v.read(e))
    hits = [(i, h, t) for i, h, s in rows for t in [dec(s)] if KEY in t]
    print("  %-18s 共 %d 条，含「%s」= %d 条" % (tab, len(rows), KEY, len(hits)))
    for i, h, t in hits[:6]:
        print("        idx=%-6d hA=%08X  %s" % (i, h, t[:70]))

print("\n=== 4. 字幕文本在 voice_script_CH 里的样子（前5条含homie/homies关键词） ===")
e = v.find("voice_script_CH", "le_strings")
rows = parse(v.read(e))
n = 0
for i, h, s in rows:
    t = dec(s)
    if "homie" in t.lower() or "Homies" in t or "弟兄" in t:
        print("        idx=%-6d hA=%08X  %s" % (i, h, t[:80])); n += 1
        if n >= 5: break
print("  （本段命中", n, "条）")
