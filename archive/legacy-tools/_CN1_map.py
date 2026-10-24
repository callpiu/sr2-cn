import sys, re
sys.path.insert(0, r"F:\sr2-cn")
from _vpp import Vpp

def parse_charlist(txt):
    # 返回 codepoint 列表
    m = re.search(r"count\s*=\s*(\d+)", txt)
    n = int(m.group(1)) if m else None
    body = txt[m.end():] if m else txt
    nums = [int(x) for x in re.findall(r"\d+", body)]
    return n, nums

game = open(r"F:\sr2-cn\_fontdump\charlist_CH.txt", "r", encoding="utf-8", errors="replace").read()
ng, Lg = parse_charlist(game)
print("游戏内 charlist_CH: count=%s 解析出=%d" % (ng, len(Lg)))

v = Vpp(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig")
e = v.find("charlist_CH", "txt")
off = v.read(e).decode("utf-8", "replace")
no, Lo = parse_charlist(off)
print("官方   charlist_CH: count=%s 解析出=%d" % (no, len(Lo)))

def idx_of(L, ch):
    cp = ord(ch)
    return L.index(cp) if cp in L else None

pairs = [("你", "任"), ("的", "璨"), ("弟", "偶"), ("兄", "巧"), ("们", "位"),
         ("需", "雄"), ("要", "衡"), ("保", "伪"), ("护", "该")]
slots = [403, 1868, 1067, 454, 364, 2699, 2328, 423, 1222]
print()
print("%-4s %-4s %-6s %-6s %-6s %-6s %-6s" % ("正", "误", "slot", "slot-256", "idx正(游)", "idx误(游)", "差"))
for (a, b), s in zip(pairs, slots):
    ia = idx_of(Lg, a); ib = idx_of(Lg, b)
    d = (ib - ia) if (ia is not None and ib is not None) else None
    print("%-4s %-4s %-6d %-6d %-8s %-8s %-6s" % (a, b, s, s - 256, ia, ib, d))

print()
print("误字在官方表下标:", [(b, idx_of(Lo, b)) for a, b in pairs])
print("正字在官方表下标:", [(a, idx_of(Lo, a)) for a, b in pairs])
