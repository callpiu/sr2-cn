# -*- coding: utf-8 -*-
# 定位字幕 [8858.6942]「还愣着干什么，赶紧离开这儿……」所属任务
# 思路：1) 同文件内 id 邻近的记录（同任务字符串 hash 前缀常接近）
#       2) 跨文件搜同句/近句（static_CH 里可能有任务名）
#       3) 搜含「愣」的其它记录
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"


def parse_charlist(raw):
    B = []
    for L in raw.split(b"\r\n"):
        s = L.strip()
        if not s or s.startswith(b"//") or s.startswith(b"count="):
            continue
        for tok in s.split():
            if tok.isdigit():
                B.append(chr(int(tok)))
    return B


cn = Vpp(CN)
B = parse_charlist(cn.read(cn.find("charlist_CH", "txt")))
Bidx = {c: i for i, c in enumerate(B)}
BT = set(T for T in [])
TARGET_ID1 = 0x8858


def load(name):
    d = cn.read(cn.find(name, "le_strings"))
    buckets, = struct.unpack_from("<H", d, 6)
    count, = struct.unpack_from("<I", d, 8)
    ptrs = struct.unpack_from("<%dI" % count, d, 12 + buckets * 8)
    return d, count, ptrs


def rec(d, p):
    id1, id2 = struct.unpack_from("<HH", d, p)
    q = p + 4
    out = []
    while True:
        s, = struct.unpack_from(">H", d, q)
        q += 2
        if s == 0:
            break
        out.append(s)
    return id1, id2, out


def txt(sl):
    r = []
    for s in sl:
        i = s - 32
        r.append(B[i] if 0 <= i < len(B) else "{%d}" % s)
    return "".join(r)


# 收集所有文件的所有记录
recs = {}
for name in ("voice_script_CH", "static_CH", "platform_pc_CH"):
    d, count, ptrs = load(name)
    for i in range(count):
        try:
            a, b_, sl = rec(d, ptrs[i])
        except Exception:
            continue
        recs[(name, a, b_)] = txt(sl)

print("总记录数 =", len(recs))

# 1) 目标记录本身
for k, v in recs.items():
    if k[1] == 0x8858 and k[2] == 0x6942:
        print("\n★ 目标: %s [%04X.%04X] = %s" % (k[0], k[1], k[2], v))

# 2) 含「愣」或「赶紧离开」的其它记录
print("\n=== 含『愣』的记录 ===")
for k, v in recs.items():
    if "愣" in v:
        print("  %s [%04X.%04X] %s" % (k[0], k[1], k[2], v[:80]))

# 3) id 邻近（同任务 hash 前缀接近）
print("\n=== id1 在 0x8858±0x40 范围内的记录（voice_script_CH）===")
near = [(k, v) for k, v in recs.items()
        if k[0] == "voice_script_CH" and abs(k[1] - TARGET_ID1) <= 0x40]
near.sort(key=lambda x: abs(x[0][1] - TARGET_ID1))
for k, v in near[:25]:
    mark = " ★" if k[1] == TARGET_ID1 else ""
    print("  [%04X.%04X]%s %s" % (k[1], k[2], mark, v[:70]))

# 4) static_CH 里含同关键词（可能含任务名/描述）
print("\n=== 含『赶紧离开』『愣着』的记录 ===")
for k, v in recs.items():
    if "赶紧离开" in v or "愣着" in v:
        print("  %s [%04X.%04X] %s" % (k[0], k[1], k[2], v[:80]))
