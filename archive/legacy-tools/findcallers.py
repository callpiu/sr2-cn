import struct, os
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
b = open(os.path.join(G,"SR2_pc.exe"),"rb").read()
BASE = 0x400000
def find_calls(target_va):
    """找所有 E8 rel32 调用 target 的位置"""
    res = []
    tgt_off = target_va - BASE
    for i in range(len(b)-5):
        if b[i] == 0xE8:
            rel = struct.unpack_from("<i", b, i+1)[0]
            if BASE + i + 5 + rel == target_va:
                res.append(BASE + i)
    return res
print("=== 调用 0xCAD04E 的位置 ===")
for va in find_calls(0xCAD04E)[:20]:
    print("  0x%X" % va)
print()
# 找 0x465C2B 所在函数的起点
off = 0x465C2B - BASE
s = off
while s > off-0x300:
    if b[s] == 0xCC and b[s+1] == 0xCC:
        s += 1; break
    s -= 1
print("0x465C2B 所在函数起点: 0x%X" % (BASE+s))
print("  函数头 48 字节: %s" % " ".join("%02X"%x for x in b[s:s+48]))
print()
print("=== 调用 0x465C2B 所在函数起点的位置 ===")
fs = BASE+s
for va in find_calls(fs)[:15]:
    print("  0x%X" % va)
