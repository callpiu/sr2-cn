import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
W = r"F:\sr2-cn"
for tag, p in (("第三方原始", os.path.join(W,"_juice_fix","patch.vpp_pc")),
               ("原厂繁中",   os.path.join(W,"pristine","patch.vpp_pc"))):
    v = Vpp(p)
    d = bytes(v.read(v.find("fnt_chinese","g_peg_pc")))
    print("=== %s  g_peg_pc %d 字节 ===" % (tag, len(d)))
    print("  前 64 字节: %s" % d[:64].hex(' '))
    # PEG 描述符
    print("  0x00 u32 = 0x%08X  0x04 u16 = 0x%04X  0x06 u16 = 0x%04X" % (
        struct.unpack_from("<I",d,0)[0], struct.unpack_from("<H",d,4)[0], struct.unpack_from("<H",d,6)[0]))
    for off in (0x08,0x0C,0x10,0x14,0x18,0x1C,0x20,0x24,0x28,0x2C,0x30,0x34):
        print("  0x%02X = %d" % (off, struct.unpack_from("<i",d,off)[0]))
    print()
    # 主数据（跳过头部，简单试偏移 0 与常见偏移）
    for skip in (0, 0x40, 0x80, 0x100):
        if len(d) - skip != 4194304: continue
        A = np.frombuffer(d[skip:], np.uint8).reshape(2048,2048)
        Image.fromarray(A).save(os.path.join(W,"_juice_fix","raw_%s_%d.png" % (tag.replace(" ",""), skip)))
        print("  按 2048x2048 灰度导出 raw_%s_%d.png (非零 %.1f%%)" % (tag.replace(" ",""), skip, 100*(A>0).mean()))
    print()
