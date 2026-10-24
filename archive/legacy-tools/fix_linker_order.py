# -*- coding: utf-8 -*-
"""修正 link_pe2.py 的 .reloc 生成顺序。"""
import re
import io

p = r"F:\sr2-cn\link_pe2.py"
src = io.open(p, encoding="utf-8").read()

# 1) 找到 "    # ---- 生成 .reloc 节 ----" 到 "        print(\"  .reloc: 无（不需要）\")" 的整块
start = src.index("    # ---- 生成 .reloc 节 ----")
end_marker = '        print("  .reloc: 无（不需要）")'
end = src.index(end_marker) + len(end_marker)
block = src[start:end]
src = src[:start] + src[end:]

# 2) 从 block 里去掉外层缩进（准备插到文件偏移计算之前）
lines = []
for ln in block.split("\n"):
    if ln.startswith("    "):
        lines.append(ln[4:])
    else:
        lines.append(ln)
newblock = "\n".join(lines)

# 3) 插入到 "# 文件偏移" 之前
anchor = "    # 文件偏移\n"
idx = src.index(anchor)
src = src[:idx] + newblock + "\n\n" + src[idx:]

io.open(p, "w", encoding="utf-8").write(src)
print("已重排 .reloc 生成顺序")
print()
# 打印新顺序的关键行
for i, ln in enumerate(src.split("\n"), 1):
    s = ln.strip()
    if (s.startswith("# ----") or "reloc_rva = reloc_size" in s
            or s.startswith("# 文件偏移") or "size_of_image = va" in s):
        print("  %4d: %s" % (i, ln))
