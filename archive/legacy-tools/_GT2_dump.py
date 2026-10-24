import os
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
d = open(os.path.join(G, "SR2_pc.exe"), "rb").read()
s = 0x9e0f80; e = 0x9e10e0
for off in range(s, e, 16):
    chunk = d[off:off+16]
    hexs = " ".join(f"{b:02x}" for b in chunk)
    asc  = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    print(f"{off:08x}  {hexs:<47s}  |{asc}|")
