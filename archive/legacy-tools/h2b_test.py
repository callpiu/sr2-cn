# -*- coding: utf-8 -*-
"""H2b 判定：HUD 是否把 (slot-0x20) 直接当 common 字形索引。

证据链：内存抓到真 UTF-16LE 串「任璨偶巧位」= slot 403/1868/1067/454/364 的转换结果。
若 common 字形数组第 371/1836/1035/422/332 项恰是 任/璨/偶/巧/位 的字形，
则「引擎用 common 字体、按 charlist 索引直接取字形」成立，与字体/图集无关，
修复 = 按 common 字形顺序重写这 2 条串的 slot。
"""
import sys, os, struct, re
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
from PIL import Image

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# ---------------------------------------------------------- charlist
import sr2lib as S
vp = S.Vpp(os.path.join(G, "patch.vpp_pc"))
clbuf = vp.read(vp.find("charlist_CH", "txt"))
print("charlist_CH.txt 前 120 字节: %r" % clbuf[:120])
m = re.search(rb'count=(\d+)', clbuf)
if m:
    body = clbuf[m.end():]
    CL = [int(x) for x in re.findall(rb'\d+', body)]
    print("有 count= 头，count=%s，解析得 %d 项" % (m.group(1).decode(), len(CL)))
else:
    CL = [int(x) for x in re.findall(rb'\d+', clbuf)]
    print("无 count= 头，解析得 %d 项" % len(CL))
print("CL[0]=%d(应为32) CL[332]=%#x(们4EEC) CL[371]=%#x(你4F60) CL[422]=%#x(兄5144) CL[1035]=%#x(弟5F1F)"
      % (CL[0], CL[332], CL[371], CL[422], CL[1035]))
CP2I = {cp: i for i, cp in enumerate(CL)}

# ---------------------------------------------------------- 轻量 VPP 读取（textures 1.26GB 不能整读）
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
            nm = names[a:names.find(b'\x00', a)].decode('ascii', 'replace') if a < len(names) else ''
            ex = exts[b:exts.find(b'\x00', b)].decode('ascii', 'replace') if b else ''
            self.ents.append(dict(idx=i, name=nm, ext=ex, body=d, size=ln))

    def find(self, name, ext=None):
        for e in self.ents:
            if e['name'].lower() == name.lower() and (ext is None or e['ext'].lower() == ext.lower()):
                return e
        return None

    def read(self, ent):
        with open(self.path, 'rb') as f:
            f.seek(self.data_start + ent['body'])
            return f.read(ent['size'])


# ---------------------------------------------------------- vf3 解析（头部 0xBC）
def load_vf3(path_vpp, name="fnt_chinese", ext="vf3_pc"):
    v = S.Vpp(os.path.join(G, path_vpp))
    e = v.find(name, ext)
    buf = bytes(v.read(e))
    N = struct.unpack_from("<I", buf, 8)[0]
    U = list(struct.unpack_from("<%dI" % N, buf, 0xBC + 16 * N))
    V = list(struct.unpack_from("<%dI" % N, buf, 0xBC + 16 * N + 4 * N))
    recs = [struct.unpack_from("<IIII", buf, 0xBC + k * 16) for k in range(min(N, 8))]
    return buf, N, U, V, recs


pbuf, pN, pU, pV, precs = load_vf3("patch.vpp_pc")
cbuf, cN, cU, cV, crecs = load_vf3("common.vpp_pc")
for tag, N, U, V, recs in (("patch", pN, pU, pV, precs), ("common", cN, cU, cV, crecs)):
    resets = [i for i in range(1, N) if U[i] < U[i - 1]][:10]
    vjumps = [i for i in range(1, N) if V[i] != V[i - 1]][:10]
    print("\n== %s vf3: N=%d size=%d" % (tag, N, len(pbuf if tag == "patch" else cbuf)))
    print("   recs[0:4]=%s" % (recs[:4],))
    print("   U[0:14]=%s" % U[:14])
    print("   V[0:14]=%s" % V[:14])
    print("   U[68:80]=%s" % U[68:80])
    print("   U 重置点(前10)=%s  共%d" % (resets, len([i for i in range(1, N) if U[i] < U[i - 1]])))
    print("   V 跳点(前10)=%s  共%d" % (vjumps, len([i for i in range(1, N) if V[i] != V[i - 1]])))

# ---------------------------------------------------------- 图集
def load_atlas_patch():
    v = S.Vpp(os.path.join(G, "patch.vpp_pc"))
    e = v.find("fnt_chinese", "g_peg_pc")
    return bytes(v.read(e)), e

def load_atlas_common():
    vl = VppLite(os.path.join(G, "textures.vpp_pc"))
    e = vl.find("fnt_chinese")
    cands = [x for x in vl.ents if x['name'].lower() == 'fnt_chinese']
    print("\ntextures.vpp_pc 中 fnt_chinese 候选: %s" % [(c['ext'], c['size']) for c in cands])
    return vl.read(e), e

def dxt3_fast(data, w=2048, h=2048):
    bw, bh = w // 4, h // 4
    blk = np.frombuffer(data, np.uint8)[:bw * bh * 16].reshape(bh, bw, 16)
    c0 = blk[:, :, 8].astype(np.uint32) | (blk[:, :, 9].astype(np.uint32) << 8)
    c1 = blk[:, :, 10].astype(np.uint32) | (blk[:, :, 11].astype(np.uint32) << 8)
    def e565(v):
        r = ((v >> 11) & 0x1F).astype(np.float64) * 255.0 / 31
        g = ((v >> 5) & 0x3F).astype(np.float64) * 255.0 / 63
        b = (v & 0x1F).astype(np.float64) * 255.0 / 31
        return np.stack([r, g, b], -1)
    P0, P1 = e565(c0), e565(c1)
    m4 = (c0 > c1)[..., None]
    P2 = np.where(m4, (2 * P0 + P1) / 3, (P0 + P1) / 2)
    P3 = np.where(m4, (P0 + 2 * P1) / 3, 0.0)
    pal = np.stack([P0, P1, P2, P3], -2)                       # (bh,bw,4,3)
    word = np.ascontiguousarray(blk[:, :, 12:16]).view(np.uint32)[:, :, 0]
    pix = ((word[:, :, None] >> (2 * np.arange(16, dtype=np.uint32))) & 3)   # (bh,bw,16)
    BI, BJ = np.arange(bh)[:, None, None], np.arange(bw)[None, :, None]
    rgb = pal[BI, BJ, pix]                                       # (bh,bw,16,3)
    rgb = rgb.reshape(bh, bw, 4, 4, 3).transpose(0, 2, 1, 3, 4).reshape(h, w, 3)
    return rgb

pa, pe = load_atlas_patch()
ca, ce = load_atlas_common()
print("patch 图集: %s.%s %d 字节" % (pe['name'], pe['ext'], pe['size']))
print("common 图集: %s.%r %d 字节" % (ce['name'], ce['ext'], ce['size']))
prgb = dxt3_fast(pa)
crgb = dxt3_fast(ca)
pink = prgb.mean(2)
cink = crgb.mean(2)
print("图集解码完成 patch%s common%s" % (pink.shape, cink.shape))

# ---------------------------------------------------------- 渲染工具
def crop_ink(img, U, V, i, cell):
    x, y = int(U[i]), int(V[i])
    g = img[y:y + cell, x:x + cell]
    nz = np.argwhere(g > 24)
    if len(nz) == 0:
        return g
    y0, x0 = nz.min(0); y1, x1 = nz.max(0)
    return g[y0:y1 + 1, x0:x1 + 1]

def norm(g, size=56):
    im = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8))
    im = im.resize((size, size), Image.LANCZOS)
    return np.asarray(im, np.float64) / 255.0

# ---------------------------------------------------------- 锚点比对
ANCH = [(332, 0x4F4D, "们->位"), (359, 0x4F2A, "保->伪"), (371, 0x4EFB, "你->任"),
        (390, 0x5DE7, "兄->巧"), (1003, 0x5076, "弟->偶"), (1158, 0x8BE5, "护->该"),
        (1804, 0x74A8, "的->璨"), (2264, 0x8861, "要->衡"), (2635, 0x96C4, "需->雄")]

CELL_P, CELL_C = 31, 30
rows = []
print("\n=== 锚点比对（左=common[idx]  中=patch[目标码点]  右=patch[idx即原字符]）===")
for idx, cp, desc in ANCH:
    cg = norm(crop_ink(cink, cU, cV, idx, CELL_C))
    pj = CP2I.get(cp)
    pg = norm(crop_ink(pink, pU, pV, pj, CELL_P)) if pj is not None else np.zeros((56, 56))
    po = norm(crop_ink(pink, pU, pV, idx, CELL_P))
    rows.append((idx, cp, desc, cg, pg, po, pj))
    # 数值相似度（仅辅助，主要靠看图）
    d_t = np.abs(cg - pg).mean()
    d_o = np.abs(cg - po).mean()
    print("  idx=%-5d %s  目标=%s(patch#%s)  |common-目标|=%.4f  |common-原字符|=%.4f  %s"
          % (idx, desc, chr(cp), pj, d_t, d_o, "★目标更近" if d_t < d_o else ""))

# 拼图
SZ = 56
W = 3 * SZ + 80
H = len(rows) * (SZ + 26) + 30
canvas = Image.new("L", (W, H), 235)
from PIL import ImageDraw
dr = ImageDraw.Draw(canvas)
for r, (idx, cp, desc, cg, pg, po, pj) in enumerate(rows):
    y = 14 + r * (SZ + 26)
    dr.text((2, y + 20), "idx%d" % idx, fill=0)
    x = 62
    for g in (cg, pg, po):
        a = (np.clip(g, 0, 1) * 255).astype(np.uint8)
        canvas.paste(Image.fromarray(a), (x, y))
        x += SZ + 8
    dr.text((62, y + SZ + 2), "common[idx]", fill=60)
    dr.text((62 + SZ + 8, y + SZ + 2), "patch[%s]=%s" % (pj, chr(cp)), fill=60)
    dr.text((62 + 2 * (SZ + 8), y + SZ + 2), "patch[idx]=%s" % chr(CL[idx]), fill=60)
canvas.save(r"F:/sr2-cn/_h2b_anchors.png")
print("\n已保存 _h2b_anchors.png")

# ASCII 自检：patch[32..79] 与 common[32..79]
def ascii_strip(img, U, V, cell, lo, hi):
    out = []
    for i in range(lo, hi):
        g = crop_ink(img, U, V, i, cell)
        out.append(chr(i) if g.size and g.max() > 24 else "?")
    return "".join(out)

print("\nASCII 自检:")
print("  patch  [32:80]: %s" % ascii_strip(pink, pU, pV, CELL_P, 32, 80))
print("  common [32:80]: %s" % ascii_strip(cink, cU, cV, CELL_C, 32, 80))
print("  common [0:40] : %s" % ascii_strip(cink, cU, cV, CELL_C, 0, 40))
