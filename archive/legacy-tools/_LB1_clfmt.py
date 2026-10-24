# -*- coding: utf-8 -*-
# 检查 charlist_CH.txt 原始格式 + 模拟引擎 fscanf("%d") 解析，看能否复现引擎索引表
import sys, os, re, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
f = Font(os.path.join(G, "patch.vpp_pc"))
raw = f.v.read(f.cl_entry)
print("charlist_CH.txt  size = %d 字节" % len(raw))
print("前 200 字节:")
print("  ", raw[:200])
print("最后 120 字节:")
print("  ", raw[-120:])
print()

# 行分析
lines = raw.split(b"\r\n") if b"\r\n" in raw else raw.split(b"\n")
print("按 \\r\\n 切分行数 =", len(lines), "   按 \\n 切分行数 =", raw.count(b"\n"))
print("是否含 \\r:", b"\r" in raw, " 是否含 \\n:", b"\n" in raw)
print("含 // 注释行数:", sum(1 for L in lines if L.strip().startswith(b"//")))
print("空行数:", sum(1 for L in lines if not L.strip()))
multi = [L for L in lines if len(re.findall(rb"\d+", L)) > 1]
print("含多个数字的行数:", len(multi), "  例:", multi[:5])
nonnum = [L for L in lines if L.strip() and not L.strip().isdigit()
          and not L.strip().startswith(b"//") and b"=" not in L]
print("非纯数字非注释非空行数:", len(nonnum), " 例:", nonnum[:5])
print()

# 引擎解析模型
count_line = raw.split(b"\n")[0].strip()
m = re.search(rb"count\s*=\s*(\d+)", raw)
declared = int(m.group(1)) if m else 0
print("count= 声明值 =", declared)

nums = re.findall(rb"-?\d+", raw[m.end():] if m else raw)
print("正则提取的数字个数 =", len(nums))

# 模型 A：引擎按 fscanf("%d") 顺序读，填进 count 个槽
arrA = [int(x) for x in nums[:declared]]
print("模型A（填满 count 槽）表长 =", len(arrA), " 前5项 =", arrA[:5], " 第370-372项 =", arrA[369:372])

# 观测到的引擎索引
E_OBS = {"你": 331, "的": 1779, "弟": 405, "兄": 962, "们": 357, "需": 2651,
         "要": 2263, "保": 349, "护": 2337}
print("\n=== 各模型下 E(c) 是否等于 arr.index(c) ===")
for nm, arr in (("模型A 全表", arrA),
                ("模型B 去掉前5项", arrA[5:]),
                ("模型C 去掉前1项", arrA[1:])):
    hit = 0
    det = []
    for c, want in E_OBS.items():
        try:
            got = arr.index(ord(c))
        except ValueError:
            got = None
        if got == want:
            hit += 1
        if len(det) < 9:
            det.append("%s:%s/%s" % (c, got, want))
    print("  %-14s 命中=%d/9  %s" % (nm, hit, " ".join(det)))

# 直接看 arr 在 E 索引处是什么字
print("\n=== 各表在引擎索引处的字符 ===")
for nm, arr in (("模型A", arrA), ("模型B(去前5)", arrA[5:]), ("模型C(去前1)", arrA[1:])):
    s = ""
    for c, e in E_OBS.items():
        s += "%s@%d=%s " % (c, e, chr(arr[e]) if 0 <= e < len(arr) else "?")
    print("  %-14s %s" % (nm, s))
