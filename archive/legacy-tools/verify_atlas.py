# -*- coding: utf-8 -*-
"""亲自看图核验 common 图集码点表：
A. 争议位置 1158 / 2264（JSON=634D/88E1 vs 早前渲染=633D/91CC）
B. JSON 中 9 个乱码输出的位置 vs patch 对应字形
C. 7 个一致锚点复核
"""
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
from PIL import Image, ImageDraw
import sr2lib as S

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def load_cl():
    vp = S.Vpp(os.path.join(G, "patch.vpp_pc"))
    clbuf = vp.read(vp.find("charlist_CH", "txt"))
    import re
    return [int(x) for x in re.findall(rb'\d+', clbuf)]
CL = load_cl()
print("charlist_CH(patch.vpp_pc) = %d 项, CL[332]=0x%04X CL[371]=0x%04X" % (len(CL), CL[332], CL[371]))
CP2I = {cp: i for i, cp in enumerate(CL)}

class VppLite:
    def __init__(self, path):
        self.path = path
        with open(path, 'rb') as f:
            head = f.read(5 + 0x14F + 20)
            o = 5 + 0x14F
            (self.num, self.cs, self.lo, self.lf, self.le) = struct.unpack_from('<iiiii', head, o)
            self.names_at = ((0x800 + self.lo) & 0xFFFFF800) + 0x800
            self.ext_at = ((self.names_at + self.lf) & 0xFFFFF800) + 0x800
            self.data_start = ((self.ext_at + self.le) & 0xFFFFF800) + 0x800
            f.seek(0x800); et = f.read(self.num * 28)
            f.seek(self.names_at); names = f.read(self.lf)
            f.seek(self.ext_at); exts = f.read(self.le)
        self.ents = []
        for i in range(self.num):
            a, b, c, d, ln, m1, z = struct.unpack_from('<IIiiiii', et, i * 28)
            nm = names[a:names.find(b'\x00', a)].decode('ascii','replace') if a < len(names) else ''
            ex = exts[b:exts.find(b'\x00', b)].decode('ascii','replace') if b else ''
            self.ents.append(dict(idx=i, name=nm, ext=ex, body=d, size=ln))
    def find(self, name, ext=None):
        for e in self.ents:
            if e['name'].lower() == name.lower() and (ext is None or e['ext'].lower() == ext.lower()):
                return e
    def read(self, ent):
        with open(self.path, 'rb') as f:
            f.seek(self.data_start + ent['body']); return f.read(ent['size'])

def load_vf3(path_vpp, name="fnt_chinese", ext="vf3_pc"):
    v = S.Vpp(os.path.join(G, path_vpp))
    buf = bytes(v.read(v.find(name, ext)))
    N = struct.unpack_from("<I", buf, 8)[0]
    U = list(struct.unpack_from("<%dI" % N, buf, 0xBC + 16 * N))
    V = list(struct.unpack_from("<%dI" % N, buf, 0xBC + 16 * N + 4 * N))
    return N, U, V

pN, pU, pV = load_vf3("patch.vpp_pc")
cN, cU, cV = load_vf3("common.vpp_pc")
print("patch vf3 N=%d   common vf3 N=%d" % (pN, cN))

def dxt3_fast(data, w=2048, h=2048):
    bw, bh = w // 4, h // 4
    blk = np.frombuffer(data, np.uint8)[:bw * bh * 16].reshape(bh, bw, 16)
    c0 = blk[:,:,8].astype(np.uint32) | (blk[:,:,9].astype(np.uint32) << 8)
    c1 = blk[:,:,10].astype(np.uint32) | (blk[:,:,11].astype(np.uint32) << 8)
    def e565(v):
        r = ((v>>11)&0x1F).astype(np.float64)*255.0/31
        g = ((v>>5)&0x3F).astype(np.float64)*255.0/63
        b = (v&0x1F).astype(np.float64)*255.0/31
        return np.stack([r,g,b],-1)
    P0,P1 = e565(c0), e565(c1)
    m4 = (c0>c1)[...,None]
    P2 = np.where(m4,(2*P0+P1)/3,(P0+P1)/2)
    P3 = np.where(m4,(P0+2*P1)/3,0.0)
    pal = np.stack([P0,P1,P2,P3],-2)
    word = np.ascontiguousarray(blk[:,:,12:16]).view(np.uint32)[:,:,0]
    pix = ((word[:,:,None] >> (2*np.arange(16,dtype=np.uint32))) & 3)
    BI,BJ = np.arange(bh)[:,None,None], np.arange(bw)[None,:,None]
    rgb = pal[BI,BJ,pix].reshape(bh,bw,4,4,3).transpose(0,2,1,3,4).reshape(h,w,3)
    return rgb

vp = S.Vpp(os.path.join(G, "patch.vpp_pc"))
prgb = dxt3_fast(bytes(vp.read(vp.find("fnt_chinese","g_peg_pc"))))
vl = VppLite(os.path.join(G, "textures.vpp_pc"))
crgb = dxt3_fast(vl.read(vl.find("fnt_chinese")))
pink, cink = prgb.mean(2), crgb.mean(2)
print("图集解码完成")

def crop(img, U, V, i, cell):
    x, y = int(U[i]), int(V[i])
    g = img[y:y+cell, x:x+cell]
    nz = np.argwhere(g > 24)
    if len(nz)==0: return g
    y0,x0 = nz.min(0); y1,x1 = nz.max(0)
    return g[y0:y1+1, x0:x1+1]

def norm(g, size=48):
    im = Image.fromarray(np.clip(g,0,255).astype(np.uint8)).resize((size,size), Image.LANCZOS)
    return np.asarray(im, np.float64)/255.0

def cg(i): return norm(crop(cink, cU, cV, i, 30))
def pg(cp):
    j = CP2I.get(cp)
    return norm(crop(pink, pU, pV, j, 31)) if j is not None else None, j

GROUPS = [
 ("A 争议: common[1158]  JSON说U+634D / 早前渲染说U+633D(捍)",
   [("common[1158]", cg(1158), None)] + [("patch U+%04X %s" % (cp, chr(cp)),) + pg(cp) for cp in (0x633D, 0x634D)]),
 ("B 争议: common[2264]  JSON说U+88E1(裡) / 早前渲染说U+91CC(里)",
   [("common[2264]", cg(2264), None)] + [("patch U+%04X %s" % (cp, chr(cp)),) + pg(cp) for cp in (0x91CC, 0x88E1)]),
 ("C 乱码输出: common[JSON位置] vs patch[该码点]",
   [(("common[%d]" % p), cg(p), None) for p in (307, 325, 374, 1731, 2038, 2248, 2653)] +
   [("patch U+%04X %s" % (cp, chr(cp)),) + pg(cp) for cp in (0x4EFB, 0x4F4D, 0x5076, 0x74A8, 0x8BE5, 0x8861, 0x96C4)]),
 ("D 锚点复核: common[idx] vs patch[码点]",
   [(("common[%d]" % i), cg(i), None) for i in (332, 359, 371, 390, 1003, 1804, 2635)] +
   [("patch U+%04X %s" % (cp, chr(cp)),) + pg(cp) for cp in (0x4F5C, 0x5012, 0x5065, 0x50CF, 0x5FD7, 0x76EF, 0x9664)]),
]

SZ = 48
items = []
for title, cells in GROUPS:
    items.append(("TITLE", title, None))
    for c in cells:
        items.append(("CELL", c[0], c[1]))
        if len(c) > 2 and c[2] is not None:
            items.append(("CELL", "   ^patch#%d" % c[2], None))

COLS = 8
rowsn = (len(items) + COLS - 1) // COLS
W = COLS * (SZ + 6) + 10
H = rowsn * (SZ + 20) + 10
canvas = Image.new("L", (W, H), 240)
dr = ImageDraw.Draw(canvas)
for k, (kind, label, g) in enumerate(items):
    r, c = divmod(k, COLS)
    x = 5 + c * (SZ + 6); y = 5 + r * (SZ + 20)
    if kind == "TITLE":
        dr.text((x, y + SZ//2), label[:60], fill=200)
        canvas.paste(Image.new("L", (SZ, SZ), 200), (x, y))
    else:
        if g is not None:
            canvas.paste(Image.fromarray((np.clip(g,0,1)*255).astype(np.uint8)), (x, y))
        else:
            canvas.paste(Image.new("L", (SZ, SZ), 210), (x, y))
        dr.text((x, y + SZ + 2), label[:16], fill=0)
canvas.save(r"F:/sr2-cn/_atlas_verify.png")
print("已保存 _atlas_verify.png  (%d 单元格)" % len(items))

# 辅助：L1 距离
print("\n=== L1 距离（common[idx] vs patch[cp]，越小越像）===")
def l1(a, b): return float(np.abs(a-b).mean()) if (a is not None and b is not None) else None
for title, cells in GROUPS[:2] + GROUPS[2:]:
    base = cells[0]
    for c in cells[1:]:
        if c[1] is None: continue
        d = l1(base[1], c[1])
        print("  %-46s vs %-22s L1=%.4f" % (base[0], c[0], d) if d is not None else "")
    print("  ---")
