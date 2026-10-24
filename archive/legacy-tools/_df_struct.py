# -*- coding: utf-8 -*-
"""解析运行时 0x7A840400 附近的 MStrings::ParsedString 结构数组。
推测格式(需验证):
  struct ParsedString {
     wchar_t slots[N]? 或 uint16 slots[N] ;   // 变长
     uint32 len;
     uint32 hash;
     ...
  }
实际观察:
  0x7A8404A0: 26 07 b4 09 20 07 af 02 b3 01 | 08 0b 00 00 | e9 90 dc b8
  后面 0x7A8404B2: be 04  -> ? 然后 0x7A8404B4 起是 " [format]..."
"""
import sys, struct
sys.stdout.reconfigure(encoding="utf-8")
import ce_mini as C

pid = C.find_pid(); h = C.open_process(pid)


def rd(a, n):
    return C.read_mem(h, a, n)


# 载入补丁字表（从 vpp 读）
sys.path.insert(0, r"F:/sr2-cn")
try:
    from minivpp import MiniVpp
    v = MiniVpp(r"F:/sr2-cn/patch.vpp_pc")
    ent = v.find("charlist_CH", "txt")
    raw = v.read(ent) if ent else None
    print("charlist_CH 读入:", len(raw) if raw else None)
except Exception as e:
    print("minivpp err", e)
    raw = None

if raw:
    txt = raw.decode("ascii", "ignore")
    patch = [int(x) for x in txt.split() if x.strip().isdigit()]
    print("补丁表项数:", len(patch))
else:
    patch = []

# 官方表
try:
    from minivpp import MiniVpp
    v2 = MiniVpp(r"F:/sr2-cn/pristine/patch.vpp_pc")
    e2 = v2.find("charlist_CH", "txt")
    raw2 = v2.read(e2)
    i = raw2.index(b"32")  # 跳到第一项
    raw2 = raw2[raw2.index(b"\n32") + 1:]
    orig = [int(x) for x in raw2.decode("ascii", "ignore").split() if x.strip().isdigit()]
    print("官方表项数:", len(orig))
except Exception as e:
    print("orig err", e)
    orig = []

# 打印补丁表 0..20 和 0x720 附近
if patch:
    print("\n补丁表[0:16]:", patch[:16])
    print("补丁表[1820:1830]:", patch[1820:1830])

# 结构起点搜索：格式猜测 —— 每条 = (u16 slots...), 长度可变
# 但记录之间有规律：看 0x7A840410: 3c 2b | 09 a3 f1 04 fe 01 c0 03 8e 01 | 00 00 | a2 3f ef 12
# 0x1C 字节固定长度？0x7A840400+0x1C=0x7A84041C... 不像
# 用另一种方式：找 "00 00" 分隔（len=0 记录?）
print("\n=== 逐 0x1C 字节切片，看是否像记录 ===")
base = 0x7A8403C0
blob = rd(base, 0x200)
for k in range(0, 0x200, 0x1C):
    c = blob[k:k + 0x1C]
    if len(c) < 0x1C:
        break
    w = struct.unpack("<14H", c)
    print("  @0x%08X: %s | u16=%s" % (base + k, c.hex(" "), [hex(x) for x in w[:7]]))
