"""定位「thin_overlay」字符串的代码引用（不是指针表，而是指令里的立即数地址）。

x86 里 push offset str 的形式是 68 <u32 VA>，
或 mov <reg>, offset str = B8/B9/... <u32 VA>。
所以要搜的字节模式是「68 <VA>」等，而不是单独的 u32。
"""
import os, struct

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
d = open(os.path.join(G, "SR2_pc.exe"), "rb").read()

TARGETS = {
    "jap": 0x9E0FCC,
    "fnt_chinese": 0x9E0FD0,
    "fnt_korea": 0x9E0FDC,
    "fnt_cz": 0x9E0FE8,
    "fnt_body_n": 0x9E0FFC,
    "fnt_body_s": 0x9E1008,
    "fnt_bodyital_n": 0x9E1014,
    "fnt_bodyital_s": 0x9E1022,
    "fnt_head_n": 0x9E1032,
    "fnt_head_s": 0x9E103E,
    "debug": 0x9E1058,
    "thin": 0x9E1060,
    "thin_overlay": 0x9E1068,
    "header_n": 0x9E1078,
    "header_n_overlay": 0x9E1088,
    "bodyital_overlay": 0x9E1098,
}

# 各种可能引用立即数地址的指令前缀
PREFIXES = {
    0x68: "push imm32",
    0xB8: "mov eax,imm32",
    0xB9: "mov ecx,imm32",
    0xBA: "mov edx,imm32",
    0xBB: "mov ebx,imm32",
    0xBE: "mov esi,imm32",
    0xBF: "mov edi,imm32",
}

print("=== 引用这些字符串的指令 ===")
for name, va in TARGETS.items():
    pat = struct.pack("<I", va)
    hits = []
    j = 0
    while True:
        k = d.find(pat, j)
        if k < 0:
            break
        if k > 0 and d[k - 1] in PREFIXES:
            hits.append((k - 1, PREFIXES[d[k - 1]]))
        j = k + 1
    if hits:
        print("  %-18s VA=0x%08X  被 %d 处指令引用:" % (name, va, len(hits)))
        for off, ins in hits[:6]:
            print("      文件 0x%06X  VA 0x%06X  %s" % (off, off, ins))
    else:
        print("  %-18s VA=0x%08X  (无直接指令引用)" % (name, va))
print()

# 看看字符串池后面紧邻的数据（可能是别名表结构）
print("=== 字符串池 0x9E10A8 之后 128 字节 ===")
S = 0x9E10A8
seg = d[S:S + 128]
for k in range(0, len(seg), 16):
    print("  %08X  %s  |%s|" % (S + k,
                               " ".join("%02X" % x for x in seg[k:k + 16]),
                               "".join(chr(x) if 32 <= x < 127 else "." for x in seg[k:k + 16])))
