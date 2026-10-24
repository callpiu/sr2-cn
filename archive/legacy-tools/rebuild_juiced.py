"""重建 juiced_CH.le_strings：用 patch 字表(2795) 把 10 条 OpenSpy 字符串重新编译。

原理（已验证）：
- 格式: magic A84C7F73 | u16 ver=1 | u16 buckets=32 | u32 count
        桶表 buckets*8 = (u32 startOffset, u32 count) 按记录 offset 分段
        offset 表 count*4 = 每条记录的绝对文件偏移
        记录: u64 hash + 0x0000 终止的 u16-BE slot 流
- 槽位: slot < 0x100 => ASCII; slot >= 0x100 => charlist[slot-0x20]
- 现 CH 版槽位索引最大 2832 > 2795（越界 37 条）=> 用了别的字表编译 => 乱码
- US 版能正确解码，可作格式黄金样本；hash 低32位与 CH 一一对应（key 哈希，与语言无关）

做法：保留原文件的桶数/哈希/记录顺序，重排数据区为正确中文，可安全改变文件大小。
"""
import sys, os, struct, hashlib, shutil
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC  = os.path.join(GAME, "Mods", "JUICED - Strings", "juiced_CH.le_strings")
BAK  = SRC + ".pre_rebuild.bak"
OUT  = r"F:\sr2-cn\_fix_candidates\juiced_CH.rebuilt.le_strings"

# ---- patch 字表 ----
v = Vpp(os.path.join(GAME, "patch.vpp_pc"))
cl_lines = v.read(v.find("charlist_CH", "txt")).decode('utf-8').split('\n')
c2s = {}   # char -> slot
for i, s in enumerate(cl_lines):
    if s.strip().isdigit():
        cp = int(s)
        if cp >= 0x100:
            c2s.setdefault(chr(cp), i + 0x20)

# ---- 目标中文（依 US 版英文原文翻译）----
# lo32 hash -> 正确中文（ASCII 部分保留原样，中文用字表槽位）
TARGETS = {
    0xC6EC1896: "Enter OpenSpy ID",          # Enter OpenSpy ID
    0x2840CF1D: "Re-enter OpenSpy Password", # Re-enter OpenSpy Password
    0x4BFF620D: "You have been disconnected from OpenSpy.",
    0x2E971EEE: "Connection to OpenSpy lost.\nReturning to main menu.",
    0x70F326B6: "Enter OpenSpy Name",
    0xD3305375: "mail",                        # 保持 ASCII
    0x55709960: "Enter OpenSpy Password",
    0x3E2123B9: "Enter OpenSpy E-mail",
    0xDECC9455: "Re-enter OpenSpy Password",
    0x1FE19653: "Logging into OpenSpy",
}
# 中文译文（把上面英文替换为中文；ASCII "OpenSpy"/"mail"/"ID" 等保留）
ZH = {
    0xC6EC1896: "输入 OpenSpy ID",
    0x2840CF1D: "重新输入 OpenSpy 密码",
    0x4BFF620D: "你已与 OpenSpy 断开连接。",
    0x2E971EEE: "与 OpenSpy 的连接已丢失。\n正在返回主菜单。",
    0x70F326B6: "输入 OpenSpy 名称",
    0xD3305375: "mail",
    0x55709960: "输入 OpenSpy 密码",
    0x3E2123B9: "输入 OpenSpy 邮箱",
    0xDECC9455: "重新输入 OpenSpy 密码",
    0x1FE19653: "正在登录 OpenSpy",
    # rec6：OpenSpy 好友/声望状态串。原槽位流 = %i/%i + 中文 + [format][color:green]$%i[/format]
    #        + 中文 + %ls（共 51 槽）。US 主表同结构原串为
    #        "...count: %i/%i, you earned [format][color:green]$%i[/format] for a %ls level performance"
    #        这里译为 OpenSpy 好友贡献榜语义，槽数与原串保持一致（自由长度，此处仅求语义正确）。
    0x54559450: "好友数：%i/%i，你获得了[format][color:green]$%i[/format]，凭借 %ls 级表现",
}
# 注意：rec6 那条 51 槽的 %i/%i 格式串不在 TARGETS 里，需保留原样

# ---- 读原文件 ----
data = bytearray(open(SRC, 'rb').read())
magic, ver, buckets, count = struct.unpack_from('<IHHI', data, 0)
assert magic == 0xA84C7F73
off_at = 16 + buckets * 8
offs = [struct.unpack_from('<I', data, off_at + k*4)[0] for k in range(count)]
print("原文件: size=%d buckets=%d count=%d" % (len(data), buckets, count))

# 提取每条 (hash, slots)
recs = []
for off in offs:
    if off + 8 > len(data):
        recs.append((None, None))       # 损坏条目
        continue
    h = struct.unpack_from('<Q', data, off)[0]
    i = off + 8; slots = []
    while i + 2 <= len(data):
        x, y = data[i], data[i+1]
        if x == 0 and y == 0:
            break
        slots.append((x << 8) | y); i += 2
    recs.append((h, slots))

# 编码中文 -> slots
def encode(text):
    out = []
    for ch in text:
        cp = ord(ch)
        if cp < 0x100:
            out.append(cp)
        else:
            s = c2s.get(ch)
            if s is None:
                raise ValueError("字表缺字 %r (%s)" % (ch, hex(cp)))
            out.append(s)
    return out

# 生成新记录（保持原顺序与哈希；仅替换文本）
new_recs = []
for h, slots in recs:
    if h is None:
        new_recs.append((None, None))
        continue
    lo = h & 0xffffffff
    if lo in ZH:
        zh = ZH[lo]
        for ch in zh:
            if ord(ch) >= 0x100 and ch not in c2s:
                raise ValueError("字表缺字 %r" % ch)
        new_recs.append((h, encode(zh)))
    else:
        new_recs.append((h, slots))    # 未列出的保持原样（如 %i/%i 格式串）

# ---- 重建文件 ----
HDR = 16
BT = buckets * 8
OT = count * 4
data_start = HDR + BT + OT

# 先算每条记录大小
rec_sizes = []
for h, slots in new_recs:
    if h is None:
        rec_sizes.append(0)
    else:
        rec_sizes.append(8 + len(slots)*2 + 2)   # hash + slots + 终止符

# 布局
cur = data_start
new_offs = []
for sz in rec_sizes:
    new_offs.append(cur)
    cur += sz
total = cur

out = bytearray(total)
struct.pack_into('<IHHI', out, 0, magic, ver, buckets, count)

# 写记录区
for (h, slots), noff in zip(new_recs, new_offs):
    if h is None:
        continue
    struct.pack_into('<Q', out, noff, h)
    p = noff + 8
    for s in slots:
        struct.pack_into('>H', out, p, s); p += 2
    struct.pack_into('>H', out, p, 0)

# 写 offset 表
for k, noff in enumerate(new_offs):
    struct.pack_into('<I', out, off_at + k*4, noff)

# 重建桶表：按新 offset 分段。原桶表语义=(startOff,count)，指向 offset 表的下标区间。
# 最稳妥：保留原始桶的分组语义，用新 offset 重建。
# 原桶表的 start 值都是 offset 表字节偏移(=off_at+4*idx)。我们按原 record 数分组，
# 把每组的第一个 record 的新 offset 作为桶 start，count = 组内 record 数。
# 读取原桶表分组：
bt_old = data[HDR:HDR+BT]
# 解析原桶：start 是 offset 表中的字节位置 -> idx = (start-off_at)//4
groups = []
for i in range(buckets):
    s, c = struct.unpack_from('<II', bt_old, i*8)
    if c == 0 and s == 0:
        groups.append([])          # 空桶
    else:
        # 该桶覆盖 offset 表区间 [s, s+c*4) -> idx 区间
        start_idx = (s - off_at)//4 if s >= off_at else 0
        groups.append(list(range(start_idx, start_idx + c)))
# 去重但保留顺序，重建桶表
for i in range(buckets):
    idxs = groups[i]
    if not idxs:
        struct.pack_into('<II', out, HDR + i*8, 0, 0)
    else:
        start_byte = off_at + idxs[0]*4
        struct.pack_into('<II', out, HDR + i*8, start_byte, len(idxs))

# ---- 保存 & 校验 ----
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'wb').write(out)
print("\n重建完成:", OUT)
print("  原 size=%d -> 新 size=%d" % (len(data), len(out)))
print("  md5:", hashlib.md5(out).hexdigest())

# 校验：用 patch 字表解码新文件
# 注意 S 的键已经是 slot( = idx+0x20 )，解码时直接 S[slot]，不要再减 0x20
S = {i+0x20: int(s) for i, s in enumerate(cl_lines) if s.strip().isdigit()}
from sr2patch import file_offsets
bc, c2, oa, noffs = file_offsets(bytes(out))
print("\n=== 新文件解码校验 ===")
ok = True
for k, noff in enumerate(noffs):
    p = noff + 8; txt = []
    while p + 2 <= len(out):
        x, y = out[p], out[p+1]
        if x == 0 and y == 0: break
        s = (x << 8) | y
        if s < 0x100:
            txt.append(chr(s))
        elif s in S:
            txt.append(chr(S[s]))
        else:
            txt.append('<越界slot=%d>' % s); ok = False
        p += 2
    line = ''.join(txt)
    print("  rec%-2d %s" % (k, line))
print("\n全部槽位均在 patch 字表范围内:" , ok)