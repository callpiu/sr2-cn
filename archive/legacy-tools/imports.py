import os, struct
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
def imports(path):
    d = open(path,"rb").read()
    e = struct.unpack_from("<I", d, 0x3C)[0]
    coff = e+4
    nsec, = struct.unpack_from("<H", d, coff+2)
    optsz, = struct.unpack_from("<H", d, coff+16)
    opt = coff+20
    magic, = struct.unpack_from("<H", d, opt)
    dd = opt + (96 if magic==0x10b else 112)
    imp_rva, imp_sz = struct.unpack_from("<II", d, dd+8)
    secs=[]
    for i in range(nsec):
        s = opt+optsz+i*40
        nm = d[s:s+8].rstrip(b"\0").decode("latin1")
        va,vsz,raw,rsz = struct.unpack_from("<IIII", d, s+12)
        secs.append((nm,va,vsz,raw,rsz))
    def r2o(rva):
        for nm,va,vsz,raw,rsz in secs:
            if va <= rva < va+vsz: return raw+(rva-va)
        return None
    out=[]
    o = r2o(imp_rva)
    while o:
        ol, td, fc, nrva, frva = struct.unpack_from("<IIIII", d, o)
        if nrva == 0: break
        no = r2o(nrva)
        s = d[no:d.index(b"\0", no)].decode("latin1")
        out.append(s)
        o += 20
    return out, secs
for f in ("SR2_pc.exe","sr2_pc_unpatched.exe","SR2_pc.exe.bak"):
    p = os.path.join(G,f)
    if not os.path.exists(p): continue
    imp, secs = imports(p)
    print("=== %s (%d 字节) ===" % (f, os.path.getsize(p)))
    print("  导入 DLL %d 个: %s" % (len(imp), ", ".join(imp)))
    print()
