import sys, os, re
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
d = bytes(v.read(v.find("static_CH","le_strings")))

def djb2(s):
    h = 5381
    for c in s.encode() if isinstance(s,str) else s:
        h = ((h*33) + c) & 0xFFFFFFFF
    return h
def djb2x(s):
    h = 5381
    for c in s.encode() if isinstance(s,str) else s:
        h = ((h*33) ^ c) & 0xFFFFFFFF
    return h
def crc32(s):
    import zlib
    return zlib.crc32(s.encode() if isinstance(s,str) else s) & 0xFFFFFFFF
def fnv1a(s):
    h = 2166136261
    for c in s.encode() if isinstance(s,str) else s:
        h = ((h ^ c) * 16777619) & 0xFFFFFFFF
    return h

HASHES = {"djb2":djb2, "djb2x":djb2x, "crc32":crc32, "fnv1a":fnv1a}
# 收集表里的 32 位值集合
offs = list(dict.fromkeys(file_offsets(d)[3]))
print("static_CH 记录数 %d" % len(offs))
present = set()
import struct
for o in offs:
    if 0 < o <= len(d)-8:
        present.add(struct.unpack_from("<I", d, o)[0])
present |= set(struct.unpack_from("<%dI" % (len(d)//4), d))
print("表里不同 32 位值 %d 个（含全文件扫描）" % len(present))
print()
TESTS = ["ACHIEVE_SR2_CRIME_LORD","GAME_LOADING","MENU_AUDIO_SFX","SUI_OPTIONS_TITLE","SUI_LOADING_9","SUI_PAGE1"]
print("%-28s %s" % ("key", "  ".join("%-10s"%h for h in HASHES)))
for t in TESTS:
    row = []
    for hn, hf in HASHES.items():
        hv = hf(t)
        row.append("%-10s" % ("命中" if hv in present else "-"))
    print("%-28s %s" % (t, "  ".join(row)))
