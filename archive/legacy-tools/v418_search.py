"""v418 错字排查：定位坏字位槽号 + OpenSpy/圣徒/霰弹/胞胎 真实记录。
输出：
  A. 关键字的 charlist idx / slot / 是否在表内 / 是否排序
  B. 全部 _CH le_strings 中含目标子串的记录（表名 / blob偏移 / 解码文本 / 每CJK字 slot,idx）
"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units, SHIFT

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC = os.path.join(GAME, "patch.vpp_pc")
v = Vpp(SRC)
print("patch md5:", hashlib.md5(v.data).hexdigest())

# ---- charlist ----
e_cl = v.find("charlist_CH", "txt")
nums = [int(x) for x in v.read(e_cl).decode('utf-8', 'replace').split()
        if x.strip().lstrip('-').isdigit()]
cl = nums[1:] if (nums and nums[0] == len(nums) - 1) else nums
N = len(cl)
print("charlist 条数:", N, " 首数:", nums[0] if nums else None,
      " 排序:", all(cl[i] <= cl[i+1] for i in range(N-1)))
S = {i + SHIFT: chr(c) for i, c in enumerate(cl)}          # slot -> char
CP2IDX = {c: i for i, c in enumerate(cl)}                    # cp -> idx
IDX2CP = {i: c for i, c in enumerate(cl)}

def info(ch):
    if ord(ch) < 0x100:
        return "(ASCII)"
    idx = CP2IDX.get(ord(ch))
    if idx is None:
        return "NOT-IN-TABLE"
    return "idx=%d slot=%d cp=0x%X" % (idx, idx+SHIFT, ord(ch))

print("\n== A. 关键字在字表状态 ==")
for ch in "楼弹徒录连接入份双散倍三胞胎圣建延丈弗伙引开底床":
    print("  %-2s %s" % (ch, info(ch)))

# ---- 解码所有 _CH 表 ----
def decode_table(name):
    ent = v.find(name, "le_strings")
    d = v.read(ent)
    b, c, oa, offs = file_offsets(d)
    recs = []
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d) - 24):
            continue
        u, end = read_units(d, off + 8)
        if u is None:
            continue
        t = "".join(chr(vv) if vv < 0x100 else S.get(vv, '\ufffd') for vv, _ in u)
        recs.append((off, t))
    return d, recs

targets_text = ["OpenSpy", "OPENSPY", "登录", "圣徒", "霰弹", "胞胎", "双", "三胞胎"]
tables = set()
for e in v.entries():
    n = e['name']
    if 'CH' in n and e['ext'] == 'le_strings':
        tables.add(n)
print("\n== CH le_strings 表:", sorted(tables), "==")

print("\n== B. 命中记录 ==")
for name in sorted(tables):
    d, recs = decode_table(name)
    for off, t in recs:
        if any(tg.lower() in t.lower() for tg in targets_text):
            # 每 CJK 字 slot/idx
            u, _ = read_units(d, off + 8)
            detail = []
            for vv, _ in u:
                if vv >= 0x100:
                    idx = vv - SHIFT
                    detail.append("%s(%d)" % (IDX2CP.get(idx, '?'), idx))
            print("  [%s] @0x%X" % (name, off))
            print("      文本: %r" % t)
            print("      CJK槽: %s" % " ".join(detail))
