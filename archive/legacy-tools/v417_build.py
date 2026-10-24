"""v417 构建：修复 static_CH 中【两处】格式串参数顺序错误（同一类 bug）。

根因：引擎按 US 字符串的占位符【顺序】传参；CH 若把 %ls(串) 与 %d/%i(整数) 相对 US 调序，
      则 %ls 会把整数当宽字符串指针 → strlen16(0x1) 崩溃。

修复1 (拆车厂，已知必崩):
  OLD1 ' %ls 清单交付 %d/%d 辆车'         顺序(%ls,%d,%d)
  NEW1 '交付 %d/%d 辆车 %ls 清单'         顺序(%d,%d,%ls)  ← 对齐 US
修复2 (@0x2F786，同类隐患，等长重排):
  OLD2 '数：%i/%i，凭借 %ls 级表现，你赚到了[format][color:green]$%i[/format]'
      顺序(%i,%i,%ls,%i)
  NEW2 '数：%i/%i，你赚到了[format][color:green]$%i[/format]，凭借 %ls 级表现'
      顺序(%i,%i,%i,%ls)  ← 对齐 US

两处均为「在原记录字池内重排」，零缺字、等长替换。
"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units, SHIFT

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC = os.path.join(GAME, "patch.vpp_pc")
OUT = r"F:\sr2-cn\_fix_candidates\patch_v417_fmtorder.vpp_pc"

v = Vpp(SRC)
e_cl = v.find("charlist_CH", "txt")
nums = [int(x) for x in v.read(e_cl).decode('utf-8', 'replace').split()
        if x.strip().lstrip('-').isdigit()]
cl = nums[1:] if nums and nums[0] == len(nums) - 1 else nums
S = {i + SHIFT: chr(c) for i, c in enumerate(cl)}

ent_ch = v.find("static_CH", "le_strings")
d_ch = v.read(ent_ch)
n = len(d_ch)
b, c, oa, offs = file_offsets(d_ch)

# 建立 记录header偏移 -> 文本 的映射，并找目标
rec_map = {}
for off in dict.fromkeys(offs):
    if not (0 < off <= n - 24):
        continue
    u, end = read_units(d_ch, off + 8)
    if u is None:
        continue
    t = "".join(chr(vv) if vv < 0x100 else S.get(vv, '\ufffd') for vv, _ in u)
    rec_map[off] = t

# 定位两条目标记录
TARGETS = [
    ('OLD1', ' %ls 清单交付 %d/%d 辆车',
             '交付 %d/%d 辆车 %ls 清单'),
    ('OLD2', '数：%i/%i，凭借 %ls 级表现，你赚到了[format][color:green]$%i[/format]',
             '数：%i/%i，你赚到了[format][color:green]$%i[/format]，凭借 %ls 级表现'),
]

raw = bytearray(v.data)
body_file_off = v.data_start + ent_ch['body']
assert bytes(raw[body_file_off:body_file_off + 0x40]) == d_ch[:0x40], "body 定位校验失败"

total_diff = 0
for tag, old, new in TARGETS:
    header_off = None
    for off, t in rec_map.items():
        if t == old:
            header_off = off
            break
    assert header_off is not None, "未找到 %s: %r" % (tag, old)
    print("[%s] 记录 header 偏移 0x%X" % (tag, header_off))

    # 原记录字池
    u, end = read_units(d_ch, header_off + 8)
    old_slots = [vv for vv, _ in u]
    pool = {}
    ok = True
    for vv, _ in u:
        ch = chr(vv) if vv < 0x100 else S.get(vv)
        if ch is None:
            ok = False
            break
        pool[ch] = vv
    assert ok, "%s 字池解析失败" % tag

    new_chars = list(new)
    missing = [cc for cc in new_chars if cc not in pool]
    assert not missing, "%s 新文本缺字: %r" % (tag, missing)
    assert len(new_chars) == len(old_slots), \
        "%s 不等长: 新 %d vs 旧 %d" % (tag, len(new_chars), len(old_slots))
    new_slots = [pool[cc] for cc in new_chars]

    slot_file_pos = body_file_off + header_off + 8
    cur = struct.unpack_from('>%dH' % len(old_slots), raw, slot_file_pos)
    assert list(cur) == old_slots, "%s 现有槽字节不匹配" % tag
    for j, sv in enumerate(new_slots):
        struct.pack_into('>H', raw, slot_file_pos + j * 2, sv)
    total_diff += abs(len(new_slots) - len(old_slots)) * 0 + len(new_slots)  # 近似计数
    print("  %s 旧槽数=%d 新槽数=%d 已在文件偏移 0x%X 改写" %
          (tag, len(old_slots), len(new_slots), slot_file_pos))
    print("  改后解码: %r" % "".join(
        chr(vv) if vv < 0x100 else S.get(vv, '\ufffd') for vv in new_slots))

open(OUT, 'wb').write(bytes(raw))
md5 = hashlib.md5(bytes(raw)).hexdigest()
print("\n✓ 写出: %s" % OUT)
print("✓ 大小: %d  MD5: %s" % (len(raw), md5))

# ---------- 复核 ----------
v2 = Vpp(OUT)
ent2 = v2.find("static_CH", "le_strings")
d2 = v2.read(ent2)
b2, c2, oa2, offs2 = file_offsets(d2)
new_map = {}
for off in dict.fromkeys(offs2):
    if not (0 < off <= len(d2) - 24):
        continue
    u, end = read_units(d2, off + 8)
    if u is None:
        continue
    t = "".join(chr(vv) if vv < 0x100 else S.get(vv, '\ufffd') for vv, _ in u)
    new_map[off] = t

print("\n=== 复核 ===")
# 1) 两条目标记录改后正确
recs2 = {t: off for off, t in new_map.items()}
for tag, old, new in TARGETS:
    assert new in recs2, "%s 改后文本未找到" % tag
    assert old not in recs2, "%s 旧文本仍存在" % tag
    print("  [%s] 改后 ✓ : %r" % (tag, new))
# 2) 其余记录零变化
same = diffcnt = 0
for off, t in new_map.items():
    if t in (new for _, _, new in TARGETS):
        continue
    if rec_map.get(off) == t:
        same += 1
    else:
        diffcnt += 1
print("其余记录不变: %d  变化: %d（应为 0）" % (same, diffcnt))
assert diffcnt == 0
print("✓✓ v417 构建完成，复核全部通过")
