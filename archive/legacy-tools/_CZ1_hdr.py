import struct
b = open(r"F:\sr2-cn\_fontdump\fnt_chinese.vf3_pc", "rb").read()
print("vf3 size =", len(b))
for pat in (b"VFNT", b"fnt_chinese.peg", b"fnt_chinese_nobdr.tga"):
    print("%-24s off=0x%X" % (pat.decode(), b.find(pat)))
print("头 0x00..0xE0:")
for off in range(0, 0xE0, 16):
    print("  0x%03X  %s" % (off, b[off:off+16].hex(" ")))
print()
print("N(0x08) =", struct.unpack_from("<I", b, 8)[0])
print("w(0x0C) =", struct.unpack_from("<I", b, 0x0C)[0], " h(0x10) =", struct.unpack_from("<I", b, 0x10)[0])
N = struct.unpack_from("<I", b, 8)[0]
for H in (0xBC, 0xD0):
    print("H=0x%X: 记录起=0x%X U起=0x%X V起=0x%X 末=0x%X (文件%d) 差=%d" % (
        H, H, H+N*16, H+N*16+N*4, H+N*24, len(b), H+N*24-len(b)))
# 用 H=0xBC 打印前几条记录与 U/V 头
H = 0xBC
print("\nH=0xBC 记录[0..3] (u32x4):")
for i in range(4):
    print("   ", struct.unpack_from("<4I", b, H+i*16))
print("H=0xBC 记录[2791..2794]:")
for i in range(2791, 2795):
    print("   ", struct.unpack_from("<4I", b, H+i*16))
U = struct.unpack_from("<%dI" % N, b, H+N*16)
V = struct.unpack_from("<%dI" % N, b, H+N*16+N*4)
print("\nU[0:6]=", U[:6], " V[0:6]=", V[:6])
print("U[371]=", U[371], "V[371]=", V[371], "  U[403]=", U[403], "V[403]=", V[403])
