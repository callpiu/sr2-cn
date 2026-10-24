# -*- coding: utf-8 -*-
"""探针版：把活动记录改成「原版 charlist 连续区间的字符」，进游戏截图即可反读引擎字符表

原理：显示 = 汉化 charlist[ E(输入字) + 5 ]
     ⇒ E(输入字) = 汉化 charlist.index(显示字) - 5
记录是原地等长修改（只改槽位，不动指针），最安全。
"""
import os, re, struct, shutil, hashlib, subprocess, sys
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp, Font

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
CN = os.path.join(G, "patch.vpp_pc")
BAK = r"F:/sr2-cn/_backup_CN/patch.vpp_pc.before_cn_fix"

# 探针区间（原版 charlist 的位置）
PLAN = [
    ("95A79EDC", 280, 85),   # 该记录 85 槽位
    ("10AF1E62", 365, 53),   # 该记录 53 槽位
]

fc = Font(CN)
CLC = fc.charlist
fv = Font(r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017")
CLV = fv.charlist

v = Vpp(CN, load_all=True)
data = bytearray(v.data)
e_le = v.find("static_CH", "le_strings")
base = v.ds + e_le["body"]
le = bytes(data[base:base + e_le["size"]])

magic, ver, buckets, count = struct.unpack_from("<I H H I", le, 0)
po = 12 + buckets * 8

# 记录表
recs = {}
for idx in range(count):
    p = struct.unpack_from("<I", le, po + idx * 4)[0]
    b4 = le[p:p + 4]
    w = p + 4
    n = 0
    while w + 2 <= len(le):
        s = struct.unpack_from(">H", le, w)[0]
        if s == 0:
            break
        n += 1
        w += 2
    recs[bytes([b4[1], b4[0], b4[3], b4[2]]).hex().upper()] = (p, n)   # 用「目标 hash」做键

print("static_CH 记录数 =", count)
for h, st, ln in PLAN:
    if h not in recs:
        print("  !! 找不到记录 %s" % h)
        continue
    p, n = recs[h]
    print("  %s @记录内偏移 0x%X，槽位 %d（需要 %d）" % (h, p, n, ln))

# 构造探针并原地写入
for h, st, ln in PLAN:
    p, n = recs[h]
    assert ln <= n, "探针比记录槽位长"
    slots = []
    miss = 0
    for k in range(ln):
        c = CLV[st + k]
        if c in CLC:
            slots.append(CLC.index(c) + 0x20)
        else:
            slots.append(slots[-1] if slots else 0x40)   # 缺失字：重复上一个（便于识别）
            miss += 1
    slots += [0x40] * (n - ln)     # 剩余补空格
    off = base + p + 4
    for i, s in enumerate(slots):
        struct.pack_into(">H", data, off + i * 2, s)
    struct.pack_into(">H", data, off + n * 2, 0)
    print("  %s：探针 %d 字（其中 %d 个不在汉化 charlist），已写入" % (h, ln, miss))

out = r"F:/sr2-cn/_PROBE/patch.vpp_pc"
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "wb").write(bytes(data))
print("\n输出: %s  md5=%s" % (out, hashlib.md5(bytes(data)).hexdigest()))

# 部署
try:
    tl = subprocess.run(["tasklist"], capture_output=True, text=True, errors="ignore").stdout.lower()
except Exception:
    tl = ""
if "sr2_pc.exe" in tl:
    print("!! 游戏正在运行，未部署")
else:
    shutil.copy2(out, CN)
    print("已部署到游戏 ✓  md5=%s" % hashlib.md5(open(CN, "rb").read()).hexdigest())
print("\n回退：cp \"%s\" \"%s\"" % (BAK.replace("\\", "/"), CN.replace("\\", "/")))
