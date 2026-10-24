# -*- coding: utf-8 -*-
"""反汇编 DFEngine 的 ParseCxtFile / StartParsing 的后半段（文件路径拼接）。
先把 PDB 里所有 MStrings / Render2D / General 相关 PUB32 的 RVA 打印出来备用。
"""
import sys, struct, pickle
sys.stdout.reconfigure(encoding="utf-8")
import capstone, pefile

P = r"G:\SteamLibrary\steamapps\common\Saints Row 2\DFEngine.dll"
data = open(P, "rb").read()
pe = pefile.PE(P)
RT = 0x5C640000


def bytes_rva(rva, n):
    o = pe.get_offset_from_rva(rva)
    return data[o:o + n]


def dis(rva, n, label, stop_ret_after=30):
    v = RT + rva
    code = bytes_rva(rva, n)
    print("\n" + "=" * 72)
    print("--- %s  RVA=0x%X VA=0x%08X ---" % (label, rva, v))
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    for ins in md.disasm(code, v):
        print("  %08X: %-22s %s %s" % (ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str))
        if ins.mnemonic in ("ret", "jmp") and ins.address > v + stop_ret_after:
            break


# 解析 PUB32 全表，拿 MStrings 全部符号 RVA
info = pickle.load(open(r"F:\sr2-cn\_pdb_dir.pkl", "rb"))
BS = info["BS"]; sizes = info["sizes"]; blocks = info["blocks"]
d2 = open(r"G:\SteamLibrary\steamapps\common\Saints Row 2\DFEngine.pdb", "rb").read()


def stream(i):
    return b"".join(d2[b * BS:(b + 1) * BS] for b in blocks[i])[:sizes[i]]


sym = stream(525); n = len(sym)
off = 0
syms = {}
while off + 4 <= n:
    rlen = struct.unpack("<H", sym[off:off + 2])[0]
    if rlen < 2 or off + rlen > n:
        break
    rtype = struct.unpack("<H", sym[off + 2:off + 4])[0]
    payload = sym[off + 4:off + rlen]
    if rtype == 0x110E and len(payload) > 14:
        so, seg = struct.unpack("<IH", payload[4:10])
        nm = payload[10:].split(b"\x00")[0].decode("latin1")
        rva = so + 0x1000
        syms[nm] = rva
    off += rlen
    if rlen % 4:
        off += 4 - (rlen % 4)

print("=== MStrings 符号 RVA ===")
for nm, rva in sorted(syms.items(), key=lambda x: x[1]):
    if "MStrings" in nm:
        print("  RVA=0x%07X  %s" % (rva, nm))
pickle.dump(syms, open(r"F:\sr2-cn\_df_syms.pkl", "wb"))
print("\n总计符号 %d" % len(syms))
