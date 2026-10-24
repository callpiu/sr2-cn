# -*- coding: utf-8 -*-
"""GF1: 总验收 —— 6 个英文字体是否已全部换成 fnt_chinese 三件套。"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
TARGETS = ["fnt_body_n", "fnt_body_s", "fnt_head_n", "fnt_head_s",
           "fnt_bodyital_n", "fnt_bodyital_s"]

c = Vpp(os.path.join(G, "common.vpp_pc"))
t = Vpp(os.path.join(G, "textures.vpp_pc"))
p = Vpp(os.path.join(G, "pegs.vpp_pc"))

src_vf3 = c.read(c.find("fnt_chinese", "vf3_pc"))
src_atlas = t.read(t.find("fnt_chinese"))
src_desc = p.read(p.find("fnt_chinese"))
sn = struct.unpack_from("<I", src_vf3, 8)[0]
ss = struct.unpack_from("<I", src_desc, 12)[0]
swh = struct.unpack_from("<HH", src_desc, 28)
sf = struct.unpack_from("<I", src_desc, 32)[0]
print("基准 fnt_chinese : vf3 N=%d (%d B)  图集 %d B  描述符 size=%d w/h=%s fmt=%d"
      % (sn, len(src_vf3), len(src_atlas), ss, swh, sf))
print()
h_vf3 = hashlib.md5(src_vf3).hexdigest()
h_at = hashlib.md5(src_atlas).hexdigest()
ok = True
print("%-16s %-28s %-24s %s" % ("字体", "vf3", "图集", "描述符"))
for nm in TARGETS:
    ev = c.find(nm, "vf3_pc"); ea = t.find(nm); ed = p.find(nm)
    if not (ev and ea and ed):
        print("  %-16s MISSING vf3=%s atlas=%s desc=%s" % (nm, bool(ev), bool(ea), bool(ed))); ok = False; continue
    bv, ba, bd = c.read(ev), t.read(ea), p.read(ed)
    n = struct.unpack_from("<I", bv, 8)[0]
    v_ok = hashlib.md5(bv).hexdigest() == h_vf3
    a_ok = hashlib.md5(ba).hexdigest() == h_at
    d_ok = (struct.unpack_from("<I", bd, 12)[0] == ss and
            struct.unpack_from("<I", bd, 52)[0] == ss and
            struct.unpack_from("<HH", bd, 28) == swh and
            struct.unpack_from("<I", bd, 32)[0] == sf)
    ok &= (v_ok and a_ok and d_ok)
    print("  %-16s N=%-5d %-18s %-10d %-11s %s"
          % (nm, n, "OK" if v_ok else "差异!", len(ba), "OK" if a_ok else "差异!",
             "OK" if d_ok else "差异!"))
print("\n总验收:", "PASS" if ok else "FAIL")

# ---- 两条字幕复核 ----
pv = Vpp(os.path.join(G, "patch.vpp_pc"))
T = [int(s) for s in pv.read(pv.find("charlist_CH", "txt")).decode("utf-8", "replace").replace("\r", "\n").split("\n") if s.strip().isdigit()]
raw = pv.read(pv.find("static_CH", "le_strings"))
N = struct.unpack_from("<I", raw, 8)[0]
body = raw[16 + N * 8:]
ps, cur, i = [], [], 0
while i + 1 < len(body):
    cc = struct.unpack_from(">H", body, i)[0]; i += 2
    if cc == 0: ps.append(cur); cur = []
    else: cur.append(cc)
if cur: ps.append(cur)
print("\ncharlist=%d  pieces=%d  (vf3 上限=%d)" % (len(T), len(ps), sn))
for tid in (0xF284ED87, 0xAF10621E):
    for k, pp in enumerate(ps):
        if len(pp) >= 2 and ((pp[0] == tid >> 16 and pp[1] == tid & 0xFFFF) or (pp[0] == tid & 0xFFFF and pp[1] == tid >> 16)):
            cds = pp[2:]
            s = "".join(chr(T[c - 32]) if 0 <= c - 32 < len(T) else "?" for c in cds)
            print("  ID 0x%08X  piece#%-6d  max_slot=%-5d  越界=%s" % (tid, k, max(cds) - 32, "是" if max(cds) - 32 >= sn else "否"))
            print("     %s" % s)
            break
