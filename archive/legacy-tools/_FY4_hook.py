"""FY4: inspect the loadcharlist hook at 0x7F4430 in SR2_pc.exe.
"""
import struct, os

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def rva_to_off(pe, rva):
    e_lfanew = struct.unpack_from("<I", pe, 0x3C)[0]
    nsec = struct.unpack_from("<H", pe, e_lfanew + 6)[0]
    opt = e_lfanew + 24
    optsize = struct.unpack_from("<H", pe, e_lfanew + 20)[0]
    base = struct.unpack_from("<I", pe, opt + 28)[0]
    sec = opt + optsize
    for i in range(nsec):
        o = sec + i * 40
        vsize, vaddr, rsize, roff = struct.unpack_from("<IIII", pe, o + 8)
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return roff + (rva - vaddr), base
    return None, base

for exe in ("SR2_pc.exe", "sr2_pc_unpatched.exe"):
    p = os.path.join(G, exe)
    if not os.path.isfile(p):
        print(exe, "MISSING"); continue
    pe = open(p, "rb").read()
    print("=" * 60)
    print(exe, "size", len(pe))
    for addr in (0x7F4430, 0x7F4F60):
        off, base = rva_to_off(pe, addr)
        if off is None:
            print("  0x%X -> not mapped" % addr); continue
        b = pe[off:off+16]
        print("  0x%X -> file 0x%X : %s" % (addr, off, b.hex()))
        if b[0] == 0xE9:
            rel = struct.unpack_from("<i", b, 1)[0]
            tgt = addr + 5 + rel
            print("      JMP -> 0x%X  (RVA)" % tgt)
            o2, _ = rva_to_off(pe, tgt)
            if o2:
                print("      target bytes:", pe[o2:o2+32].hex())
        elif b[0] == 0xE8:
            rel = struct.unpack_from("<i", b, 1)[0]
            print("      CALL -> 0x%X" % (addr + 5 + rel))
