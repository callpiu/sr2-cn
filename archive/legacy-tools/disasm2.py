import struct, os
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
b = open(os.path.join(G,"SR2_pc.exe"),"rb").read()
BASE = 0x400000
def hexdump(va, n=128, label=""):
    off = va - BASE
    print("=== %s @ 0x%X ===" % (label, va))
    for i in range(0, n, 16):
        o = off + i
        line = b[o:o+16]
        print("  %08X  %s" % (BASE+o, " ".join("%02X"%x for x in line)))
    print()
# 找函数起点：向前找 int3 填充 / push ebp; mov ebp,esp
off = 0xCAD24E - BASE
start = off
while start > off-0x200:
    if b[start] == 0xCC and b[start+1] == 0xCC:
        start += 1
        break
    start -= 1
print("推测函数起点: 0x%X (+0x%X)" % (BASE+start, start))
hexdump(BASE+start, 96, "函数开头")
hexdump(0x00CAD1E0, 128, "崩溃前后")
hexdump(0x00465C2B, 96, "调用者 0x465C2B")
