import struct
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
b = open(G + r"\SR2_pc.exe","rb").read()
BASE = 0x400000
def at(va, n=48):
    o = va - BASE
    return b[o:o+n].hex(" ")
# loadcharlist @ 0x7F4430，看它如何写 cc_list (0x2528B2C) / num_cchars (0x2528B30)
print("=== loadcharlist @ 0x7F4430 (前 240 字节) ===")
o = 0x7F4430 - BASE
chunk = b[o:o+240]
for i in range(0, len(chunk), 16):
    print("  %08X  %s" % (0x7F4430+i, chunk[i:i+16].hex(" ")))
