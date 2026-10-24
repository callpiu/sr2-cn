# -*- coding: utf-8 -*-
"""Minimal DXT3(BC2) decode + PNG write, pure stdlib."""
import struct, zlib


def dxt3_decode_block(src, x, y, w, h, px):
    """decode one 4x4 BC2 block at px[x,y] (px is bytearray w*h*4 RGBA)"""
    a0, a1 = struct.unpack_from('<HH', src, 0)
    c0, c1 = struct.unpack_from('<HH', src, 8)
    bits = struct.unpack_from('<I', src, 12)[0]
    # colors
    def rgb565(v):
        r = (v >> 11) & 31
        g = (v >> 5) & 63
        b = v & 31
        return (r * 255 // 31, g * 255 // 63, b * 255 // 31)

    C0 = rgb565(c0)
    C1 = rgb565(c1)
    if c0 > c1:
        C2 = tuple((2 * C0[i] + C1[i]) // 3 for i in range(3))
        C3 = tuple((C0[i] + 2 * C1[i]) // 3 for i in range(3))
    else:
        C2 = tuple((C0[i] + C1[i]) // 2 for i in range(3))
        C3 = (0, 0, 0)
    cols = (C0, C1, C2, C3)
    for by in range(4):
        av = struct.unpack_from('<H', src, 2 * by)[0]
        for bx in range(4):
            xx, yy = x + bx, y + by
            if xx >= w or yy >= h:
                continue
            ci = (bits >> (2 * (4 * by + bx))) & 3
            r, g, b = cols[ci]
            alpha4 = (av >> (4 * bx)) & 15
            o = (yy * w + xx) * 4
            px[o] = r
            px[o + 1] = g
            px[o + 2] = b
            px[o + 3] = alpha4 * 17


def dxt3_decode(data, w, h):
    px = bytearray(w * h * 4)
    bw, bh = w // 4, h // 4
    for by in range(bh):
        for bx in range(bw):
            o = (by * bw + bx) * 16
            dxt3_decode_block(data[o:o + 16], bx * 4, by * 4, w, h, px)
    return px


def write_png(path, px, w, h, scale=1, white_bg=True):
    if scale != 1:
        nw, nh = w * scale, h * scale
        npx = bytearray(nw * nh * 4)
        for y in range(h):
            for x in range(w):
                o = (y * w + x) * 4
                no = ((y * scale) * nw + x * scale) * 4
                for sy in range(scale):
                    for sx in range(scale):
                        q = no + (sy * nw + sx) * 4
                        npx[q:q + 4] = px[o:o + 4]
        px, w, h = npx, nw, nh
    if white_bg:
        # composite over white
        for i in range(0, len(px), 4):
            a = px[i + 3]
            px[i] = px[i] * a // 255 + (255 - a)
            px[i + 1] = px[i + 1] * a // 255 + (255 - a)
            px[i + 2] = px[i + 2] * a // 255 + (255 - a)
            px[i + 3] = 255
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += px[y * w * 4:(y + 1) * w * 4]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(t, d):
        c = struct.pack('>I', len(d)) + t + d
        return c + struct.pack('>I', zlib.crc32(t + d) & 0xFFFFFFFF)

    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', comp)
    png += chunk(b'IEND', b'')
    open(path, 'wb').write(png)


def crop_png(srcpx, sw, sh, x, y, cw, ch, scale, path):
    out = bytearray(cw * ch * 4 * scale * scale)
    for yy in range(ch):
        for xx in range(cw):
            o = ((y + yy) * sw + (x + xx)) * 4
            for sy in range(scale):
                for sx in range(scale):
                    q = ((yy * scale + sy) * cw * scale + (xx * scale + sx)) * 4
                    out[q:q + 4] = srcpx[o:o + 4]
    write_png(path, out, cw * scale, ch * scale)
