# -*- coding: utf-8 -*-
import os, sys, struct, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _vpp import Vpp
GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def load_charlist(path):
    v = Vpp(path); e = v.find('charlist_CH')
    b = v.read(e).decode('utf-8', 'replace')
    out = []
    for ln in b.replace('\r\n', '\n').split('\n'):
        ln = ln.strip()
        if not ln or ln.startswith('//') or '=' in ln: continue
        out.append(int(ln))
    return out

CL = load_charlist(os.path.join(GAME, 'patch.vpp_pc'))
inv = {c: i for i, c in enumerate(CL)}

rendered = "任璨偶巧位雄衡任璨伪该"
g_idx = [inv[ord(c)] for c in rendered]
print("渲染字形索引:", g_idx)

def parse_lestrings(buf):
    magic, ver, buckets, count = struct.unpack_from('<IHHI', buf, 0)
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
        if len(body) < 6: continue
        h = struct.unpack_from('>I', body, 0)[0]
        slots = []; p = 4
        while p + 1 < len(body):
            v = struct.unpack_from('>H', body, p)[0]; p += 2
            if v == 0: break
            slots.append(v)
        recs.append((h, slots))
    return recs

sigM1 = [403,1868,1067,454,364,2699,2328,403,1868,423,1222]
sigM2 = [g+32 for g in g_idx]
print("sigM1:", sigM1)
print("sigM2:", sigM2)

buf = Vpp(os.path.join(GAME, 'patch.vpp_pc')).read(
      Vpp(os.path.join(GAME, 'patch.vpp_pc')).find('static_CH'))
recs = parse_lestrings(buf)
print("records:", len(recs))

for tag, sig in (('M1', sigM1), ('M2', sigM2)):
    print("\n--- %s 只比中文字槽位 ---" % tag)
    n = 0
    for h, slots in recs:
        hi = [s for s in slots if s >= 0x100]
        if hi == sig:
            print("  HIT %08X  slots=%s" % (h, slots)); n += 1
    print("  命中 %d 条" % n)

# 另外：看看 sigM1/sigM2 的前几个槽位在整表中是否有任何记录包含
print("\n--- 表内是否出现 368 / 442 / 999 / 394 / 2688 / 2300 / 386 / 2374 这些槽位 ---")
allslots = set()
for h, slots in recs:
    allslots.update(slots)
for s in [368,442,999,394,2688,2300,386,2374,1816]:
    print("  slot %5d 出现: %s" % (s, s in allslots))
