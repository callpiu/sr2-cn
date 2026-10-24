# -*- coding: utf-8 -*-
"""判决性测试：
   观察到的渲染字形（从截图逐字读出）在 charlist_CH 中的索引 = 引擎实际使用的字形格号。
   分两种模型：
     M1 引擎: glyph = charlist[slot-32]     -> 源记录应为 F284ED87 (slots 403,1868,...)
     M2 引擎: glyph = charlist[slot-32] 且 charlist 被错位 -> 源记录 slots = glyphIdx+32
   在 static_CH 全表里反查：是否存在 slots == glyphIdx+32 的记录。
"""
import os, sys, struct, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _vpp import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# ---- 1. 取 charlist_CH (游戏内) ----
def load_charlist(path):
    v = Vpp(path)
    e = v.find('charlist_CH')
    b = v.read(e).decode('utf-8', 'replace')
    out = []
    for ln in b.replace('\r\n', '\n').split('\n'):
        ln = ln.strip()
        if not ln or ln.startswith('//') or '=' in ln:
            continue
        out.append(int(ln))
    return out

CL = load_charlist(os.path.join(GAME, 'patch.vpp_pc'))
print("charlist_CH len =", len(CL))
inv = {c: i for i, c in enumerate(CL)}

def idx(ch):
    return inv.get(ord(ch), None)

# ---- 2. 从截图读出的渲染串 ----
rendered = "任璨偶巧位雄衡任璨伪该"
src_text = "你的弟兄们需要你的保护"   # 去掉空格
print("\n[截图] 渲染:", rendered)
print("[推断] 源文:", src_text)
g_idx = [idx(c) for c in rendered]
print("渲染字形索引:", g_idx)

# ---- 3. 解析 le_strings ----
def parse_lestrings(buf):
    magic, ver, buckets, count = struct.unpack_from('<IHHI', buf, 0)
    assert magic == 0xA84C7F73, hex(magic)
    offs = []
    for i in range(buckets):
        c, off = struct.unpack_from('<II', buf, 0x0C + i * 8)
        for j in range(c):
            offs.append(struct.unpack_from('<I', buf, off + j * 4)[0])
    offs.sort()
    recs = []
    for k, o in enumerate(offs):
        end = offs[k + 1] if k + 1 < len(offs) else len(buf)
        body = buf[o:end]
        if len(body) < 6:
            continue
        h = struct.unpack_from('>I', body, 0)[0]
        slots = []
        p = 4
        while p + 1 < len(body):
            v = struct.unpack_from('>H', body, p)[0]
            p += 2
            if v == 0:
                break
            slots.append(v)
        recs.append((h, slots))
    return recs, count

# 找 static_CH
cands = []
for d in [GAME, os.path.join(GAME, 'Mods')]:
    for f in glob.glob(os.path.join(d, '*.vpp_pc')):
        cands.append(f)
cands += glob.glob(os.path.join(GAME, 'Mods', '*.le_strings'))

target_ident = [g + 32 for g in g_idx]        # M2 假设的源槽位
target_real  = [403,1868,1067,454,364,2699,2328,403,1868,423,1222]  # M1

print("\ntarget(M2 identity) :", target_ident)
print("target(M1 known)    :", target_real)

found = []
for f in cands:
    if f.lower().endswith('.le_strings'):
        buf = open(f, 'rb').read()
        recs = None
        try:
            recs, cnt = parse_lestrings(buf)
        except Exception as ex:
            continue
        label = f
        for h, slots in recs:
            if slots == target_ident:
                found.append(('M2', label, h, slots))
            if slots == target_real:
                found.append(('M1', label, h, slots))
        continue
    try:
        v = Vpp(f)
    except Exception:
        continue
    for e in v.entries():
        nm = e['name'].lower()
        if 'static_ch' not in nm:
            continue
        buf = v.read(e)
        try:
            recs, cnt = parse_lestrings(buf)
        except Exception as ex:
            print("  parse fail", label if False else f, nm, ex); continue
        print("  [%s] %s/%s  recs=%d count=%d" % (os.path.basename(f), e['name'], e['ext'], len(recs), cnt))
        for h, slots in recs:
            if slots == target_ident:
                found.append(('M2', f + '::' + e['name'], h, slots))
            if slots == target_real:
                found.append(('M1', f + '::' + e['name'], h, slots))

print("\n=== 命中 ===")
for m, lab, h, slots in found:
    print(" %s  %08X  %s" % (m, h, lab))
    print("     slots:", slots)
if not found:
    print(" (无命中)")
