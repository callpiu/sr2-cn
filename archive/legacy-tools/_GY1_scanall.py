# -*- coding: utf-8 -*-
"""只读：索引级扫描全部 vpp_pc，列出所有字体相关条目（不载入大文件）。"""
import os, struct, glob
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
MAGIC = bytes([0xCE,0x0A,0x89,0x51,0x04])

def index_only(path):
    with open(path,'rb') as f:
        head = f.read(0x800)
        if head[:5] != MAGIC: return None
        o = 5 + 0x14F
        num, csize, lo, lf, le = struct.unpack_from('<iiiii', head, o)
        names_at = ((0x800 + lo) & 0xFFFFF800) + 0x800
        ext_at   = ((names_at + lf) & 0xFFFFF800) + 0x800
        need = max(names_at + lf, ext_at + le, 0x800 + num*28)
        f.seek(0); buf = f.read(need)
        def s(base, pos):
            if not pos: return ''
            e = buf.find(b'\x00', base+pos)
            return buf[base+pos:e].decode('ascii','replace')
        out = []
        for i in range(num):
            e = 0x800 + i*28
            a,b,c,d,ln,m1,z = struct.unpack_from('<IIiiiii', buf, e)
            out.append((s(names_at,a), s(ext_at,b), ln))
        return out

PAT = ('fnt_','jap','korea','ige_','ug-debug','font_','charlist','.vf3','g_peg')
for p in sorted(glob.glob(os.path.join(G,'*.vpp_pc'))):
    ents = index_only(p)
    if ents is None:
        print(f"!! {os.path.basename(p)} 不是 VPP"); continue
    hits = [e for e in ents if any(t in (e[0]+'.'+e[1]).lower() for t in PAT)]
    if hits:
        print(f"### {os.path.basename(p)}  ({len(ents)} 项, {os.path.getsize(p):,} B)")
        for n,x,ln in sorted(hits):
            print(f"    {n}.{x}" if x else f"    {n}", "=", ln)
print("SCAN DONE")
