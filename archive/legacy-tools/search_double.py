"""排查：食物界面 "double" -> "双胞胎" 的来源。
搜索范围：patch.vpp_pc 所有 le_strings（含英文）、DLC dlc_ch.le_strings、juiced 系列。
策略：① 用 charlist 取得 双/胞/胎 的槽位，搜这些槽位的 16-bit 序列；② 直接搜 ascii "double"；
③ 列出所有含 "double" 的英文记录与其同记录的中文字（若同串里有中文则可能是翻译来源）。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, SHIFT

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# ---- 取 charlist 槽位 ----
def charlist_slots(vpp_path):
    v = Vpp(vpp_path)
    e = v.find("charlist_CH", "txt")
    cl = v.read(e).decode('utf-8').split('\n')
    slots = {}
    for i, s in enumerate(cl):
        if s.strip().isdigit():
            slots[chr(int(s))] = i + SHIFT
    return v, slots

v, slots = charlist_slots(os.path.join(GAME, "patch.vpp_pc"))
print("charlist 命中槽位:", {c: slots.get(c) for c in ['双','胞','胎','份','倍']})

def iter_recs(v, e):
    b = v.read(e)
    bc, count, oa, offs = file_offsets(b)
    body_off = v.data_start + e['body']
    seen = set()
    for off in offs:
        sp = body_off + off + 8
        if sp in seen:
            continue
        seen.add(sp)
        i = sp; n = len(v.data); vals = []
        while i + 2 <= n:
            b0,b1 = v.data[i],v.data[i+1]
            if b0==0 and b1==0:
                yield vals; break
            vals.append((b0<<8)|b1); i += 2

def search_in(vpp_path, want_ascii=None, want_slots=None, label=""):
    v = Vpp(vpp_path) if not isinstance(vpp_path, Vpp) else vpp_path
    print("\n--- %s ---" % label)
    hits = 0
    for e in v.entries():
        if e['ext'] != 'le_strings':
            continue
        for vals in iter_recs(v, e):
            txt = []
            has_ascii_double = False
            has_want_slot = False
            for x in vals:
                if x < 0x100:
                    txt.append(chr(x))
                    if want_ascii and chr(x).lower() in want_ascii:
                        has_ascii_double = True
                else:
                    c = slots.get(chr(0))  # placeholder
                    txt.append('[%d]'%x)
                    if want_slots and x in want_slots:
                        has_want_slot = True
            s = ''.join(txt)
            if (want_ascii and has_ascii_double) or (want_slots and has_want_slot):
                print("  [%s] %r" % (e['name'], s[:80]))
                hits += 1
    print("  命中 %d 条" % hits)

# 搜 ascii "double"（大小写）
search_in(v, want_ascii="double", label="patch.vpp_pc 含 'double' 的英文串")

# 搜 双/胞/胎 槽位
target_slots = {slots.get(c) for c in ['双','胞','胎','份','倍'] if slots.get(c)}
print("\n目标槽位:", target_slots)
search_in(v, want_slots=target_slots, label="patch.vpp_pc 含 双/胞/胎/份/倍 槽位的串")

# DLC
dlc = os.path.join(GAME, "DLC", "Text", "dlc_ch.le_strings")
if os.path.exists(dlc):
    search_in(dlc, want_ascii="double", label="DLC dlc_ch.le_strings 含 'double'")
    search_in(dlc, want_slots=target_slots, label="DLC 含 双/胞/胎/份/倍 槽位")
else:
    print("\nDLC dlc_ch.le_strings 不存在:", dlc)

# juiced 目录
import glob
for f in glob.glob(r"F:\sr2-cn\**\*juiced*", recursive=True):
    if f.endswith('.le_strings'):
        print("\njuiced le_strings:", f)
        search_in(f, want_ascii="double", label="  %s 含 double"%os.path.basename(f))
