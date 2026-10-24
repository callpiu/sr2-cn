"""全目录字节级扫描：找 ascii "twins"/"twin"，以及 双胞胎 的 UTF-8/UTF-16LE 字节序列。
双 = U+53CC, 胞 = U+80CE, 胎 = U+80CE
UTF-8:  e58f8c e8839e e8838f
UTF16LE:53cc 80ce 80ce
"""
import os, glob, sys

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
patterns = {
    b'twins': b'twins',
    b'twin': b'twin',
    '双胞胎_utf8': bytes.fromhex('e58f8ce8839ee8838f'),
    '双胞胎_utf16le': bytes.fromhex('53cc80ce80ce'),
}
# 也加 双胞/胞胎 两字组合，容错
extra = {
    '双胞_utf8': bytes.fromhex('e58f8ce8839e'),
    '胞胎_utf8': bytes.fromhex('e8839ee8838f'),
    '双胞_utf16le': bytes.fromhex('53cc80ce'),
    '胞胎_utf16le': bytes.fromhex('80ce80ce'),
}
patterns.update(extra)

CHUNK = 8*1024*1024
OVERLAP = 32
found_any = False
for root, dirs, files in os.walk(GAME):
    # 跳过明显无关/超大目录
    for fn in files:
        fp = os.path.join(root, fn)
        try:
            size = os.path.getsize(fp)
        except OSError:
            continue
        # 只扫可能含文本的文件（含 vpp/le_strings/cxt/xml/xtbl/txt/lut 等）
        low = fn.lower()
        interesting = low.endswith(('.vpp_pc','.le_strings','.cxt','.xml','.xtbl','.txt','.csv','.lut','.dat','.str','.bin','.ini'))
        if not interesting:
            continue
        try:
            with open(fp,'rb') as f:
                prev = b''
                pos = 0
                while True:
                    chunk = f.read(CHUNK)
                    if not chunk:
                        break
                    buf = prev + chunk
                    for pname, pat in patterns.items():
                        idx = 0
                        while True:
                            j = buf.find(pat, idx)
                            if j < 0:
                                break
                            abspos = pos - len(prev) + j
                            print("[%s] %s @0x%X  file=%s" % (pname, pname, abspos, fp))
                            found_any = True
                            idx = j+1
                    pos += len(chunk)
                    prev = buf[-OVERLAP:] if len(buf)>=OVERLAP else buf
        except OSError as e:
            pass
if not found_any:
    print("全目录未命中任何 twins / 双胞胎 字节序列")
