# -*- coding: utf-8 -*-
"""完整 PDB 符号→RVA 解析：DBI section headers (segment->RVA) + symStream S_PUB32/S_GPROC32"""
import sys, struct, pickle
sys.stdout.reconfigure(encoding="utf-8")
P = r"G:\SteamLibrary\steamapps\common\Saints Row 2\DFEngine.pdb"
d = open(P, "rb").read()
info = pickle.load(open(r"F:\sr2-cn\_pdb_dir.pkl", "rb"))
BS = info["BS"]; sizes = info["sizes"]; blocks = info["blocks"]
def stream(i):
    return b"".join(d[b*BS:(b+1)*BS] for b in blocks[i])[:sizes[i]]

s3 = stream(3)
u32=lambda o: struct.unpack("<I", s3[o:o+4])[0]
u16=lambda o: struct.unpack("<H", s3[o:o+2])[0]
symStream = u16(20)
print("symStream", symStream)

sym = stream(symStream)
# 解析所有记录
recs=[]
off=0; n=len(sym)
while off+4<=n:
    rl=struct.unpack("<H",sym[off:off+2])[0]
    if rl<2 or off+rl>n: break
    rt=struct.unpack("<H",sym[off+2:off+4])[0]
    recs.append((off,rl,rt,sym[off+4:off+rl]))
    off+=rl
    if rl%4: off+=4-(rl%4)
print("recs",len(recs))

# ---- 全局符号偏移表 (GSI) 可给出段信息, 但 S_GPROC32 里带 segment ----
# S_GPROC32 = 0x1108: payload: u32 parent,u32 end,u32 next,u32 len(u32?),u32 dbgstart, u32 dbgend, u32 typeidx, u32 off, u16 seg, u8 flags, name
# 实际 MS PDB: parent(u32) end(u32) next(u32) len(u32) dbgStart(u32) dbgEnd(u32) typeIndex(u32) offset(u32) segment(u16) flags(u8) name
targets={0x1108:"GPROC32",0x110A:"LPROC32",0x110E:"PUB32",0x1147:"PROCREF"}
hits=[]
for o,rl,rt,pl in recs:
    if rt in targets:
        try:
            if rt in (0x1108,0x110A):
                # 24 bytes header before name
                seg=struct.unpack("<H",pl[28:30])[0]
                ofs=struct.unpack("<I",pl[24:28])[0]
                nm=pl[30:].split(b"\x00")[0]
                hits.append((targets[rt],seg,ofs,nm))
            elif rt==0x110E:  # S_PUB32: flags u32, off u32, seg u16, name
                ofs=struct.unpack("<I",pl[4:8])[0]
                seg=struct.unpack("<H",pl[8:10])[0]
                nm=pl[10:].split(b"\x00")[0]
                hits.append(("PUB32",seg,ofs,nm))
        except Exception:
            pass
print("hits",len(hits))
KEY=[b"MStrings",b"loadcharlist",b"get_localization",b"increase_localization"]
for t,seg,ofs,nm in hits:
    for k in KEY:
        if k in nm:
            print(f"  {t} seg={seg} off={ofs:#x} {nm.decode('ascii','replace')}")
            break
out=[(t,seg,ofs,nm.decode('ascii','replace')) for t,seg,ofs,nm in hits]
pickle.dump(out, open(r"F:\sr2-cn\_dfeng_syms.pkl","wb"))
print("saved _dfeng_syms.pkl", len(out))
