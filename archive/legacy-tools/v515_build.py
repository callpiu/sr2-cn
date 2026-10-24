"""v515：复现 v422 的双槽冗余方案（用户确认 v422 时主菜单/游戏均正常）。

★★★ 关键事实 ★★★
用户实测反馈："v422 时还是正常的"。v422 的组合是：
    patch   = 字表 6 处改码点 + 458 条字符串换槽(1090→717 等)
    common  = vf3 6 处重指字形(653/685 → 徒字形 等)
    textures= 官方原版（未动）

★ 双槽冗余原理（本次已解码）★
    徒: charlist[653]=徒, charlist[685]=徒
        vf3[653]=徒字形,   vf3[685]=徒字形
        字符串用 slot717 → 引擎取 idx685(徒)
                        → 若引擎再多减 0x20 取 idx653(也是徒) ⇒ 仍是徒
    ⇒ 把"正常索引"和"再减32的索引"都填成目标字，两条路径都正确。

★ 只做这一件事，不碰主菜单那批（阶/我/缉/棍 无规律，另行处理）
★ 基线：patch 用 v513(=v417+GameSpy修正)，common 用官方原版
"""
import sys, os, struct, hashlib, shutil
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
COMMON = os.path.join(GAME, "common.vpp_pc")
PATCH  = os.path.join(GAME, "patch.vpp_pc")
COMMON_BAK = COMMON + ".official_bak"
PATCH_BAK  = PATCH + ".v513.bak"
OUT_C = r"F:\sr2-cn\_fix_candidates\common_v515.vpp_pc"
OUT_P = r"F:\sr2-cn\_fix_candidates\patch_v515.vpp_pc"

# v422 用过的槽（已验证有效）：旧槽 -> 新槽
#   徒 1090 -> 717 (idx685, 配对 653)
#   录 1077 -> 729 (idx697, 配对 665)
#   弹 1073 -> 957 (idx925, 配对 893)
OLD2NEW = {1090: 717, 1077: 729, 1073: 957}
# 新槽对应的"配对位"（= 新槽idx - 0x20）
PAIR = {717: 653, 729: 665, 957: 893}
# 每个字在 common vf3 里正确字形的源索引
GLYPH_SRC = {717: 1058, 729: 1045, 957: 1041}   # 徒/录/弹 原本的正确索引

# ---------- 备份 ----------
for src, bak, nm in ((PATCH, PATCH_BAK, "patch"), (COMMON, COMMON_BAK, "common")):
    if not os.path.exists(bak):
        shutil.copy2(src, bak)
        print("✓ 备份 %s -> %s  md5 %s" % (nm, os.path.basename(bak),
                                            hashlib.md5(open(bak,'rb').read()).hexdigest()))
    else:
        print("%s 备份已存在  md5 %s" % (nm, hashlib.md5(open(bak,'rb').read()).hexdigest()))

# ================= common: vf3 重指 =================
vc = Vpp(COMMON)
ec = vc.find("fnt_chinese","vf3_pc"); co = vc.data_start + ec['body']
NC = struct.unpack_from('<I', vc.data, co + 0x08)[0]
def cuv(i): return (struct.unpack_from('<i', vc.data, co+0xAF6C+i*4)[0],
                    struct.unpack_from('<i', vc.data, co+0xDB18+i*4)[0])
def crec(i): return struct.unpack_from('<IIII', vc.data, co+0xD0+i*16)

print("\n=== common vf3 重指 ===")
for new, pair in PAIR.items():
    src = GLYPH_SRC[new]
    u, v = cuv(src); r = crec(src)
    for idx in (new - 0x20, pair):
        struct.pack_into('<i', vc.data, co+0xAF6C+idx*4, u)
        struct.pack_into('<i', vc.data, co+0xDB18+idx*4, v)
        struct.pack_into('<IIII', vc.data, co+0xD0+idx*16, *r)
    print("  新槽%d: idx%d 和配对 idx%d 都 -> %s 字形(源idx%d)" % (new, new-0x20, pair, u, src))
vc.save(OUT_C)
print("✓ 写出", OUT_C, "md5", hashlib.md5(open(OUT_C,'rb').read()).hexdigest())

# ================= patch: 换槽 + 字表改码点 =================
vp = Vpp(PATCH)
cl_off_entry = vp.find("charlist_CH","txt")
cl_raw = vp.read(cl_off_entry).decode('utf-8')
segs = cl_raw.split('\n')
cl = [int(s) for s in segs if s.strip().isdigit()]

changed = 0; tbl = {}
for e in vp.entries():
    if e['ext'] != 'le_strings' or '_CH' not in e['name']: continue
    b = vp.read(e)
    try: bc,c,oa,offs = file_offsets(b)
    except: continue
    body = vp.data_start + e['body']; seen = set()
    for off in offs:
        sp = body + off + 8
        if sp in seen: continue
        seen.add(sp)
        if not (body < sp <= len(vp.data) - 24): continue
        i = sp; n = len(vp.data); sl = []
        while i + 2 <= n:
            x,y = vp.data[i], vp.data[i+1]
            if x == 0 and y == 0: break
            sl.append((x << 8) | y); i += 2
        if not sl or not any(s in OLD2NEW for s in sl): continue
        for j, s in enumerate(sl):
            if s in OLD2NEW:
                struct.pack_into('>H', vp.data, sp + j*2, OLD2NEW[s])
        changed += 1; tbl[e['name']] = tbl.get(e['name'],0)+1
print("\n✓ patch 字符串换槽 %d 条: %s" % (changed, tbl))

# 字表：新槽 idx 与配对 idx 都改成对应字的码点（5位→5位，长度不变）
c2s = {}
for i, cp in enumerate(cl):
    if cp >= 0x100: c2s.setdefault(chr(cp), i + 0x20)
print("\n=== 字表改码点 ===")
touched = []
for ch, new in (('徒',717), ('录',729), ('弹',957)):
    want = ord(ch)
    for idx in (new - 0x20, PAIR[new]):
        old = segs[idx]
        assert len(str(want)) == len(old), (ch, idx, old, want)
        segs[idx] = str(want)
        touched.append((ch, idx, old, segs[idx]))
for ch, idx, old, new_v in touched:
    print("  %r charlist[%d]: %s -> %s" % (ch, idx, old, new_v))

new_body = '\n'.join(segs).encode('utf-8')
assert len(new_body) == len(cl_raw.encode('utf-8')), "字表长度变了"
off = vp.data_start + cl_off_entry['body']
vp.data[off:off+len(new_body)] = new_body
vp.save(OUT_P)
print("✓ 写出", OUT_P, "md5", hashlib.md5(open(OUT_P,'rb').read()).hexdigest())

# ================= 校验 =================
print("\n=== 校验：两条路径都正确 ===")
v2 = Vpp(OUT_C); e2 = v2.find("fnt_chinese","vf3_pc"); c2 = v2.data_start + e2['body']
def nUv(i): return (struct.unpack_from('<i', v2.data, c2+0xAF6C+i*4)[0],
                    struct.unpack_from('<i', v2.data, c2+0xDB18+i*4)[0])
vp2 = Vpp(OUT_P)
cl2 = [int(s) for s in vp2.read(vp2.find("charlist_CH","txt")).decode('utf-8').split('\n') if s.strip().isdigit()]
ok = True
for ch, new in (('徒',717), ('录',729), ('弹',957)):
    tgt = nUv(GLYPH_SRC[new])
    a, b = nUv(new-0x20), nUv(PAIR[new])
    ca, cb = chr(cl2[new-0x20]), chr(cl2[PAIR[new]])
    good = (a==tgt and b==tgt and ca==ch and cb==ch)
    ok &= good
    print("  %r 新槽%d: vf3正常=%s vf3配对=%s | 字表正常=%r 字表配对=%r  %s" %
          (ch, new, a, b, ca, cb, "OK" if good else "!!"))
assert ok
left = 0
for e in vp2.entries():
    if e['ext'] != 'le_strings' or '_CH' not in e['name']: continue
    b = vp2.read(e)
    try: bc,c,oa,offs = file_offsets(b)
    except: continue
    body = vp2.data_start + e['body']; seen=set()
    for off2 in offs:
        sp = body + off2 + 8
        if sp in seen: continue
        seen.add(sp)
        if not (body < sp <= len(vp2.data) - 24): continue
        i=sp; n=len(vp2.data)
        while i+2<=n:
            x,y=vp2.data[i],vp2.data[i+1]
            if x==0 and y==0: break
            if (x<<8|y) in OLD2NEW: left += 1
            i+=2
print("  残留旧槽: %d (应0)" % left)
assert left == 0
print("\n✓ v515 构建完成（候选，未部署）")