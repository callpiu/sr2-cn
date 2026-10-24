# -*- coding: utf-8 -*-
"""把 .reloc 生成块移动到【重定位循环之后、文件偏移之前】。"""
import io

p = r"F:\sr2-cn\link_pe2.py"
src = io.open(p, encoding="utf-8").read()

start = src.index("# ---- 生成 .reloc 节 ----")
end_marker = 'print("  .reloc: 无（不需要）")'
end = src.index(end_marker) + len(end_marker)
block = src[start:end]
src = src[:start] + src[end:]

# 去掉块尾部多余空行
block = block.rstrip() + "\n"

# 重新缩进（顶层 -> 函数体 4 空格）
lines = []
for ln in block.split("\n"):
    lines.append(("    " + ln) if ln.strip() else ln)
block = "\n".join(lines)

# 插入点：重定位循环结束（"重定位: 成功" 那行之后）
anchor = 'print("  重定位: 成功 %d, 失败 %d" % (nok, nbad))\n'
idx = src.index(anchor) + len(anchor)
src = src[:idx] + "\n" + block + "\n" + src[idx:]

io.open(p, "w", encoding="utf-8").write(src)
print("已重排")
for i, ln in enumerate(src.split("\n"), 1):
    s = ln.strip()
    if (s.startswith("# ----") or "reloc_rva = reloc_size = 0" in s
            or "重定位: 成功" in s or "size_of_image = va" in s):
        print("  %4d: %s" % (i, ln))
