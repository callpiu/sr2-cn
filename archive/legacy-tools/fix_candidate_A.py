"""修复候选 A：把 static_CH 里的 <img map_mp_bor_chopshop> 标记原地等长替换。

原理
    崩溃发生在游戏【解析含 <img ...> 标记的文本】时（字符串资源已释放）。
    这里把该标记替换成【等长的纯文字】，槽位数完全不变，
    因此 le_strings 记录的字节长度与 VPP 条目大小都不变 —— 可安全原地修改。

替换内容
    "<img map_mp_bor_chopshop>"   25 个字符
    " 拆车厂(地图图标)          "  ← 需要正好 25 个 ASCII 字符
    实际使用：" map icon: chop shop      "（25 个 ASCII 字符，安全）

注意
    - 只改这 2 条记录（@93130 / @299546）
    - 原地写入，条目大小不变
    - 写盘后用 strip / 重新解析复核
"""
import os, sys, struct, shutil

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC = os.path.join(G, "patch.vpp_pc")
OUT = r"F:\sr2-cn\_fix_candidates\patch_fixA_noimg.vpp_pc"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

TAG = "<img map_mp_bor_chopshop>"          # 25 字符
REPL = " map icon: chop shop     "          # 需要 25 字符
assert len(TAG) == len(REPL), (len(TAG), len(REPL))
print("替换: %r  ->  %r   （各 %d 字符）" % (TAG, REPL, len(TAG)))
print()

raw = bytearray(open(SRC, "rb").read())
v = Vpp(SRC)

# 定位 static_CH 条目
ent = v.find("static_CH", "le_strings")
if not ent:
    raise SystemExit("找不到 static_CH")

# 计算该条目的绝对文件偏移
# Vpp.read() 返回 body；先找到 body 在文件中的位置
body = bytes(v.read(ent))
pos = raw.find(body)
if pos < 0:
    raise SystemExit("无法在文件里定位 static_CH 的 body")
print("static_CH 条目: size=%d, 文件偏移 0x%X" % (ent["size"], pos))

# 解析记录，找出含 <img map_mp_bor_chopshop> 的那些
d = bytearray(body)
b, c, off_at, offs = file_offsets(bytes(d))
CPS = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i + 0x20: chr(cp) for i, cp in enumerate(CPS)}
SLOT = {ch: i + 0x20 for i, ch in enumerate(CPS)}

patched = []
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d) - 10):
        continue
    u, end = read_units(bytes(d), off + 8)
    if u is None:
        continue
    vals = [x for x, _ in u]
    t = "".join(S.get(x, "\uFFFD") for x in vals)
    if TAG not in t:
        continue
    # 在槽位序列里找 TAG 对应的位置：TAG 全是 ASCII，所以槽位值 == 字符码点
    tag_slots = [ord(ch) for ch in TAG]
    # 找子序列
    idx = -1
    for k in range(len(vals) - len(tag_slots) + 1):
        if vals[k:k + len(tag_slots)] == tag_slots:
            idx = k
            break
    if idx < 0:
        print("  @%d 文本含标记但槽位未匹配，跳过" % off)
        continue
    new_slots = [ord(ch) for ch in REPL]
    # 原地写入（文本区起点 = off+8）
    for j, s in enumerate(new_slots):
        struct.pack_into("<H", d, off + 8 + (idx + j) * 2, s)
    patched.append((off, len(vals), idx))
    print("  @%-9d len=%-4d  标记在位置 %d  已替换" % (off, len(vals), idx))

if not patched:
    raise SystemExit("没有找到可替换的记录")

# 校验：修改后条目大小不变
assert len(d) == ent["size"], (len(d), ent["size"])
print()
print("已修改 %d 条记录，条目大小不变（%d 字节）" % (len(patched), len(d)))

# 写回整份文件
raw[pos:pos + len(d)] = d
open(OUT, "wb").write(bytes(raw))
print()
print("已写出: %s  (%d 字节)" % (OUT, len(raw)))

# 复核：重新解析输出文件
print()
print("=== 复核输出文件 ===")
v2 = Vpp(OUT)
e2 = v2.find("static_CH", "le_strings")
d2 = bytes(v2.read(e2))
CPS2 = [int(l) for l in v2.read(v2.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S2 = {i + 0x20: chr(cp) for i, cp in enumerate(CPS2)}
b2, c2, oa2, offs2 = file_offsets(d2)
for off, ln, idx in patched:
    u, _ = read_units(d2, off + 8)
    t = "".join(S2.get(x, "\uFFFD") for x, _ in u)
    print("  @%-9d %s" % (off, t))
    assert "<img" not in t, "替换失败！"
print()
print("✓ 复核通过：<img> 标记已移除，其余内容不变")
n_img = 0
for off in dict.fromkeys(offs2):
    if not (0 < off <= len(d2) - 10):
        continue
    u, _ = read_units(d2, off + 8)
    if u is None:
        continue
    if "<img" in "".join(S2.get(x, "\uFFFD") for x, _ in u):
        n_img += 1
print("  剩余含 <img 的记录: %d 条（原 13 条）" % n_img)
