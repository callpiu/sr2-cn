# -*- coding: utf-8 -*-
"""修正的 DBI 解析：正确 DBI header + section contributions"""
import sys, struct, pickle
sys.stdout.reconfigure(encoding="utf-8")
P=r"G:\SteamLibrary\steamapps\common\Saints Row 2\DFEngine.pdb"
d=open(P,"rb").read()
info=pickle.load(open(r"F:\sr2-cn\_pdb_dir.pkl","rb"))
BS=info["BS"]; sizes=info["sizes"]; blocks=info["blocks"]
def stream(i): return b"".join(d[b*BS:(b+1)*BS] for b in blocks[i])[:sizes[i]]

s3=stream(3)
sig,ver,age = struct.unpack("<III", s3[:12])
gs, build, pubStrm, pdbver, symStrm, rbld = struct.unpack("<HHHHHH", s3[12:24])
modInfoSize, secConSize, secMapSize, srcInfoSize, tsmSize, mfcIdx, optHdrSize, ecSize = struct.unpack("<iiiiIiiI", s3[24:48])
flags, machine, reserved = struct.unpack("<HHI", s3[48:56])
print(f"sig={sig:#x} ver={ver} age={age}")
print(f"symStrm={symStrm} pubStrm={pubStrm} machine={machine:#x}")
print(f"modInfoSize={modInfoSize} secConSize={secConSize} secMapSize={secMapSize} optHdrSize={optHdrSize}")

# ---- Section Contributions (secCon) : 给出每个 (segment, offset, size) 属于哪个 section ----
o3 = 56
SECCON = s3[o3: o3+secConSize]
print("secCon bytes", len(SECCON))
# 记录: u16 seg, u16 pad, i32 offset, i32 size, u32 characteristics, u16 module, u16 pad, u32 dataCrc, u32 relocCrc  (共 28 字节)
segsize={}
o=0
while o+28<=len(SECCON):
    seg,pad,ofs,size,chars,mod,pad2,crc1,crc2 = struct.unpack("<HHiiIHHII", SECCON[o:o+28])
    if seg==0: break
    segsize[seg]=max(segsize.get(seg,0), ofs+size)
    o+=28
print("segments found:", sorted(segsize.items())[:8], "...")

# ---- Section map ----
o3m = o3+secConSize
SECMAP=s3[o3m:o3m+secMapSize]
# u16 count, then entries: u16 flags; name follows null-terminated... 简化: 直接打印
print("secMap head:", SECMAP[:80])

# 段 -> RVA 映射由 PE 提供; 这里只拿到 seg 的 VA. 用典型 PE: 段1代码基址=0x1000
# 用贡献表: 段号->该段的虚拟地址 (取最小offset对应RVA). 无PE表则用可选调试头.
# 可选调试头 (optHdr) 里有 IMAGE_DEBUG_TYPE_MISC 等; 我们改从 secCon 的最大 size 推断.
pickle.dump(segsize, open(r"F:\sr2-cn\_dfeng_segsize.pkl","wb"))

# ---- 用 PE 的 section 基址: 需要 RVA. DBI 段号 == PE 段序号 ----
import pefile
pe=pefile.PE(r"G:\SteamLibrary\steamapps\common\Saints Row 2\DFEngine.dll", fast_load=True)
print("\nPE sections:")
for i,s in enumerate(pe.sections, start=1):
    print(f"  seg{i} {s.Name.decode().rstrip(chr(0))} VA={s.VirtualAddress:#x} VS={s.Misc_VirtualSize:#x}")
pickle.dump([(i,s.VirtualAddress,s.Misc_VirtualSize) for i,s in enumerate(pe.sections,1)],
            open(r"F:\sr2-cn\_dfeng_pe_secs.pkl","wb"))
