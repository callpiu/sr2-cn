import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
def get(p):
    v=Vpp(p); return v.read(v.find("static_CH","le_strings"))
a=get(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig")
b=get(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")

def parse(x, tag):
    n = struct.unpack_from('<I', x, 8)[0]
    dirstart = 12
    dirend = dirstart + n*8
    print("=== %s: n=%d dirend=%d filesize=%d  剩余=%d" % (tag, n, dirend, len(x), len(x)-dirend))
    # 目录
    ents = [struct.unpack_from('<II', x, dirstart+i*8) for i in range(n)]
    tot = sum(l for l,_ in ents)
    print("   目录长度总和=%d  (含结束符?)" % tot)
    # 找文本起点：从 dirend 起找第一个能让 UTF-16LE 解出合理 ASCII 的对齐
    for off in (dirend, dirend+1):
        seg = x[off:off+200].decode('utf-16-le','replace')
        print("   off=%d: %r" % (off, seg[:50]))
    return ents, dirend

ea, da = parse(a, "原始")
eb, db = parse(b, "当前")

def strings(x, ents, dirend, off):
    # 按目录顺序切分，每串长 = len*2 字节 (UTF-16LE, 含结束符)
    p = off; out=[]
    for l,hid in ents:
        seg = x[p:p+l*2]
        out.append((hid, seg.decode('utf-16-le','replace')))
        p += l*2
    return out, p

sa, enda = strings(a, ea, da, da+1)
sb, endb = strings(b, eb, db, db+1)
print("\n原始解析消耗到 %d / %d" % (enda, len(a)))
print("当前解析消耗到 %d / %d" % (endb, len(b)))
print("\n--- 前 12 条对照 ---")
for i in range(12):
    print("  id=0x%04X\n     原始: %r\n     当前: %r" % (sa[i][0], sa[i][1], sb[i][1]))
