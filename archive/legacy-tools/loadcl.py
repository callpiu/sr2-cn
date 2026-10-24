import struct
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
b = open(G + r"\SR2_pc.exe","rb").read()
BASE = 0x400000
def va2off(va): return va - BASE
# compress_char @ 0x7F4F60
for va, nm, ln in ((0x7F4F60,"compress_char",64), (0x7F4BC0,"display/req_string",48)):
    off = va2off(va)
    print("=== %s @ VA 0x%X (文件偏移 0x%X) ===" % (nm, va, off))
    print("  %s" % b[off:off+ln].hex(" "))
    print()
# 找 cc_list / num_cchars 的引用
print("=== 搜索对 0x2528B2C / 0x2528B30 的引用 ===")
for target in (0x2528B2C, 0x2528B30):
    pat = struct.pack("<I", target)
    idx = 0; hits=[]
    while True:
        i = b.find(pat, idx)
        if i < 0: break
        hits.append(i); idx = i+1
    print("  0x%08X 出现 %d 次: %s" % (target, len(hits), ["0x%X"%h for h in hits[:8]]))
