"""分析：汉化包 vs 原版 的条目差异 + 用繁/简两套字表分别解码每个 le_strings 表。

决定性问题：哪些表在【简体字表】下解码会越界（崩溃源），在【繁体字表】下却正常。
"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, parse_charlist
from sr2patch import file_offsets, read_units, decode, SHIFT, MAGIC

VANILLA = r"F:\sr2-cn\_day_2026-10-07\07_备份快照\patch.vpp_pc.原版_能跑_2320.bak"
LOCAL  = r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc"

def keys(v):
    return {(e['name'], e['ext']) for e in v.entries()}

v_van = Vpp(VANILLA)
v_loc = Vpp(LOCAL)
kv, kl = keys(v_van), keys(v_loc)
added = sorted(kl - kv)
removed = sorted(kv - kl)
common = sorted(kv & kl)
print("== 条目数 ==  原版=%d  汉化=%d" % (v_van.num, v_loc.num))
print("== 新增(%d) ==" % len(added))
for k in added: print("   +", k)
print("== 删除(%d) ==" % len(removed))
for k in removed: print("   -", k)

# 取两套字表（稳健：按空白切整数，首数是 count，其余是码点）
def get_cl(v, name="charlist_CH", ext="txt"):
    e = v.find(name, ext)
    if not e: return None
    nums = [int(x) for x in v.read(e).decode('utf-8', 'replace').split()
            if x.strip().lstrip('-').isdigit()]
    # 首数是 count，丢弃，取后续码点（若后续数量 == count 则正确）
    if nums and nums[0] == len(nums) - 1:
        return nums[1:]
    return nums

cl_trad = get_cl(v_van)   # 繁体
cl_simp = get_cl(v_loc)   # 简体
print("\n== 字表 ==  繁体条目=%d  简体条目=%d" % (len(cl_trad), len(cl_simp)))

# 字表 rev：slot->char
def make_rev(cl):
    return {i + SHIFT: chr(cp) for i, cp in enumerate(cl)}
def make_slot(cl):
    d = {}
    for i, cp in enumerate(cl):
        d.setdefault(cp, i + SHIFT)
    return d

rev_trad, rev_simp = make_rev(cl_trad), make_rev(cl_simp)
slot_trad, slot_simp = make_slot(cl_trad), make_slot(cl_simp)

def decode_table(d, revmap, count):
    """正确只扫记录区。返回 (ok_records, bad_records, samples)。"""
    buckets, cnt, off_at, offs = file_offsets(d)
    ok = bad = 0
    samples = []
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d) - 10): continue
        units, end = read_units(d, off + 8)
        if units is None:
            bad += 1; continue
        # 逐槽解码
        txt = []
        rec_bad = False
        for vv, _ in units:
            if vv < 0x100:
                txt.append(chr(vv))
            else:
                idx = vv - SHIFT
                if 0 <= idx < count:
                    txt.append(revmap.get(vv, '\ufffd'))
                else:
                    rec_bad = True
                    txt.append('\ufffd')
        if rec_bad:
            bad += 1
            if len(samples) < 3:
                samples.append("BAD: " + ''.join(txt)[:40])
        else:
            ok += 1
            if len(samples) < 6 and any(ord(c) > 0x100 for c in ''.join(txt)):
                samples.append("OK: " + ''.join(txt)[:40])
    return ok, bad, samples

print("\n== 各 le_strings 表：繁体表 vs 简体表 解码对比 ==")
print("%-28s %8s %8s | %8s %8s  判定" % ("name", "繁OK", "繁BAD", "简OK", "简BAD"))
tables = [(e['name'], e['ext']) for e in v_loc.entries()
          if e['ext'] == 'le_strings']
for name, ext in tables:
    e = v_loc.find(name, ext)
    d = v_loc.read(e)
    ok_t, bad_t, s_t = decode_table(d, rev_trad, len(cl_trad))
    ok_s, bad_s, s_s = decode_table(d, rev_simp, len(cl_simp))
    verdict = ""
    if bad_s == 0 and ok_s > 0:
        verdict = "简表OK(已正确)"
    elif bad_t == 0 and bad_s > 0:
        verdict = "★繁表OK简表坏(需重映射)"
    elif bad_t > 0:
        verdict = "?两表都坏"
    print("%-28s %8d %8d | %8d %8d  %s" % (name, ok_t, bad_t, ok_s, bad_s, verdict))
    if bad_t == 0 and bad_s > 0:
        for s in s_s[:2]:
            print("      简表样本: %s" % s)
        for s in s_t[:2]:
            print("      繁表样本: %s" % s)
