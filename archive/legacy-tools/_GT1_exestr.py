import os, re
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
exe = os.path.join(G, "SR2_pc.exe")
d = open(exe, "rb").read()
print("exe size =", len(d))
needles = [b"thin_overlay", b"thin\x00", b"fnt_body_n", b"fnt_body_s", b"fnt_head_n",
           b"fnt_head_s", b"fnt_bodyital_n", b"fnt_bodyital_s", b"font_hudsmall",
           b"fnt_chinese", b"header_n", b"bodyital_overlay", b"debug\x00",
           b"charlist", b"jap", b"font_hudsmall"]
for n in needles:
    offs = [m.start() for m in re.finditer(re.escape(n), d)]
    print(f"{n!r:26s} count={len(offs)}  offs={[hex(o) for o in offs[:12]]}")
