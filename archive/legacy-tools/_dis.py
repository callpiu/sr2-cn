# -*- coding: utf-8 -*-
"""SR2_pc.exe 反汇编助手"""
import struct
import capstone

class PE:
    def __init__(self, path):
        self.path = path
        self.d = open(path, 'rb').read()
        d = self.d
        e_lfanew = struct.unpack_from('<I', d, 0x3C)[0]
        assert d[e_lfanew:e_lfanew+4] == b'PE\x00\x00'
        coff = e_lfanew + 4
        self.nsec, = struct.unpack_from('<H', d, coff + 2)
        self.opt_size, = struct.unpack_from('<H', d, coff + 16)
        opt = coff + 20
        self.magic, = struct.unpack_from('<H', d, opt)
        self.image_base, = struct.unpack_from('<I', d, opt + 28)
        self.sections = []
        so = opt + self.opt_size
        for i in range(self.nsec):
            o = so + i * 40
            name = d[o:o+8].rstrip(b'\x00').decode('latin1')
            vsize, va, rsize, rptr = struct.unpack_from('<IIII', d, o + 8)
            self.sections.append(dict(name=name, va=va, vsize=vsize, ptr=rptr, size=rsize))
        self.mode = capstone.CS_MODE_32 if self.magic == 0x10b else capstone.CS_MODE_64
        self.md = capstone.Cs(capstone.CS_ARCH_X86, self.mode)
        self.md.detail = True

    def va2off(self, va):
        r = va - self.image_base
        for s in self.sections:
            if s['va'] <= r < s['va'] + max(s['vsize'], s['size']):
                return s['ptr'] + (r - s['va'])
        return None

    def off2va(self, off):
        for s in self.sections:
            if s['ptr'] <= off < s['ptr'] + s['size']:
                return self.image_base + s['va'] + (off - s['ptr'])
        return None

    def dis(self, va, n=200, stop_at_ret=True):
        off = self.va2off(va)
        if off is None:
            return []
        code = self.d[off:off + n * 8]
        out = []
        for ins in self.md.disasm(code, va):
            out.append((ins.address, ins.mnemonic, ins.op_str, ins))
            if len(out) >= n:
                break
            if stop_at_ret and ins.mnemonic in ('ret', 'retn'):
                break
        return out

    def find_imm_refs(self, target_va):
        """在 .text 中找引用该 VA 的指令 (直接 imm32)"""
        b = struct.pack('<I', target_va)
        res = []
        for s in self.sections:
            if s['name'] != '.text':
                continue
            base = s['ptr']
            seg = self.d[base:base + s['size']]
            i = 0
            while True:
                j = seg.find(b, i)
                if j < 0:
                    break
                res.append(self.image_base + s['va'] + j)
                i = j + 1
        return res


if __name__ == '__main__':
    import sys
    pe = PE(r"G:\SteamLibrary\steamapps\common\Saints Row 2\SR2_pc.exe")
    print("image base", hex(pe.image_base), "magic", hex(pe.magic))
    for s in pe.sections:
        print("  %-8s va=%08X vsize=%X ptr=%X size=%X" % (s['name'], s['va'], s['vsize'], s['ptr'], s['size']))
    print("\nVA of charlist_%s.txt (file 0xA26070) =", hex(pe.off2va(0xA26070) or 0))
    print("VA of fnt_chinese (file 0x9E0FD0) =", hex(pe.off2va(0x9E0FD0) or 0))
