import sys, os, struct
import numpy as np
W = r"F:\sr2-cn"
raw = open(os.path.join(W,"_juice_fix","charlist_CH.txt"),"rb").read()
print("=== 第三方 charlist 格式 ===")
print("  前 200 字节: %r" % raw[:200])
print("  后 60 字节 : %r" % raw[-60:])
lines = raw.decode("utf-8","replace").split("\n")
cps = [int(l) for l in lines if l.strip().isdigit()]
print("  解析出 %d 个码点（文档说 2795）" % len(cps))
print("  前 12 个: %s" % cps[:12])
print("  末 20 个: %s" % "".join(chr(c) for c in cps[-20:]))
print()
# 找 ASCII A-Z 的索引
idx = {}
for i,c in enumerate(cps):
    if 0x20 <= c <= 0x7E:
        idx.setdefault(chr(c), i)
print("  ASCII 0x20-0x7E 在表内的索引范围: %s .. %s (共 %d 个)" % (
    min(idx.values()) if idx else None, max(idx.values()) if idx else None, len(idx)))
for ch in "JUICEDisplay":
    print("    %s -> 索引 %s (槽 %s)" % (ch, idx.get(ch), (idx.get(ch)+0x20) if ch in idx else None))
print()
vf3 = open(os.path.join(W,"_juice_fix","fnt_chinese.vf3_pc"),"rb").read()
print("=== 第三方 vf3 ===")
print("  大小 %d" % len(vf3))
print("  0x04 Version   = %d" % struct.unpack_from("<i",vf3,0x04)[0])
print("  0x08 NumChars  = %d" % struct.unpack_from("<i",vf3,0x08)[0])
print("  0x0C FirstAscii= %d" % struct.unpack_from("<i",vf3,0x0C)[0])
print("  0x10 Width     = %d" % struct.unpack_from("<i",vf3,0x10)[0])
print("  0x14 Height    = %d" % struct.unpack_from("<h",vf3,0x14)[0])
print("  0x16 RenderH   = %d" % struct.unpack_from("<h",vf3,0x16)[0])
print("  0x1C CharSpace = %d" % struct.unpack_from("<i",vf3,0x1C)[0])
print("  0x20 KernPairs = %d" % struct.unpack_from("<i",vf3,0x20)[0])
print("  0x24 VertOff   = %d" % struct.unpack_from("<i",vf3,0x24)[0])
print("  0x28 PegName   = %r" % vf3[0x28:0x68].split(b"\0")[0])
