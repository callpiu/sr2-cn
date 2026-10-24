# -*- coding: utf-8 -*-
# 方案 B 最小风险版：从干净 patch 出发，在 static_CH 原记录位置等长覆盖英文短句
# 目的：兼容引擎若不走 pointer array、而顺序读取原 records blob 的情况。
import os, sys, re, struct, shutil, hashlib
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
PK = os.path.join(G, "patch.vpp_pc")
CLEAN = r"F:/sr2-cn/_backup_B/patch.vpp_pc.before_safeB"  # md5 3a451da5，B前干净状态
CUR_BAK = r"F:/sr2-cn/_backup_B4/patch.vpp_pc.before_inplaceB"
os.makedirs(os.path.dirname(CUR_BAK), exist_ok=True)
shutil.copy2(PK, CUR_BAK)
print("当前状态备份:", CUR_BAK)

# 回到干净 patch，避免保留前一版追加 pointer 修改
shutil.copy2(CLEAN, PK)
print("已回到干净 patch:", CLEAN)

# hA -> 等长英文短句（会自动右侧补空格到原槽位数）
REPL = {
    0x84F287ED: "Homies need protection",
    0x10AF1E62: "Protect homies from attackers",
    0xEC2D9F07: "HOMIES!",
    0xE52F931A: "Special Homies unlock as you play. Explore Stilwater.",
    0x95A79EDC: "Homies car is out of gas. Recruit them and fly home.",
    0x343FEA1F: "Homies are waiting for you",
}

def parse_slots(data, p):
    id1, id2 = struct.unpack_from("<HH", data, p)
    q = p + 4; slots = []
    while q + 2 <= len(data):
        w = struct.unpack_from(">H", data, q)[0]
        if w == 0: break
        slots.append(w); q += 2
    return id1, id2, slots, q + 2

def encode_fixed(text, n):
    # 只用 ASCII，避免字幕 CJK 渲染路径；等长补空格，保持记录长度完全不变
    s = text.encode("ascii", "replace").decode("ascii")
    if len(s) > n:
        s = s[:n]
    s = s.ljust(n)
    return [ord(c) for c in s]

v = Vpp(PK)
e = v.find("static_CH", "le_strings")
d = bytearray(v.read(e))
magic, ver, buckets, count = struct.unpack_from("<I H H I", d, 0)
ptr_off = 12 + buckets * 8

modified = 0
for idx in range(count):
    p = struct.unpack_from("<I", d, ptr_off + idx * 4)[0]
    id1, id2, slots, end = parse_slots(d, p)
    h = (id1 << 16) | id2
    if h not in REPL:
        continue
    new_slots = encode_fixed(REPL[h], len(slots))
    raw = struct.pack("<HH", id1, id2)
    raw += b"".join(struct.pack(">H", w) for w in new_slots)
    raw += b"\x00\x00"
    assert len(raw) == (end - p)
    d[p:end] = raw
    modified += 1
    print("  %08X idx=%d ptr=%08x slots=%d -> %r" % (h, idx, p, len(slots), REPL[h]))

if modified != len(REPL):
    raise SystemExit("目标未全部命中: %d/%d" % (modified, len(REPL)))

# body 大小保持不变
assert len(d) == e['size']
v.replace_body_appended(e, bytes(d), align=0x800)
v.save(PK)

print("修改记录数:", modified)
print("static_CH 大小保持:", len(d), "B")
print("patch md5:", hashlib.md5(open(PK, "rb").read()).hexdigest())
print("\n回滚命令:")
print('  cp "F:/sr2-cn/_backup_B/patch.vpp_pc.before_safeB" "' + PK.replace('\\', '/') + '"')
print("\n判据: 重启游戏后，这几句弟兄字幕应显示英文短句，不再显示中文乱码。")
