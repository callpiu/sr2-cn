# -*- coding: utf-8 -*-
"""GH1: 把 SR2_pc.exe 字体名表里的 6 个英文字体原地改名为 fnt_chinese。

理由：sr2.vint_proj 已把 thin_overlay 等别名全指向 fnt_chinese 却无效果，
说明别名->字体的解析表硬编码在 exe 内（字体名表紧邻别名名表）。
把英文字体槽位改名后，这些别名就会加载唯一的中文字体 fnt_chinese。
"""
import sys, os, shutil, hashlib
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
EXE = os.path.join(G, "SR2_pc.exe")
BAK = r"F:\sr2-cn\_backup_EXE"

def md5f(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

print("当前 exe md5:", md5f(EXE))
print("orig  exe md5:", md5f(r"F:\sr2-cn\SR2_pc.exe.orig"))

os.makedirs(BAK, exist_ok=True)
dst = os.path.join(BAK, "SR2_pc.exe.before_fontrename")
if not os.path.exists(dst):
    shutil.copy2(EXE, dst); print("备份 ->", dst)

d = bytearray(open(EXE, "rb").read())

# 字体名表：名字 -> 起始偏移（由 GG5 的 dump 得到），每个条目有 NUL 结尾 + 填充
FONTS = {
    b"fnt_body_n":     10358780,
    b"fnt_body_s":     10358792,
    b"fnt_bodyital_n": 10358804,
    b"fnt_bodyital_s": 10358820,
    b"fnt_head_n":     10358836,
    b"fnt_head_s":     10358848,
}
NEW = b"fnt_chinese"

for name, off in FONTS.items():
    cur = bytes(d[off:off + 64])
    end = cur.find(b"\x00")
    assert end > 0, (name, off)
    cur_name = cur[:end]
    assert cur_name == name, (cur_name, name, off)
    # 条目总长 = 下一个条目的起始 - 本起始（用 NUL 后的填充判定）
    # 这里按“名字+NUL”后补齐到与原名等长的槽位（原槽位长度 = 名字长 + 1 向上取整到 4 的倍数）
    slot = ((end + 1 + 3) // 4) * 4
    assert slot >= len(NEW) + 1, (name, slot)
    d[off:off + slot] = NEW + b"\x00" * (slot - len(NEW))
    print("  %-16s @%d 槽位 %d 字节 -> %s" % (name.decode(), off, slot, NEW.decode()))

open(EXE, "wb").write(bytes(d))
print("已写入。新 md5:", md5f(EXE))

# 回读校验
d2 = open(EXE, "rb").read()
for name, off in FONTS.items():
    e = d2.find(b"\x00", off)
    got = d2[off:e]
    print("  校验 @%d -> %s" % (off, got.decode()))
print("区域内可打印视图:")
print("".join(chr(c) if 32 <= c < 127 else ("|" if c == 0 else ".") for c in d2[10358720:10358880]))
