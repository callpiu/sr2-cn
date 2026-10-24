"""v419 修正版：重建 juiced_CH.le_strings，【桶表原样不动】。

崩溃复盘（0x7F491B）：
  上版把桶表一起重建了 → 改变了原文件"脏桶表"行为 → 内层 `cmp edx,[ebp]` 越界 → AV。
  反汇编确认桶表语义：`bucket[i] = (u32 offset起始字节, u32 记录数)`，
  其中 offset 起始字节是裸值（未加基址，运行时 `add [ebp+4], edi` 加的是另一字段），
  且原文件含脏数据（bucket[31] 记录数=316，超出实际 12 条）——**游戏能容忍它**。
  ⇒ 结论：桶表一个字节都不能动。

本版策略：
  1) 头部、桶表 原样保留（占位后整体重排，但桶表【内容字节】完全一致）
  2) 记录数据区重新布局（可任意长度，支持完整中文）
  3) offset 表按新位置更新
  4) 保持 buckets=32 / count=12 不变
"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC  = os.path.join(GAME, "Mods", "JUICED - Strings", "juiced_CH.le_strings")
OUT  = r"F:\sr2-cn\_fix_candidates\juiced_CH.fixed.le_strings"

v = Vpp(os.path.join(GAME, "patch.vpp_pc"))
cl_lines = v.read(v.find("charlist_CH", "txt")).decode('utf-8').split('\n')
c2s, S = {}, {}
for i, s in enumerate(cl_lines):
    if s.strip().isdigit():
        cp = int(s)
        if cp >= 0x100: c2s.setdefault(chr(cp), i + 0x20)
        S[i + 0x20] = cp

data = bytearray(open(SRC, 'rb').read())
magic, ver, buckets, count = struct.unpack_from('<IHHI', data, 0)
HDR, BT = 16, buckets * 8
off_at = HDR + BT
data_start = off_at + count * 4
BUCKET_TABLE_ORIG = bytes(data[HDR:HDR+BT])     # ★ 原样保留

offs = [struct.unpack_from('<I', data, off_at + k*4)[0] for k in range(count)]

def read_slots(buf, pos):
    n = len(buf); out = []; i = pos
    while i + 2 <= n:
        x, y = buf[i], buf[i+1]
        if x == 0 and y == 0: return out
        out.append((x << 8) | y); i += 2
    return out

def dec(sl):
    o = []
    for s in sl:
        if s < 0x100: o.append(chr(s))
        else:
            cp = S.get(s); o.append(chr(cp) if cp else '<?%d>' % s)
    return ''.join(o)

def encode(t):
    out = []
    for ch in t:
        cp = ord(ch)
        if cp < 0x100: out.append(cp)
        else:
            s = c2s.get(ch)
            if s is None: raise ValueError("字表缺字 %r" % ch)
            out.append(s)
    return out

recs = []
for off in offs:
    if off + 8 > len(data):
        recs.append((off, None, None)); continue
    h = struct.unpack_from('<Q', data, off)[0]
    recs.append((off, h, read_slots(data, off + 8)))

# ★ rec11 的 offset 在原版就是垃圾值 0xA5EDEEAF（远超文件尾）。
#   游戏读它时因越界/脏桶表被跳过——这是"原版既有行为"，必须原样保留！
#   上一版我"修正"成 0x32E（== 文件大小），反而让它变成边界值被读到，
#   导致界面出现乱码前缀（"瑞傲正在登录 OpenSpy"）。
#   => 本版对 rec11（越界记录）完全不动：沿用原版 offset 与原样数据。
BROKEN_IDX = {k for k, (off, h, sl) in enumerate(recs) if h is None}
print("\n沿用原版损坏 offset 的记录(不动):", sorted(BROKEN_IDX))

# ★ 完整中文译文（长度不再受原槽位限制）
TARGETS = {
    0xC6EC1896: "输入 OpenSpy ID",
    0x2840CF1D: "重新输入 OpenSpy 密码",
    0x4BFF620D: "你已与 OpenSpy 断开连接。",
    0x2E971EEE: "与 OpenSpy 的连接已丢失。\n正在返回主菜单。",
    0x70F326B6: "输入 OpenSpy 名称",
    0xD3305375: "mail",
    0x54559450: "好友：%i/%i，获得[format][color:green]$%i[/format]，%ls级表现",
    0x55709960: "输入 OpenSpy 密码",
    0x3E2123B9: "输入 OpenSpy 邮箱",
    0xDECC9455: "重新输入 OpenSpy 密码",
    0x1FE19653: "正在登录 OpenSpy",
}

# ---- 构建新记录（顺序、哈希不变；未列出的保持原样）----
new = []
for off, h, sl in recs:
    if h is None:
        new.append((None, None)); continue
    lo = h & 0xffffffff
    if lo in TARGETS:
        new.append((h, encode(TARGETS[lo])))
    else:
        new.append((h, sl))

# ---- 布局 ----
cur = data_start
new_offs, sizes = [], []
for h, sl in new:
    new_offs.append(cur)
    sizes.append(0 if h is None else 8 + len(sl)*2 + 2)
    cur += sizes[-1]
total = cur

out = bytearray(total)
struct.pack_into('<IHHI', out, 0, magic, ver, buckets, count)
out[HDR:HDR+BT] = BUCKET_TABLE_ORIG             # ★ 桶表字节完全照抄
for k, noff in enumerate(new_offs):
    struct.pack_into('<I', out, off_at + k*4, noff)
for (h, sl), noff in zip(new, new_offs):
    if h is None: continue
    struct.pack_into('<Q', out, noff, h)
    p = noff + 8
    for s in sl:
        struct.pack_into('>H', out, p, s); p += 2
    struct.pack_into('>H', out, p, 0)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'wb').write(out)
print("✓ 写出 %s" % OUT)
print("  size %d -> %d   md5=%s" % (len(data), len(out), hashlib.md5(out).hexdigest()))

# ---- 校验 ----
print("\n=== 校验 ===")
o2 = bytes(out)
print("  桶表与原文件一致:", o2[HDR:HDR+BT] == BUCKET_TABLE_ORIG)
print("  头部一致:", o2[:HDR] == bytes(data[:HDR]))
bad = 0
for k, noff in enumerate(new_offs):
    if new[k][0] is None: continue
    sl = read_slots(out, noff + 8)
    txt = dec(sl)
    oob = [s for s in sl if s >= 0x100 and S.get(s) is None]
    bad += len(oob)
    print("  rec%-2d n=%-3d 越界=%d %r" % (k, len(sl), len(oob), txt[:60]))
print("\n  总越界槽:", bad, "(应为 0)")