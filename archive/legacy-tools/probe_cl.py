import sys, os, hashlib, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units, SHIFT

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC = os.path.join(GAME, "patch.vpp_pc")

v = Vpp(SRC)
print("file md5:", hashlib.md5(v.data).hexdigest())

# charlist
e_cl = v.find("charlist_CH", "txt")
raw = v.read(e_cl)
text = raw.decode('utf-8')
lines = text.split('\n')
print("charlist total lines:", len(lines))
print("first 3 lines:", lines[:3])
print("has count= header:", lines[0].startswith('count='))
# 是否所有行都是 5 位？
lens = set(len(x) for x in lines)
print("line length set:", sorted(lens))

REP = {2224: '徒', 2256: '徒', 2261: '录', 2293: '录', 2552: '弹', 2584: '弹'}
print("--- REP 索引原值 / 目标值 / 位数 ---")
for X, ch in REP.items():
    old = lines[X]
    print("  [%d] old=%r(%d位) -> %s(ord=%d,%d位) len_ok=%s" % (
        X, old, len(old), ch, ord(ch), len(str(ord(ch))), len(old) == len(str(ord(ch)))))

# vf3 source glyphs
e_vf3 = v.find("fnt_chinese", "vf3_pc")
vo = v.data_start + e_vf3['body']
n3 = struct.unpack_from('<I', v.data, vo + 0x08)[0]
print("vf3 count @0x08:", n3)
for src in (1058, 1045, 1041):
    U = struct.unpack_from('<i', v.data, vo + 0xAF6C + src*4)[0]
    V = struct.unpack_from('<i', v.data, vo + 0xDB18 + src*4)[0]
    rec = struct.unpack_from('<IIII', v.data, vo + 0xD0 + src*16)
    print("  src glyph idx=%d U=%d V=%d rec=%s" % (src, U, V, rec))
