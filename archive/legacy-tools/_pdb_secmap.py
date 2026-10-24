# -*- coding: utf-8 -*-
"""PDB DBI section headers -> segment:RVA map, 然后把关键符号转 RVA 并反汇编"""
import sys, struct, pickle
sys.stdout.reconfigure(encoding="utf-8")
P=r"G:\SteamLibrary\steamapps\common\Saints Row 2\DFEngine.pdb"
d=open(P,"rb").read()
info=pickle.load(open(r"F:\sr2-cn\_pdb_dir.pkl","rb"))
BS=info["BS"]; sizes=info["sizes"]; blocks=info["blocks"]
def stream(i): return b"".join(d[b*BS:(b+1)*BS] for b in blocks[i])[:sizes[i]]

s3=stream(3)
# DBI header: u32 sig, u32 ver, u32 hdrSize, u32 age, u16 gs, u16 ps, u16 sym, u16 old, u16 sec, ...
sig,ver,hdrSize,age=struct.unpack("<IIII",s3[:16])
gs,ps,symStrm,old,secStrm=struct.unpack("<HHHHH",s3[16:26])
print(f"sig={sig:#x} ver={ver} hdrSize={hdrSize} secStrm={secStrm} symStrm={symStrm}")

# section headers 在 DBI header 之后 (offset hdrSize)
off=hdrSize
nsec=struct.unpack("<H",s3[off+2:off+4])[0]
print("nsec",nsec)
segs={}
o=off+4
for i in range(nsec):
    # IMAGE_SECTION_HEADER-ish in DBI: name[8], virtSize u32, virtAddr u32, sizeRaw u32, ptrRaw u32, ...
    name=s3[o:o+8].rstrip(b"\x00").decode("ascii","replace")
    vsize,vaddr,rawsize,rawptr=struct.unpack("<IIII",s3[o+8:o+24])
    segs[i+1]=(name,vaddr,rawsize,rawptr)
    print(f"  seg{i+1} {name} VA={vaddr:#x} raw={rawptr:#x} sz={rawsize:#x}")
    o+=40

# 映射: segment -> RVA(=vaddr)
sym_recs=pickle.load(open(r"F:\sr2-cn\_dfeng_syms.pkl","rb"))
def rva(seg,ofs):
    if seg in segs:
        return segs[seg][1]+ofs
    return None

print("\n关键符号 -> RVA:")
KEYS=["loadcharlist@MStrings","get_localization_from_hash@MStrings","StartParsing@MStrings",
      "increase_localization_buffer@MStrings","loadcharlistD@MStrings","get_localization_from_hashD@MStrings",
      "Utf8ToWide","ParseCxtFile@MStrings"]
for t,seg,ofs,nm in sym_recs:
    for k in KEYS:
        if k in nm and not nm.startswith("??"):
            r=rva(seg,ofs)
            print(f"  seg{seg} off={ofs:#x} RVA={r if r is None else hex(r)}  {nm}")
            break
