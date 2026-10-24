# -*- coding: utf-8 -*-
"""解析运行时 0x179A63xx 的字符串记录并按补丁表解码 slot。"""
import sys, struct, re
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"F:/sr2-cn")
import ce_mini as C
from minivpp import MiniVpp

pid = C.find_pid(); h = C.open_process(pid)


def rd(a, n):
    return C.read_mem(h, a, n)


# 补丁表
v = MiniVpp(r"F:/sr2-cn/_v534_build.vpp_pc")
raw = v.read(v.find("charlist_CH", "txt"))
patch = [int(x) for x in raw.decode("ascii", "ignore").split() if x.strip().isdigit()]
print("补丁表", len(patch))
v2 = MiniVpp(r"F:/sr2-cn/pristine/patch.vpp_pc")
raw2 = v2.read(v2.find("charlist_CH", "txt"))
m = re.search(rb"(?m)^32\r?$", raw2)
orig = [int(x) for x in raw2[m.start():].decode("ascii", "ignore").split() if x.strip().isdigit()]
print("官方表", len(orig))


def dec(slots, table):
    o = []
    for s in slots:
        i = s - 0x20
        o.append(chr(table[i]) if 0 <= i < len(table) and table[i] < 0x10000 else "?")
    return "".join(o)


# 扫描一段内存，尝试识别 (u16 len, len*u16 slots) 记录
base = 0x179A62E0
blob = rd(base, 0x200)
print("\n=== 扫描记录 ===")
# 强行从每 2 字节对齐尝试：找形如 len 小(1..40) 且后续 slot 大多 < 3000 的位置
for off in range(0, len(blob) - 4, 2):
    ln = struct.unpack("<H", blob[off:off + 2])[0]
    if 1 <= ln <= 40 and off + 2 + ln * 2 <= len(blob):
        slots = [struct.unpack("<H", blob[off + 2 + 2 * i: off + 4 + 2 * i])[0] for i in range(ln)]
        # 合理性：多数 slot 在 [0x20, 0x0C00]
        ok = sum(1 for s in slots if 0x20 <= s <= 0x0C00)
        if ok >= ln - 1 and all(0x20 <= s <= 0x1000 for s in slots):
            d1 = dec(slots, patch)
            d2 = dec(slots, orig)
            printable = sum(1 for c in d1 if c not in "?")
            if printable >= ln - 1:
                print("  @0x%08X len=%d slots=%s" % (base + off, ln, [hex(s) for s in slots]))
                print("        补丁表: %s" % d1)
                print("        官方表: %s" % d2)
