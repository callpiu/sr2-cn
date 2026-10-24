# -*- coding: utf-8 -*-
"""运行时字表转储：读 cc_list(0x2528B2C/0x2528B30) 全量，输出 unicode->glyph 映射。
用于定案「活动字幕乱码」：需要游戏进入任意能显示中文的界面（使 num_cchars != 0）。
"""
import sys, struct, json, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "F:/sr2-cn")
import ce_mini as C

pid = C.find_pid()
print("pid =", pid)
if not pid:
    sys.exit("游戏未运行")
h = C.open_process(pid)

PTR = 0x2528B2C
CNT = 0x2528B30
FLAG = 0x2528B28
TBL2_PTR = 0x2528B34
TBL2_CNT = 0x2528B38

for attempt in range(3):
    num = struct.unpack("<I", C.read_mem(h, CNT, 4))[0]
    ptr = struct.unpack("<I", C.read_mem(h, PTR, 4))[0]
    print("num_cchars=%d  cc_list=0x%08X" % (num, ptr))
    if 0 < num < 20000 and 0x10000 < ptr < 0x80000000:
        break
    print("  ... 字表尚未加载（仍停在菜单？），1 秒后重试")
    time.sleep(1)
else:
    sys.exit("cc_list 仍为空：请先让游戏进入能显示中文的界面（主菜单/游戏中）再运行本脚本。")

raw = C.read_mem(h, ptr, num * 4)
pairs = struct.unpack("<%dH" % (num * 2), raw)
entries = [(pairs[i * 2], pairs[i * 2 + 1]) for i in range(num)]
print("读取 %d 项" % len(entries))

# 自洽性检查：glyph == index ?
mismatch = [i for i, (u, g) in enumerate(entries) if g != i]
print("glyph != index 的项数: %d / %d" % (len(mismatch), num))
print("前 20 项 (unicode, glyph):", [(hex(u), hex(g)) for u, g in entries[:20]])
if mismatch:
    print("前 20 个不一致:", [(i, hex(entries[i][0]), hex(entries[i][1])) for i in mismatch[:20]])

# 单调性检查（校验器 0x7F4E30 假定升序）
desc = [i for i in range(1, num) if entries[i][0] < entries[i - 1][0]]
print("unicode 非升序处: %d (前 10: %s)" % (len(desc), desc[:10]))

# 目标字符索引
targets = "你的兄弟们赶到他们的目的地需要保护直升机装甲车生命值"
print("\n目标字符在运行时表的位置:")
uni2idx = {}
for i, (u, g) in enumerate(entries):
    uni2idx.setdefault(u, i)
for ch in dict.fromkeys(targets):
    u = ord(ch)
    i = uni2idx.get(u)
    if i is None:
        print("  %s U+%04X  表中不存在" % (ch, u))
    else:
        print("  %s U+%04X  index=%d  slot(idx+0x20)=%d  glyph=%d" % (ch, u, i, i + 0x20, entries[i][1]))

out = {
    "num": num,
    "cc_list": ptr,
    "entries": entries,
    "mismatch_count": len(mismatch),
}
with open("F:/sr2-cn/_runtime_charlist.json", "w", encoding="utf-8") as f:
    json.dump({"num": num, "cc_list": hex(ptr), "pairs": [[u, g] for u, g in entries]}, f)
print("\n已保存 F:/sr2-cn/_runtime_charlist.json")
