import os, sys
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G, "common.vpp_pc"))
ents = { (e['name'] + ('.' + e['ext'] if e['ext'] else '')).lower(): e for e in v.entries() }
for nm in ["fnt_body_n.vf3_pc","fnt_body_s.vf3_pc","fnt_head_n.vf3_pc",
           "fnt_bodyital_n.vf3_pc","fnt_chinese.vf3_pc","jap.vf3_pc","fnt_cz.vf3_pc","ug-debug.vf3_pc"]:
    e = ents.get(nm)
    if not e: print(nm, "MISSING"); continue
    b = v.read(e)
    print(f"--- {nm}  size={len(b)}")
    print("   head64:", " ".join(f"{x:02x}" for x in b[:64]))
    # 找可打印串
    import re
    ss = re.findall(rb"[\x20-\x7e]{4,}", b[:400])
    print("   strs :", [s.decode() for s in ss][:8])
print()
print("=== pegs 描述符文本 ===")
p = Vpp(os.path.join(G, "pegs.vpp_pc"))
pe = { (e['name'] + ('.' + e['ext'] if e['ext'] else '')).lower(): e for e in p.entries() }
for nm in ["fnt_body_n","fnt_body_s","fnt_head_n","fnt_chinese","jap"]:
    e = pe.get(nm)
    if not e: print(nm, "MISSING"); continue
    b = p.read(e)
    print(f"--- {nm} size={len(b)}")
    print("   ", b.decode('latin-1').replace("\x00"," ").strip())
    print("   head:", " ".join(f"{x:02x}" for x in b[:40]))
