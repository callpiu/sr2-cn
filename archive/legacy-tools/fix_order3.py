# -*- coding: utf-8 -*-
"""把【文件偏移计算】移到 .reloc 生成之后。"""
import io

p = r"F:\sr2-cn\link_pe2.py"
src = io.open(p, encoding="utf-8").read()

# 提取文件偏移块
fstart = src.index("    # 文件偏移\n")
fend_marker = "    size_of_file = fo\n"
fend = src.index(fend_marker) + len(fend_marker)
fblock = src[fstart:fend]
src = src[:fstart] + src[fend:]

# 插入到 .reloc 块之后（即 "size_of_image = va" 最后一次出现之后）
# 找 .reloc 块结束位置：'print("  .reloc: 无（不需要）")'
m = 'print("  .reloc: 无（不需要）")'
idx = src.index(m) + len(m)
# 该行后面就是 size_of_image = va
nxt = src.index("size_of_image = va", idx) + len("size_of_image = va")
src = src[:nxt] + "\n\n" + fblock.rstrip() + "\n" + src[nxt:]

io.open(p, "w", encoding="utf-8").write(src)
print("已重排文件偏移块")
for i, ln in enumerate(src.split("\n"), 1):
    s = ln.strip()
    if (s.startswith("# ----") or "size_of_image = va" in s
            or s.startswith("# 文件偏移") or "size_of_file = fo" in s):
        print("  %4d: %s" % (i, ln))
