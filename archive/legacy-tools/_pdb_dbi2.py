# -*- coding: utf-8 -*-
import sys, struct, pickle
sys.stdout.reconfigure(encoding="utf-8")
d=open(r"G:\SteamLibrary\steamapps\common\Saints Row 2\DFEngine.pdb","rb").read()
info=pickle.load(open(r"F:\sr2-cn\_pdb_dir.pkl","rb"))
BS=info["BS"]; sizes=info["sizes"]; blocks=info["blocks"]
def st(i): return b"".join(d[b*BS:(b+1)*BS] for b in blocks[i])[:sizes[i]]
s3=st(3)

modInfoSize=struct.unpack("<i",s3[24:28])[0]
secConSize=struct.unpack("<i",s3[28:32])[0]
secMapSize=struct.unpack("<i",s3[32:36])[0]
print("modInfoSize",modInfoSize,"secConSize",secConSize,"secMapSize",secMapSize)

# ---- section map @ 56 (after hdr; skip modInfo) ---- 实际: DBG header 56 字节, 然后 modInfo, 然后 secCon
base=56
secCon=s3[base+modInfoSize: base+modInfoSize+secConSize]
print("secCon len",len(secCon),"head",secCon[:40].hex(' '))
segsize={}
o=0
while o+28<=len(secCon):
    seg,pad,ofs,size,chars,mod,pad2,crc1,crc2=struct.unpack("<HHiiIHHII",secCon[o:o+28])
    if seg==0 and ofs==0: break
    segsize.setdefault(seg,[0,1<<30])
    segsize[seg][0]=max(segsize[seg][0],ofs+size)
    segsize[seg][1]=min(segsize[seg][1],ofs)
    o+=28
print("\nsegments (seg: maxEnd, minStart):")
for k in sorted(segsize)[:12]:
    print(f"  seg{k}: end={segsize[k][0]:#x} start={segsize[k][1]:#x}")

# PE sections for DLL
import pefile
pe=pefile.PE(r"G:\SteamLibrary\steamapps\common\Saints Row 2\DFEngine.dll", fast_load=True)
print("\nPE sections:")
secs=[]
for i,s in enumerate(pe.sections,1):
    nm=s.Name.rstrip(b"\x00").decode()
    print(f"  seg{i} {nm} RVA={s.VirtualAddress:#x} VS={s.Misc_VirtualSize:#x}")
    secs.append((i,s.VirtualAddress,s.Misc_VirtualSize))
pickle.dump(secs, open(r"F:\sr2-cn\_dfeng_pe_secs.pkl","wb"))

# 解析符号 -> RVA
syms=pickle.load(open(r"F:\sr2-cn\_dfeng_syms.pkl","rb"))
def rva(seg,ofs):
    for i,va,vs in secs:
        if i==seg: return va+ofs
    return None
print("\n关键符号 RVA:")
for t,seg,ofs,nm in syms:
    if nm.startswith("??"): continue
    for k in ["loadcharlist@MStrings","get_localization_from_hash@MStrings","StartParsing@MStrings",
              "increase_localization_buffer@MStrings","loadcharlistD@MStrings","get_localization_from_hashD@MStrings",
              "Utf8ToWide@MStrings"]:
        if k in nm:
            r=rva(seg,ofs)
            print(f"  RVA={hex(r) if r else '?'} seg{seg}+{ofs:#x} {nm}")
            break
