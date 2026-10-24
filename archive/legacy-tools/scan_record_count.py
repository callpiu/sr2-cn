"""字节级全文件扫描：static_CH.le_strings 里「弟兄们」到底出现几次？

为什么要做
    probe_vary 把 REC1 改成 3 个字「一二三」，屏幕仍是 11 个乱码。
    但核查文档指出「字形映射在两条串里高度一致」，说明文本确实相关。

    一个可能的解释：**同 hash 有重复记录**（老坑），
    我改的是其中一条，游戏读的是另一条。
    之前用偏移表（offs）遍历，可能漏掉不在表里的记录。

做法
    直接在整个 static_CH 字节流里搜「弟兄们」的槽位序列（大端），
    以及「需要你的保护」，统计出现位置。
    同时把每个命中点周围的记录头解出来（hash）。
"""
import os, sys, struct

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
PATH = os.path.join(G, "patch.vpp_pc")

v = Vpp(PATH)
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
IDX = {chr(cp): i for i, cp in enumerate(cn)}
S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}


def seq(s):
    out = b""
    for c in s:
        if c not in IDX:
            return None
        out += struct.pack(">H", IDX[c] + 0x20)
    return out


d = bytes(v.read(v.find("static_CH", "le_strings")))
print("static_CH %d 字节" % len(d))

pats = {}
for w in ("弟兄们", "需要你的保护", "保护他们免遭袭击", "你的弟兄们"):
    q = seq(w)
    if q:
        pats[w] = q
        print("  模式 %-16s %s" % (w, q.hex(" ")))
print()

for w, q in pats.items():
    offs = []
    i = 0
    while True:
        j = d.find(q, i)
        if j < 0:
            break
        offs.append(j)
        i = j + 1
    print("「%s」出现 %d 次: %s" % (w, len(offs), [hex(x) for x in offs]))

print()
print("=== 每个「弟兄们」命中点的记录头（往前找 hash）===")
q = pats["弟兄们"]
i = 0
while True:
    j = d.find(q, i)
    if j < 0:
        break
    i = j + 1
    # 往前找记录起点：文本以 00 00 结束，起点在 hash 之后
    # 记录头 4 字节紧邻文本之前？不 —— 头是 id1,id2，然后文本
    # 所以文本起点 = 头起点 + 4
    hdr = j - 4
    if hdr < 0:
        continue
    id1, id2 = struct.unpack_from("<HH", d, hdr)
    h = (id1 << 16) | id2
    # 解出该记录全部文本
    vals = []
    p = j
    while p + 1 < len(d):
        s = struct.unpack_from(">H", d, p)[0]
        if s == 0:
            break
        vals.append(s)
        p += 2
    t = "".join(S.get(x, "·") for x in vals)
    print("  文本@0x%X  头@0x%X  hash=0x%08X (%s)  长度=%d" % (j, hdr, h, "LE" if h == 0x84F287ED else "?"))
    print("      %s" % t)
    print("      槽位: %s" % vals[:24])
print()

# 用偏移表统计：每个 off 对应的 hash 和文本首段
b, c, oa, offs = file_offsets(d)
print("=== 偏移表里的记录（找所有含 弟兄们 的）===")
n = 0
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d) - 10):
        continue
    p = off + 4
    vals = []
    while p + 1 < len(d):
        s = struct.unpack_from(">H", d, p)[0]
        if s == 0:
            break
        vals.append(s)
        p += 2
    t = "".join(S.get(x, "·") for x in vals)
    if "弟兄们" in t:
        id1, id2 = struct.unpack_from("<HH", d, off)
        print("  @%-9d hash=0x%08X len=%d  %s" % (off, (id1 << 16) | id2, len(vals), t[:60]))
        n += 1
print("  共 %d 条" % n)
