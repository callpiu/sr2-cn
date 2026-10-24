"""v513 版 patch 构建：在【v417 干净基线】上只做 GameSpy→OpenSpy 替换。

★ 为什么不用 v420 ★
v420 = v417 + v418槽位改动 + GameSpy→OpenSpy。
v418 的槽位改动（charlist 6 行 + vf3 6 字形 + 458 条记录换槽）经用户三次实测
均无效（徒/录/弹仍显示为建/底/床），且徒/录/弹的渲染机制尚未查明，
带着它交付等于把未验证的改动塞给用户。
⇒ 本版只保留 GameSpy→OpenSpy（纯 ASCII 等长替换，零风险）。

★ 差异预期：仅 40 字节（10 条记录 × 4 个字符 G→O / a→p / m→e / e→n）
"""
import sys, os, struct, hashlib, shutil
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
BASE = os.path.join(GAME, "patch.vpp_pc.v417bak")     # v417 干净基线
OUT = r"F:\sr2-cn\_fix_candidates\patch_v513.vpp_pc"
EXPECT_BASE = "24920a5c9f3b7b5daba33b402989bb03"

assert hashlib.md5(open(BASE,'rb').read()).hexdigest() == EXPECT_BASE, "基线不是 v417"
print("基线 v417 校验 OK")

v = Vpp(BASE)
GS = [ord(c) for c in "GameSpy"]     # G a m e S p y
OP = [ord(c) for c in "OpenSpy"]     # O p e n S p y

changed = 0; tbl = {}; records = []
for e in v.entries():
    if e['ext'] != 'le_strings' or '_CH' not in e['name']: continue
    b = v.read(e)
    try: bc,c,oa,offs = file_offsets(b)
    except: continue
    body = v.data_start + e['body']; seen = set()
    for off in offs:
        sp = body + off + 8
        if sp in seen: continue
        seen.add(sp)
        if not (body < sp <= len(v.data) - 24): continue
        i = sp; n = len(v.data); sl = []
        while i + 2 <= n:
            x,y = v.data[i], v.data[i+1]
            if x == 0 and y == 0: break
            sl.append((x << 8) | y); i += 2
        if not sl: continue
        hit = None
        for k in range(len(sl) - 6):
            if sl[k:k+7] == GS:
                hit = k; break
        if hit is None: continue
        p = sp + hit*2
        for j, ch in enumerate(OP):
            struct.pack_into('>H', v.data, p + j*2, ch)
        changed += 1
        tbl[e['name']] = tbl.get(e['name'],0)+1
        records.append((e['name'], off, sl[hit:hit+7]))

print("替换 %d 条: %s" % (changed, tbl))
for n,o,_ in records:
    print("   [%s] @0x%X" % (n,o))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
v.save(OUT)
md5v = hashlib.md5(open(OUT,'rb').read()).hexdigest()
print("\n写出 %s" % OUT)
print("  md5 =", md5v)
print("  size =", os.path.getsize(OUT))

# ---- 严格差分 ----
a = open(BASE,'rb').read(); b2 = open(OUT,'rb').read()
assert len(a) == len(b2), "大小必须一致"
d = [i for i in range(len(a)) if a[i] != b2[i]]
print("\n=== 差分校验 ===")
print("  差异字节数: %d  (预期 40 = 10条 x 4字符)" % len(d))
segs = []
if d:
    s = d[0]; p = d[0]
    for x in d[1:]:
        if x == p+1: p = x
        else: segs.append((s,p)); s = x; p = x
    segs.append((s,p))
mapping = {ord('G'):ord('O'), ord('a'):ord('p'), ord('m'):ord('e'), ord('e'):ord('n')}
allok = True
for (x,y) in segs:
    old = a[x:y+1]; new = b2[x:y+1]
    rebuilt = bytes(mapping.get(c,c) for c in old)
    if rebuilt != new:
        allok = False
        print("  ★段 @0x%X 不符合: %r -> %r" % (x, old, new))
print("  所有差异均为 GameSpy->OpenSpy:", allok)
assert len(d) == 40 and allok

# ---- 残留检查（只查中文表：其他语言是官方原版翻译，游戏读不到）----
# 说明：patch 内还含 CZ/DK/ES/FR/IT/RU/SE/US/PL/NL/DE 等语种的官方译文，
# 其中 "GameSpy" 字样是官方原文，属正常，不应改动（改了反而破坏对应语言）。
left = 0
for e in v.entries():
    if e['ext'] != 'le_strings' or '_CH' not in e['name']: continue
    bb = v.read(e)
    try: bc,c,oa,offs = file_offsets(bb)
    except: continue
    body = v.data_start + e['body']; seen=set()
    for off in offs:
        sp = body + off + 8
        if sp in seen: continue
        seen.add(sp)
        if not (body < sp <= len(v.data) - 24): continue
        i=sp; n=len(v.data); sl=[]
        while i+2<=n:
            x,y=v.data[i],v.data[i+1]
            if x==0 and y==0: break
            sl.append((x<<8)|y); i+=2
        for k in range(len(sl)-6):
            if sl[k:k+7]==GS: left += 1
print("  残留 GameSpy（中文表）: %d (应 0)" % left)
assert left == 0
print("\n✓ v513 patch 构建完成")
print("  注：其它语种表中的 GameSpy 为官方原文，未改动（游戏中文模式不读取）")