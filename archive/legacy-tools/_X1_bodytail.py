# -*- coding: utf-8 -*-
import sys, struct, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
cv = Vpp(G + r"\common.vpp_pc")
e = cv.find("fnt_body_n", "vf3_pc")
d = cv.read(e)
N = struct.unpack_from('<I', d, 8)[0]
hv = 0xBC
rec_end = hv + N*16
uv_start = rec_end
uv_end = uv_start + N*8
print("size=%d N=%d rec_end=0x%X uv_end=0x%X(%d) tail=%d bytes" %
      (len(d), N, rec_end, uv_end, uv_end, len(d)-uv_end))
tail = d[uv_end:]
print("tail head 64:", tail[:64].hex(' '))
print("tail is all 0xCD:", set(tail) == {0xCD}, " nonzero bytes:", sum(1 for b in tail if b != 0xCD))
# interpret tail as u32 sequence
vals = struct.unpack_from('<%dI' % (len(tail)//4), tail, 0)
print("tail u32 first 40:", vals[:40])
# compare against fnt_chinese U/V array slices
pv = Vpp(G + r"\patch.vpp_pc")
vf = pv.read(pv.find("fnt_chinese", "vf3_pc"))
NC = struct.unpack_from('<I', vf, 8)[0]
UC = struct.unpack_from('<%dI' % NC, vf, 0xBC + NC*16)
VC = struct.unpack_from('<%dI' % NC, vf, 0xBC + NC*16 + NC*4)
# does tail contain 403,336 style values?
print("chinese U[403]=%d V[403]=%d ; U[336]=%d V[336]=%d" % (UC[403], VC[403], UC[336], VC[336]))
# search tail for the U/V pair (342,156) of 任
pat = struct.pack('<II', 342, 156)
print("任 UV (342,156) in tail:", tail.find(pat))
pat2 = struct.pack('<II', UC[403], VC[403])
print("值 UV in tail:", tail.find(pat2))
