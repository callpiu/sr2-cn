# -*- coding: utf-8 -*-
"""GK1(A轮): exe 字体名表 —— 一次穷举，把全部 11 个字体名都指向 fnt_chinese。

上一轮只改了 6 个（fnt_body_n/s, fnt_bodyital_n/s, fnt_head_n/s）无效，
说明 thin_overlay 可能映射到 jap / fnt_korea / fnt_cz / fnt_cz_s / ug-debug。
本轮全覆盖。

槽位宽度（原版 exe）：
  jap          10358732  4 B  -> 与 fnt_chinese 合并为 16 B
  fnt_chinese  10358736 12 B
  fnt_korea    10358748 12 B
  fnt_cz       10358760  8 B  -> 与 fnt_cz_s 合并为 20 B
  fnt_cz_s     10358768 12 B
  fnt_body_n   10358780 12 B
  fnt_body_s   10358792 12 B
  fnt_bodyital_n 10358804 16 B
  fnt_bodyital_s 10358820 16 B
  fnt_head_n   10358836 12 B
  fnt_head_s   10358848 12 B
  ug-debug     10358860 12 B
"""
import sys, os, shutil, hashlib
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
EXE = os.path.join(G, "SR2_pc.exe")
ORIG = r"F:\sr2-cn\SR2_pc.exe.orig"
BAK = r"F:\sr2-cn\_backup_EXE"
os.makedirs(BAK, exist_ok=True)

def md5f(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

print("当前 exe md5:", md5f(EXE))
print("orig  exe md5:", md5f(ORIG))

# 备份当前 exe（含上一轮的改名）
dst = os.path.join(BAK, "SR2_pc.exe.before_allfont")
if not os.path.exists(dst):
    shutil.copy2(EXE, dst)
    print("备份 ->", dst)

d = bytearray(open(ORIG, "rb").read())
NEW = b"fnt_chinese"

def put(off, slot, expect):
    cur = bytes(d[off:off+slot])
    name = cur.split(b"\x00")[0]
    assert name == expect, (off, name, expect)
    assert slot >= len(NEW) + 1, (off, slot)
    d[off:off+slot] = NEW + b"\x00" * (slot - len(NEW))
    print("  %-16s @%d 槽位 %2d -> %s" % (expect.decode(), off, slot, NEW.decode()))

# jap + fnt_chinese 合并成 16 B
put(10358732, 16, b"jap")
# fnt_cz + fnt_cz_s 合并成 20 B
put(10358760, 20, b"fnt_cz")
# 其余单独
put(10358748, 12, b"fnt_korea")
put(10358780, 12, b"fnt_body_n")
put(10358792, 12, b"fnt_body_s")
put(10358804, 16, b"fnt_bodyital_n")
put(10358820, 16, b"fnt_bodyital_s")
put(10358836, 12, b"fnt_head_n")
put(10358848, 12, b"fnt_head_s")
put(10358860, 12, b"ug-debug")

open(EXE, "wb").write(bytes(d))
print("\n已写入。新 md5:", md5f(EXE))

# 校验
d2 = open(EXE, "rb").read()
seg = d2[10358732:10358880]
print("\n字体名表 10358732..10358880:")
print(" ", "".join(chr(c) if 32 <= c < 127 else ("|" if c == 0 else ".") for c in seg))
import re
print("\n该区间内所有可打印串:", [m.group().decode() for m in re.finditer(rb"[\x20-\x7e]{2,}", seg)])
