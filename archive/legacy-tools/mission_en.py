# -*- coding: utf-8 -*-
"""任务名解析链：
   Name key(如 sh_rn_rec_center) -> static_US 里的英文显示名
   再看 static_CH 同 resID 的中文是什么。
   关键：定位 '三王' 的英文原名。"""
import sys, os, re, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(l) for l in
       v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n")
       if l.strip().isdigit()]
slot2ch = {i + 0x20: chr(c) for i, c in enumerate(cps)}


def load(name):
    d = bytes(v.read(v.find(name, "le_strings")))
    b, c, off_at, offs = file_offsets(d)
    out = []
    for off in offs:
        r = read_units(d, off + 8)
        if not r or not r[0]:
            continue
        slots = [x for x, _ in r[0]]
        t = "".join(slot2ch.get(s, chr(s) if s < 0x20 else "\uFFFD")
                    for s in slots)
        out.append((off, struct.unpack_from("<HH", d, off), t, slots))
    return out


ch = load("static_CH")
us = load("static_US")
print("static_CH %d 条 / static_US %d 条" % (len(ch), len(us)))

# resID -> 文本
ch_by_id = {}
for off, rid, t, s in ch:
    ch_by_id.setdefault(rid, (off, t, s))
us_by_id = {}
for off, rid, t, s in us:
    us_by_id.setdefault(rid, (off, t, s))

# 从 MissionText 抽取所有 key
mt = bytes(v.read(v.find("MissionText", ""))).decode("utf-8", "replace")
keys = re.findall(r"<Name>([^<]+)</Name>", mt)
print("MissionText key 数 %d（去重 %d）" % (len(keys), len(set(keys))))

# 在 static_US 里找含 'King' 的英文条目（三王 = Three Kings）
print("\n### static_US 含 'King' 的条目")
for off, rid, t, s in us:
    if "king" in t.lower():
        cid = ch_by_id.get(rid)
        print("  US @%-8d %-42r  CH 同ID=%r" % (
            off, t[:42], cid[1][:30] if cid else None))

print("\n### static_US 含 'Defender' / 'Lawyer' / 'Attorney'")
for off, rid, t, s in us:
    if any(w in t.lower() for w in ("defender", "lawyer", "attorney")):
        cid = ch_by_id.get(rid)
        print("  US @%-8d %-42r  CH 同ID=%r" % (
            off, t[:42], cid[1][:30] if cid else None))