"""v416 修复：static_CH 格式串参数顺序错误导致的 strlen16(0x1) 崩溃。

根因（已铁证确认）：
  US:  Delivered %d of %d cars for the %ls list   → 游戏传参 (int, int, str)
  CH:  ' %ls 清单交付 %d/%d 辆车'                  → printf 读取 (str, int, int)
  ⇒ %ls 把第一个参数(整数1)当宽字符串指针 → strlen16(0x1) → 交付拆车厂必崩。

修复：等长重排 '交付 %d/%d 辆车 %ls 清单'（18槽→18槽，字全部来自原记录字池）。

同时审计全部 CH 表中「%ls 与 %d/%i 混用」的记录，用 US 表同占位符多重集配对，
报告所有疑似顺序颠倒的条目。
"""
import sys, os, struct, re, hashlib, shutil, collections
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units, SHIFT

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC = os.path.join(GAME, "patch.vpp_pc")
OUT = r"F:\sr2-cn\_fix_candidates\patch_v416_fix_fmtorder.vpp_pc"

v = Vpp(SRC)
e_cl = v.find("charlist_CH", "txt")
nums = [int(x) for x in v.read(e_cl).decode('utf-8', 'replace').split()
        if x.strip().lstrip('-').isdigit()]
cl = nums[1:] if nums and nums[0] == len(nums) - 1 else nums
S = {i + SHIFT: chr(c) for i, c in enumerate(cl)}
SLOT = {}
for i, c in enumerate(cl):
    SLOT.setdefault(chr(c), i + SHIFT)

def table(name):
    ent = v.find(name, "le_strings")
    d = v.read(ent)
    b, c, oa, offs = file_offsets(d)
    n = len(d)
    recs = []
    for off in dict.fromkeys(offs):
        if not (0 < off <= n - 24):
            continue
        u, end = read_units(d, off + 8)
        if u is None:
            continue
        t = "".join(chr(vv) if vv < 0x100 else S.get(vv, '\ufffd') for vv, _ in u)
        recs.append((off, t))
    return ent, d, recs

def specseq(t):
    """格式占位符序列，如 ['%ls','%d','%d']"""
    return re.findall(r'%l[si]|%[diufcs]', t)

# ---------- 审计：CH 混合占位符记录 vs US 同多重集 ----------
ent_us, d_us, recs_us = table("static_US")
us_by_spec = collections.defaultdict(list)
for off, t in recs_us:
    us_by_spec[tuple(sorted(specseq(t)))].append(t)

ent_ch, d_ch, recs_ch = table("static_CH")
print("== 审计：static_CH 混合占位符（%ls 与 %d/%i 同现）记录 ==")
suspects = []
for off, t in recs_ch:
    sp = specseq(t)
    if '%ls' in sp and ('%d' in sp or '%i' in sp):
        key = tuple(sorted(sp))
        cands = us_by_spec.get(key, [])
        # 找 US 中含 'list'/'Deliver' 特征或唯一候选
        tag = ""
        if len(cands) == 1:
            tag = "US唯一候选: %r" % cands[0]
        suspects.append((off, t, sp, cands[:2]))
        print("  @0x%-6X 顺序=%s  %r" % (off, sp, t))
        if tag:
            print("        %s" % tag)
print()

# ---------- 修复目标记录 ----------
TARGET_OFF = None
TARGET_OLD = ' %ls 清单交付 %d/%d 辆车'
TARGET_NEW = '交付 %d/%d 辆车 %ls 清单'
for off, t in recs_ch:
    if t == TARGET_OLD:
        TARGET_OFF = off
assert TARGET_OFF is not None, "未找到目标记录"
print("目标记录: body 偏移 0x%X" % TARGET_OFF)

# 记录内字池（char->slot）
u, end = read_units(d_ch, TARGET_OFF + 8)
old_slots = [vv for vv, _ in u]
pool = {}
ok = True
for vv, _ in u:
    ch = chr(vv) if vv < 0x100 else S.get(vv)
    if ch is None:
        ok = False; break
    pool[ch] = vv
assert ok

new_chars = list(TARGET_NEW)
missing = [c for c in new_chars if c not in pool]
assert not missing, "新文本缺字: %r" % missing
assert len(new_chars) == len(old_slots), (len(new_chars), len(old_slots))
new_slots = [pool[c] for c in new_chars]
print("旧槽: %s" % old_slots)
print("新槽: %s" % new_slots)
print("新文本解码: %r" % "".join(
    chr(vv) if vv < 0x100 else S.get(vv, '\ufffd') for vv in new_slots))

# ---------- 写入（文件绝对偏移） ----------
raw = bytearray(v.data)
body_file_off = v.data_start + ent_ch['body']
# 校验：文件中该处应与 d_ch 一致
assert bytes(raw[body_file_off:body_file_off + 0x40]) == d_ch[:0x40], "body 定位校验失败"
slot_file_pos = body_file_off + TARGET_OFF + 8
# 再校验现有槽字节
cur = struct.unpack_from('>%dH' % len(old_slots), raw, slot_file_pos)
assert list(cur) == old_slots, "现有槽字节不匹配"
for j, sv in enumerate(new_slots):
    struct.pack_into('>H', raw, slot_file_pos + j * 2, sv)
print("已在文件偏移 0x%X 原地改写 %d 槽" % (slot_file_pos, len(new_slots)))

diff = sum(1 for a, b in zip(v.data, raw) if a != b)
print("全文件字节差异: %d（预期 = 变化槽数×2 以内）" % diff)

open(OUT, 'wb').write(bytes(raw))
md5 = hashlib.md5(bytes(raw)).hexdigest()
print()
print("✓ 已写出: %s" % OUT)
print("✓ 大小: %d  MD5: %s" % (len(raw), md5))

# ---------- 复核 ----------
v2 = Vpp(OUT)
ent2 = v2.find("static_CH", "le_strings")
d2 = v2.read(ent2)
b2, c2, oa2, offs2 = file_offsets(d2)
u2, _ = read_units(d2, TARGET_OFF + 8)
t2 = "".join(chr(vv) if vv < 0x100 else S.get(vv, '\ufffd') for vv, _ in u2)
print()
print("=== 复核 ===")
print("改后记录: %r" % t2)
assert t2 == TARGET_NEW, "复核失败"
# 全表其余记录不变
old_map = {off: t for off, t in recs_ch}
same = diffcnt = 0
for off in dict.fromkeys(offs2):
    if not (0 < off <= len(d2) - 24):
        continue
    u3, _ = read_units(d2, off + 8)
    if u3 is None:
        continue
    t3 = "".join(chr(vv) if vv < 0x100 else S.get(vv, '\ufffd') for vv, _ in u3)
    if off == TARGET_OFF:
        continue
    if old_map.get(off) == t3:
        same += 1
    else:
        diffcnt += 1
print("其余记录不变: %d  变化: %d（应为 0）" % (same, diffcnt))
assert diffcnt == 0
print("✓✓ v416 构建完成，复核全部通过")
