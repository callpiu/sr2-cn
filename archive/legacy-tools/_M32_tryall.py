# -*- coding: utf-8 -*-
# 用游戏里所有 charlist 反推 22 字乱码句的源文本，找出哪个产出通顺中文
import sys, struct, os
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp

VANILLA = r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017"
CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"


def parse_charlist(raw):
    B = []
    for L in raw.split(b"\r\n"):
        s = L.strip()
        if not s or s.startswith(b"//") or s.startswith(b"count="):
            continue
        for tok in s.split():
            if tok.isdigit():
                B.append(chr(int(tok)))
    return B


cn = Vpp(CN)
f = Font(CN)
B = [chr(c) for c in f.charlist]
bidx = {c: i for i, c in enumerate(B)}

DISP = "任璨偶巧们校衡勾远藐乱携伪该亡们通像匪冰挺拮"

# 列出所有 charlist
print("=== 官方原版 patch 里的 charlist ===")
vv = Vpp(VANILLA)
tabs = {}
for e in vv.entries():
    if (e["ext"] or "").lower() == "txt" and "charlist" in (e["name"] or "").lower():
        raw = vv.read(e)
        t = parse_charlist(raw)
        tabs["官方:" + e["name"]] = t
        print("  %-16s %d 项" % (e["name"], len(t)))
tabs["汉化:charlist_CH"] = B

print("\n=== 用各表反推：源字 = 表[B.index(显示字)] ===")
for tag, tab in tabs.items():
    out = []
    ok = True
    for d in DISP:
        if d not in bidx:
            out.append("?"); ok = False; continue
        k = bidx[d]
        out.append(tab[k] if k < len(tab) else "?")
    s = "".join(out)
    han = sum(1 for c in s if 0x4E00 <= ord(c) <= 0x9FFF)
    print("  %-22s (%d项) %s   汉字%d/%d" % (tag, len(tab), s, han, len(s)))

# 反向：若槽位按表 X 编码、引擎按 B 解码，则 显示字 = B[X.index(源字)]
# => 源字 = X[B.index(显示字)]  已试。再试：源字 = X 中码点满足 X.index(c)=B.index(d) 的另一个解
print("\n=== 另一种：若源字码点 cp，槽位=B.index(c) 但引擎用 X 解码 ===")
print("   显示字 d = X[B.index(源字)]  =>  源字在 B 的位置 = B.index(d)")
print("   => 源字 = B[B.index(d)] = d  （自反，无意义）")

# 关键：也许这条字幕的槽位流里含非 B 可编码的字符（如繁体）
# 直接搜 le_strings 里所有 22 字记录，看哪条的「引擎解码后」== 显示句
print("\n=== 搜 le_strings：解码后等于显示句的记录 ===")
target = DISP.replace("们", "们")
found = 0
for name in ("voice_script_CH", "static_CH", "platform_pc_CH"):
    d = cn.read(cn.find(name, "le_strings"))
    buckets, = struct.unpack_from("<H", d, 6)
    count, = struct.unpack_from("<I", d, 8)
    ptrs = struct.unpack_from("<%dI" % count, d, 12 + buckets * 8)
    for i in range(count):
        p = ptrs[i]
        if p + 6 > len(d):
            continue
        q = p + 4
        sl = []
        while True:
            s, = struct.unpack_from(">H", d, q)
            q += 2
            if s == 0:
                break
            sl.append(s)
        t = "".join(B[s - 32] if 0 <= s - 32 < len(B) else "{%d}" % s for s in sl)
        if t == target:
            a, b_ = struct.unpack_from("<HH", d, p)
            print("  ★ %s [%04X.%04X] %s" % (name, a, b_, t))
            found += 1
print("  找到", found, "条")
