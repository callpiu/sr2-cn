import sys, re
sys.path.insert(0, r"F:\sr2-cn")
from _vpp import Vpp

def parse_charlist(txt):
    m = re.search(r"count\s*=\s*(\d+)", txt)
    body = txt[m.end():]
    return [int(x) for x in re.findall(r"\d+", body)]

Lg = parse_charlist(open(r"F:\sr2-cn\_fontdump\charlist_CH.txt", encoding="utf-8", errors="replace").read())
v = Vpp(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig")
Lo = parse_charlist(v.read(v.find("charlist_CH", "txt")).decode("utf-8", "replace"))

def ch(L, i):
    return chr(L[i]) if 0 <= i < len(L) else "?"

slots = [403, 1868, 1067, 454, 364, 2699, 2328, 423, 1222]
rendered = list("任璨偶巧位雄衡伪该")
correct = list("你的弟兄们需要保护")

print("slot  渲染  |  游[s]  游[s-256] 游[s-288] 游[s-32] | 官[s]  官[s-256] 官[s-288] | 游[渲染字idx] 官[渲染字idx]")
for s, r, c in zip(slots, rendered, correct):
    print("%5d %s   | %s    %s     %s    %s  | %s    %s     %s   | %s %s" % (
        s, r,
        ch(Lg, s), ch(Lg, s - 256), ch(Lg, s - 288), ch(Lg, s - 32),
        ch(Lo, s), ch(Lo, s - 256), ch(Lo, s - 288),
        Lg.index(ord(r)) if ord(r) in Lg else "-",
        Lo.index(ord(r)) if ord(r) in Lo else "-"))
print()
print("正确字在游表下标:", [(c, Lg.index(ord(c)) if ord(c) in Lg else None) for c in correct])
print("渲染字在游表下标:", [(r, Lg.index(ord(r)) if ord(r) in Lg else None) for r in rendered])
