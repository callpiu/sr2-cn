# -*- coding: utf-8 -*-
# Option B：检查 charlist_CH.txt 里注释行的位置与内容
# 假设：引擎没正确跳过中间注释行，把注释里的数字当成字符表项 -> 索引偏移
import sys, re, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font

f = Font(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")
raw = f.v.read(f.cl_entry)
print("文件大小 = %d 字节" % len(raw))

lines = raw.split(b"\r\n")
print("总行数 = %d" % len(lines))
print()
print("=== 所有注释行 / 空行 / 非数字行 ===")
for i, L in enumerate(lines):
    s = L.strip()
    if not s:
        print("  [%4d] (空行)" % i)
    elif s.startswith(b"//"):
        nums = re.findall(rb"\d+", s)
        print("  [%4d] 注释: %s" % (i, s[:80].decode("ascii", "replace")))
        if nums:
            print("         含数字: %s" % nums)
    elif not s.isdigit():
        print("  [%4d] 其它: %r" % (i, s[:80]))

print()
print("=== 前 6 行原文 ===")
for i in range(6):
    print("  [%d] %r" % (i, lines[i][:100]))

print()
print("=== 后 6 行原文 ===")
for i in range(max(0, len(lines) - 6), len(lines)):
    print("  [%d] %r" % (i, lines[i][:100]))

# 统计数字总数
nums = re.findall(rb"\d+", raw)
print("\n全文数字串总数 = %d（应为 1 个 count 值 + 2795 个码点 = 2796）" % len(nums))
m = re.search(rb"count\s*=\s*(\d+)", raw)
print("count 声明 =", m.group(1) if m else "无")
after = raw[m.end():]
nums_after = re.findall(rb"\d+", after)
print("count 之后的数字串 = %d 个" % len(nums_after))
