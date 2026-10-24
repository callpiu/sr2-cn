import os, struct, re
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
d = open(os.path.join(G, "SR2_pc.exe"), "rb").read()
IB = 0x400000
strs = {
 "jap":0x9e0fcc, "fnt_chinese":0x9e0fd0, "fnt_korea":0x9e0fdc, "fnt_cz":0x9e0fe8,
 "fnt_cz_s":0x9e0ff0, "fnt_body_n":0x9e0ffc, "fnt_body_s":0x9e1008,
 "fnt_bodyital_n":0x9e1014, "fnt_bodyital_s":0x9e1024, "fnt_head_n":0x9e1034,
 "fnt_head_s":0x9e1040, "ug-debug":0x9e104c, "debug":0x9e1058, "thin":0x9e1060,
 "thin_overlay":0x9e1068, "header_n":0x9e1078, "header_n_overlay":0x9e1084,
 "bodyital_overlay":0x9e1098,
}
for nm, rva in strs.items():
    pats = {"RVA": struct.pack("<I", rva), "VA": struct.pack("<I", rva + IB)}
    out = []
    for tag, p in pats.items():
        offs = [m.start() for m in re.finditer(re.escape(p), d)]
        if offs:
            out.append(f"{tag}:{len(offs)}@{[hex(o) for o in offs[:6]]}")
    print(f"{nm:18s} rva={rva:#x}  " + ("  ".join(out) if out else "NO-PTR"))
