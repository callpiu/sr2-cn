"""决定性探针 2：把 REC1 改成 11 个 ASCII 字母。

为什么之前都没判别力
    - ASCII 探针：改成 "PROBE-A..." 但**槽位数不变**，
      而屏幕字幕是【固定 11 个字形位置】（空格不占位）-> 看起来"没变"
    - 变长探针：改成 3 个字 + 36 空格 -> 屏幕还是 11 个位置 -> 还是"没变"
    ★ 根本问题：我没确认「屏幕上看到的是不是不同的字」

本轮
    把 REC1 的 11 个位置填成 'A'..'K'（11 个 ASCII 字母）。
    - 若屏幕变成 ABCDEFGHIJK -> 字幕就是 REC1，问题在字形映射
    - 若屏幕还是 11 个乱码汉字 -> 字幕不是 REC1（字母不可能渲染成汉字）
"""
import os, sys, struct, shutil, datetime, hashlib

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
PATH = os.path.join(G, "patch.vpp_pc")
H1 = 0x84F287ED

v = Vpp(PATH)
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}

ent = v.find("static_CH", "le_strings")
body = bytes(v.read(ent))
pos = v.data.find(body)
d = bytearray(body)
b, c, oa, offs = file_offsets(bytes(d))

# 找 REC1
target = None
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d) - 10):
        continue
    id1, id2 = struct.unpack_from("<HH", d, off)
    if ((id1 << 16) | id2) == H1:
        target = off
        break
if target is None:
    raise SystemExit("找不到 REC1")

print("REC1 @%d" % target)
# 读出当前槽位
p = target + 4
vals = []
while p + 1 < len(d):
    s = struct.unpack_from(">H", d, p)[0]
    if s == 0:
        break
    vals.append(s)
    p += 2
print("  当前 %d 槽位: %s" % (len(vals), "".join(S.get(x, "·") for x in vals)))
print("  当前槽位值: %s" % vals)

# 改成 A..K（ASCII 槽位 = 码点）
NEW = "ABCDEFGHIJK"
assert len(NEW) <= len(vals)
new_slots = [ord(ch) for ch in NEW] + [0x20] * (len(vals) - len(NEW))
print()
print("  改为: %r  （前 %d 个槽位，其余空格）" % (NEW, len(NEW)))

for j, s in enumerate(new_slots):
    bp = target + 4 + j * 2
    d[bp] = (s >> 8) & 0xFF
    d[bp + 1] = s & 0xFF

# 原地写回（不重建，长度不变）
assert len(d) == ent["size"]
raw = bytearray(open(PATH, "rb").read())
raw[pos:pos + len(d)] = d

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
bak = PATH + ".v%s_before_ascii11.bak" % ts
shutil.copy2(PATH, bak)
open(PATH, "wb").write(bytes(raw))
print()
print("备份: %s" % os.path.basename(bak))
print("新 md5: %s" % hashlib.md5(bytes(raw)).hexdigest())

# 复核
v2 = Vpp(PATH)
d2 = bytes(v2.read(v2.find("static_CH", "le_strings")))
p = target + 4
vals2 = []
while p + 1 < len(d2):
    s = struct.unpack_from(">H", d2, p)[0]
    if s == 0:
        break
    vals2.append(s)
    p += 2
print()
print("复核 REC1: %s" % "".join(S.get(x, "·") for x in vals2))
print()
print(">>> 进游戏看字幕：")
print("    若显示 ABCDEFGHIJK  -> 字幕是 REC1（问题在字形映射）")
print("    若仍是 11 个乱码汉字 -> 字幕绝不是 REC1")
