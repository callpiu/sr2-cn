# -*- coding: utf-8 -*-
"""从 patch.vpp_pc 提取 fnt_chinese 图集，解码并裁出指定索引的字形，拼成带标注的大图"""
import sys, struct, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from _vpp import Vpp
from PIL import Image, ImageDraw, ImageFont

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
gv = Vpp(GAME)

# 找 fnt_chinese 的两条：图集(4MB) 与 vf3(67KB)
atlas = vf3 = None
for e in gv.entries():
    if e['name'] == 'fnt_chinese':
        d = gv.read(e)
        if len(d) == 4194304: atlas = d
        else: vf3 = d
print('atlas', len(atlas) if atlas else None, 'vf3', len(vf3) if vf3 else None)
if vf3:
    print('vf3 head', vf3[:32].hex())

def decode_dxt(data, w, h, mode='dxt3'):
    out = bytearray(w*h*4)
    bw, bh = w//4, h//4
    for by in range(bh):
        for bx in range(bw):
            off = (by*bw + bx) * 16
            blk = data[off:off+16]
            # color: two u16 LE
            c0, c1 = struct.unpack_from('<HH', blk, 8)
            def unpack(c):
                r = (c >> 11) & 0x1f; g = (c >> 5) & 0x3f; b = c & 0x1f
                return ((r<<3)|(r>>2), (g<<2)|(g>>4), (b<<3)|(b>>2), 255)
            e0, e1 = unpack(c0), unpack(c1)
            if c0 > c1:
                e2 = tuple((2*e0[i]+e1[i])//3 for i in range(3))+(255,)
                e3 = tuple((e0[i]+2*e1[i])//3 for i in range(3))+(255,)
            else:
                e2 = tuple((e0[i]+e1[i])//2 for i in range(3))+(255,)
                e3 = (0,0,0,0)
            pal = [e0,e1,e2,e3]
            bits = struct.unpack_from('<I', blk, 4)[0]
            if mode == 'dxt3':
                alpha = struct.unpack_from('<Q', blk, 0)[0]
                alist = [(alpha >> (4*i)) & 0xF for i in range(16)]
                alist = [a*17 for a in alist]
            else:
                a0, a1 = blk[0], blk[1]
                abits = int.from_bytes(blk[2:8], 'little')
                if a0 > a1:
                    at = [a0,a1]+[((7-i)*a0 + i*a1)//7 for i in range(1,7)]
                else:
                    at = [a0,a1]+[((5-i)*a0 + i*a1)//5 for i in range(1,5)]+[0,255]
                alist = [at[(abits >> (3*i)) & 7] for i in range(16)]
            for py in range(4):
                for px in range(4):
                    idx = (py*4+px)
                    pi = (bits >> (2*idx)) & 3
                    r,g,b,_ = pal[pi]
                    a = alist[idx]
                    yy, xx = by*4+py, bx*4+px
                    o = (yy*w+xx)*4
                    out[o]=r; out[o+1]=g; out[o+2]=b; out[o+3]=a
    return Image.frombytes('RGBA', (w,h), bytes(out))

W = H = 2048
img = decode_dxt(atlas, W, H, 'dxt3')
img.save(r'F:\sr2-cn\_atlas_dxt3.png')
img2 = decode_dxt(atlas, W, H, 'dxt5')
img2.save(r'F:\sr2-cn\_atlas_dxt5.png')
print('saved atlas previews')

COLS = 65
STEP = 31
def cell(i):
    x = 1 + STEP*(i % COLS); y = 1 + STEP*(i // COLS)
    return img.crop((x, y, x+30, y+30))

# 期望字形（按 charlist 顺序）
def parse_charlist(buf):
    out=[]
    for ln in buf.decode('latin-1').splitlines():
        s=ln.strip()
        if not s or s.startswith('//') or s.startswith('count'): continue
        try: out.append(int(s))
        except: pass
    return out
cl = parse_charlist(gv.read(gv.find('charlist_CH')))

# 关键索引
idxs = [336, 371, 403, 1784, 1836, 1035, 422, 332, 2667, 2296, 391, 1190, 410, 967, 362, 2656, 2268, 354, 2342]
SC = 4
CW = 30*SC
try:
    font = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 26)
    font2 = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 20)
except Exception:
    font = font2 = ImageFont.load_default()

percol = 5
rows = (len(idxs)+percol-1)//percol
cellW, cellH = CW+16, CW+64
canvas = Image.new('RGBA', (percol*cellW, rows*cellH), (255,255,255,255))
dr = ImageDraw.Draw(canvas)
for n, i in enumerate(idxs):
    cx = (n % percol)*cellW; cy = (n // percol)*cellH
    c = cell(i).resize((CW, CW), Image.NEAREST)
    canvas.alpha_composite(c, (cx+8, cy+8))
    ch = chr(cl[i]) if 0 <= i < len(cl) else '?'
    dr.rectangle([cx+6, cy+6, cx+8+CW, cy+8+CW], outline=(200,0,0,255))
    dr.text((cx+8, cy+10+CW), f'i={i}', fill=(0,0,0,255), font=font2)
    dr.text((cx+8, cy+36+CW), f'cl={ch}', fill=(0,0,180,255), font=font)
canvas.save(r'F:\sr2-cn\_cellcheck.png')
print('saved _cellcheck.png')

# 渲染字幕应有的字形行
sub_idx = [371,1836,1035,422,332,2667,2296,371,1836,391,1190]
row = Image.new('RGBA', (len(sub_idx)*CW, CW), (255,255,255,255))
for n,i in enumerate(sub_idx):
    row.alpha_composite(cell(i).resize((CW,CW), Image.NEAREST), (n*CW, 0))
row.save(r'F:\sr2-cn\_sub_expected.png')
print('saved _sub_expected.png', sub_idx)
