# -*- coding: utf-8 -*-
"""GG5: dump SR2_pc.exe 里那段硬编码字体名表。"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
P = r"G:\SteamLibrary\steamapps\common\Saints Row 2\SR2_pc.exe"
d = open(P, "rb").read()
print("exe size", len(d))
pos = d.find(b"fnt_body_n")
print("fnt_body_n @", pos)
# 往前找 400 字节内的字符串区
start = max(0, pos - 400)
end = min(len(d), pos + 600)
blk = d[start:end]
print("\n--- 区域 %d..%d 的 NUL 分隔字符串 ---" % (start, end))
cur = bytearray()
for i, c in enumerate(blk):
    if c == 0:
        if cur:
            s = bytes(cur)
            if all(32 <= x < 127 for x in s):
                print("  @%d  %s" % (start + i - len(s), s.decode()))
            cur = bytearray()
    else:
        cur.append(c)
if cur:
    s = bytes(cur)
    if all(32 <= x < 127 for x in s):
        print("  @%d  %s" % (start + end - len(s) - start, s.decode()))

print("\n--- 可打印视图 ---")
print("".join(chr(c) if 32 <= c < 127 else ("|" if c == 0 else ".") for c in blk))
