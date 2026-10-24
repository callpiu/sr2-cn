import struct, os
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
def exports(path):
    d = open(path,"rb").read()
    if d[:2] != b"MZ": return None
    e_lfanew = struct.unpack_from("<I", d, 0x3C)[0]
    if d[e_lfanew:e_lfanew+4] != b"PE\0\0": return None
    coff = e_lfanew+4
    nsec, = struct.unpack_from("<H", d, coff+2)
    optsz, = struct.unpack_from("<H", d, coff+16)
    opt = coff+20
    magic, = struct.unpack_from("<H", d, opt)
    dd = opt + (96 if magic==0x10b else 112)
    edir_rva, edir_sz = struct.unpack_from("<II", d, dd)
    if not edir_rva: return []
    secs = []
    for i in range(nsec):
        s = opt+optsz+i*40
        nm = d[s:s+8].rstrip(b"\0").decode("latin1")
        va, vsz, raw, rsz = struct.unpack_from("<IIII", d, s+12)
        secs.append((va, vsz, raw, rsz))
    def r2o(rva):
        for va,vsz,raw,rsz in secs:
            if va <= rva < va+vsz: return raw + (rva-va)
        return None
    o = r2o(edir_rva)
    if o is None: return []
    nfun, nnam = struct.unpack_from("<II", d, o+20)
    namerv = struct.unpack_from("<I", d, o+32)[0]
    on = r2o(namerv)
    out = []
    for i in range(min(nnam, 40)):
        nr = struct.unpack_from("<I", d, on+i*4)[0]
        no = r2o(nr)
        s = d[no:d.index(b"\0", no)].decode("latin1")
        out.append(s)
    return out
for f in ("d3d9.dll","dxgi.dll","binkw32.dll","DFEngine.dll","discord_game_sdk.dll","SDL3.dll"):
    p = os.path.join(G,f)
    if not os.path.exists(p): continue
    ex = exports(p)
    print("=== %s (%d 字节) ===" % (f, os.path.getsize(p)))
    if ex is None: print("  非 PE 或解析失败")
    elif not ex: print("  无导出")
    else:
        print("  导出 %d+ 个，前 12: %s" % (len(ex), ", ".join(ex[:12])))
    print()
