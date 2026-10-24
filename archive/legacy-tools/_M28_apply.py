# -*- coding: utf-8 -*-
# 实施修复：1) le_strings 里所有「位」按规则换成同义字（等长替换，结构不变）
#           2) 图集第357格复制第327格（们 的字形）
# 所有规则均为等长替换 => 槽位流长度不变 => pointer 数组与 bucket 表无需改动
import sys, struct, shutil, hashlib, os
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
SRC = os.path.join(G, "patch.vpp_pc")
BAK = r"F:/sr2-cn/_backup_MEN/patch.vpp_pc.before_weifix"
OUT = r"F:/sr2-cn/_FIX/patch_weifix.vpp_pc"

RULES = [
    ("排位赛", "排名赛"), ("排位）", "排名）"), ("排位，", "排名，"),
    ("段位", "等级"),
    ("就位了", "到位了"), ("就位，", "到位，"), ("就位。", "到位。"), ("就位", "到位"),
    ("条位于", "条在于"), ("位于", "处于"),
    ("各位", "大家"),
    ("槽位", "槽号"),
    ("位置", "地点"),
    ("几位", "几个"), ("一位", "一个"), ("有位", "有个"),
    ("这位", "这个"), ("那位", "那个"), ("哪位", "哪个"),
    ("站位", "地点"),
    ("空位", "空座"),
    ("驾驶位", "驾驶座"),
]


def fix_text(t):
    for a, b in RULES:
        t = t.replace(a, b)
    return t


f = Font(SRC)
B = [chr(c) for c in f.charlist]
bidx = {c: i for i, c in enumerate(B)}
cn = Vpp(SRC)
data = bytearray(open(SRC, "rb").read())

changed = 0
checked = 0
for name in ("voice_script_CH", "static_CH", "platform_pc_CH"):
    e = cn.find(name, "le_strings")
    if not e:
        continue
    d = bytearray(cn.read(e))
    buckets, = struct.unpack_from("<H", d, 6)
    count, = struct.unpack_from("<I", d, 8)
    base = 12 + buckets * 8
    ptrs = struct.unpack_from("<%dI" % count, d, base)
    for i in range(count):
        p = ptrs[i]
        if p + 6 > len(d):
            continue
        q = p + 4
        sl = []
        while True:
            s, = struct.unpack_from(">H", d, q)
            q += 2
            if s == 0:
                break
            sl.append(s)
        txt = "".join(B[s - 32] if 0 <= s - 32 < len(B) else "?" for s in sl)
        if "位" not in txt:
            continue
        checked += 1
        nt = fix_text(txt)
        if nt == txt:
            continue
        # 校验等长
        if len(nt) != len(txt):
            print("!! 长度变化 %s: %r -> %r" % (name, txt[:30], nt[:30]))
            continue
        # 校验新文本全部字符可编码
        if any(ch not in bidx for ch in nt):
            bad = [ch for ch in nt if ch not in bidx]
            print("!! 无法编码 %s: %s" % (name, "".join(bad)))
            continue
        # 重写槽位（就地，长度不变）
        w = p + 4
        for ch in nt:
            struct.pack_into(">H", d, w, bidx[ch] + 32)
            w += 2
        struct.pack_into(">H", d, w, 0)
        changed += 1
    # 写回 vpp
    off = cn.abs_offset(e)
    data[off:off + len(d)] = d
    print("%-18s count=%-6d 含位记录=%d" % (name, count, checked))

print("\n成功替换记录 =", changed)

# --- 图集：第357格 <- 第327格（们 的字形）---
f2 = Font(SRC)
atlas = bytearray(f2.atlas)
CELL, PAD = 31, 3
SZ = CELL + PAD * 2


def px(A, X, Y):
    from sr2font import dec_block
    return dec_block(A, ((Y // 4) * (2048 // 4) + X // 4) * 16)[Y % 4][X % 4]


from sr2font import dec_block, enc_block

ux, uy = f2.uv(327)
vx, vy = f2.uv(357)
src = [[px(atlas, ux + xx, uy + yy) for xx in range(CELL)] for yy in range(CELL)]
for by in range(vy // 4, (vy + CELL - 1) // 4 + 1):
    for bx in range(vx // 4, (vx + CELL - 1) // 4 + 1):
        o = (by * (2048 // 4) + bx) * 16
        blk = [list(r) for r in dec_block(atlas, o)]
        for yy in range(4):
            Y = by * 4 + yy
            if not (vy <= Y < vy + CELL):
                continue
            for xx in range(4):
                X = bx * 4 + xx
                if vx <= X < vx + CELL:
                    blk[yy][xx] = src[Y - vy][X - vx]
        atlas[o:o + 16] = enc_block(blk)
print("图集第357格已复制第327格（们）")

# 写回图集
ae = cn.find("fnt_chinese", "g_peg_pc")
aoff = cn.abs_offset(ae)
data[aoff:aoff + len(atlas)] = atlas

os.makedirs(os.path.dirname(OUT), exist_ok=True)
os.makedirs(os.path.dirname(BAK), exist_ok=True)
if not os.path.exists(BAK):
    shutil.copy2(SRC, BAK)
    print("已备份原 patch.vpp_pc ->", BAK)
open(OUT, "wb").write(bytes(data))
print("输出:", OUT, " md5=", hashlib.md5(bytes(data)).hexdigest())
