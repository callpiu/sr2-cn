"""v422：把徒/录/弹 迁到【完全空闲】的槽位，避开所有被占用的坏字位。

思路（用户建议：把坏字位替换成别的字）：
  建/底/床 的槽位被大量真实字符串使用 ⇒ 不能占用它们。
  改为：给徒/录/弹 分配【从未被任何 CH 串引用】的新槽 S，
  且要求 S-0x40（坏路径落点）也从未被引用 ⇒ 两条路径都不会撞到任何在用汉字。
  然后把 vf3(新槽)、vf3(S-0x20)、vf3(S-0x40) 三处字形都重指成目标字。

★ 同时修 patch 的 charlist? 不需要 —— charlist 只决定 slot→码点，
  而我们要让"同一 slot"在两条路径下显示同一字，所以字形层面重指即可。
  但要注意：字表里 S-0x20 / S-0x40 对应的码点仍是原来的字（吐/吴/…），
  这不影响显示（渲染只看 vf3 字形），但为保险同时把它们也指向目标字码点。
"""
import sys, os, struct, hashlib, shutil
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
COMMON = os.path.join(GAME, "common.vpp_pc")
PATCH  = os.path.join(GAME, "patch.vpp_pc")
COMMON_BAK = COMMON + ".v420bak"
PATCH_BAK  = PATCH + ".v420bak"
OUT_C = r"F:\sr2-cn\_fix_candidates\common_v422.vpp_pc"
OUT_P = r"F:\sr2-cn\_fix_candidates\patch_v422.vpp_pc"

# 当前线上是 v420：v418 的 2288(徒)/2325(录)/2616(弹) 槽还在用
CUR_SLOT = {'徒': 2288, '录': 2325, '弹': 2616}
OLD_SLOT = {'徒': 1090, '录': 1077, '弹': 1073}
TARGET_IDX = {'徒': 1058, '录': 1045, '弹': 1041}   # common vf3 内正确字形源

# ---------- 统计已用槽 ----------
vp = Vpp(PATCH)
cl_lines = vp.read(vp.find("charlist_CH","txt")).decode('utf-8').split('\n')
cl = [int(s) for s in cl_lines if s.strip().isdigit()]
CLLEN = len(cl)
used = set()
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
        i = sp; n = len(vp.data)
        while i + 2 <= n:
            x,y = vp.data[i], vp.data[i+1]
            if x == 0 and y == 0: break
            used.add((x << 8) | y); i += 2
print("字表长度 %d, CH 已用槽 %d" % (CLLEN, len(used)))

# common vf3 尺寸
vc = Vpp(COMMON)
ec = vc.find("fnt_chinese","vf3_pc"); co = vc.data_start + ec['body']
NC = struct.unpack_from('<I', vc.data, co + 0x08)[0]
def cuv(v_, i):
    return (struct.unpack_from('<i', v_.data, co+0xAF6C+i*4)[0],
            struct.unpack_from('<i', v_.data, co+0xDB18+i*4)[0])
def crc_(v_, i):
    return struct.unpack_from('<IIII', v_.data, co+0xD0+i*16)

# ---------- 选槽：新槽 S 与 S-0x40 都必须 (a)未被 CH 引用 (b)在字表和 vf3 范围内 ----------
cands = []
for S in range(0x100, CLLEN + 0x20):
    if S in used: continue
    bad = S - 0x40
    if bad < 0x100 or bad in used: continue
    a, b = S - 0x20, S - 0x40
    if a >= NC or b >= NC: continue          # vf3 越界
    if a >= CLLEN or b >= CLLEN: continue   # 字表越界
    cands.append(S)
print("合格空闲槽: %d  %s" % (len(cands), cands[:12]))

assert len(cands) >= 3
NEW = {}
for i, ch in enumerate(('徒','录','弹')):
    NEW[ch] = cands[i]
print("\n分配:")
for ch in ('徒','录','弹'):
    S = NEW[ch]; a, b = S-0x20, S-0x40
    print("  %r: 原槽%d(已换2288等) -> 新槽%d  (字表[%d]=%r 字表[%d]=%r)" % (
        ch, OLD_SLOT[ch], S, a, chr(cl[a]), b, chr(cl[b])))

# ---------- 备份 ----------
for src, dst, nm in ((PATCH, PATCH_BAK, "patch"), (COMMON, COMMON_BAK, "common")):
    if not os.path.exists(dst):
        shutil.copy2(src, dst)
        print("\n✓ 备份 %s -> md5 %s" % (nm, hashlib.md5(open(dst,'rb').read()).hexdigest()))
    else:
        print("%s 备份已存在 md5 %s" % (nm, hashlib.md5(open(dst,'rb').read()).hexdigest()))

# ---------- ① patch: 2288/2325/2616 -> 新槽 ----------
BACK2 = {CUR_SLOT[ch]: NEW[ch] for ch in ('徒','录','弹')}
print("\n槽替换:", BACK2)
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
        if not sl or not any(s in BACK2 for s in sl): continue
        for j, s in enumerate(sl):
            if s in BACK2:
                struct.pack_into('>H', vp.data, sp + j*2, BACK2[s])
        changed += 1; tbl[e['name']] = tbl.get(e['name'],0)+1
print("✓ patch 换槽 %d 条: %s" % (changed, tbl))
vp.save(OUT_P)
print("  写出", OUT_P, "md5", hashlib.md5(open(OUT_P,'rb').read()).hexdigest())

# ---------- ② patch charlist: 把新槽的两条路径码点也指向目标字 ----------
#  行长度必须保持（5位十进制 -> 5位十进制）
cl_off = vp.data_start + vp.find("charlist_CH","txt")['body']
segs = vp.read(vp.find("charlist_CH","txt")).decode('utf-8').split('\n')
touched = []
for ch in ('徒','录','弹'):
    S = NEW[ch]
    for idx in (S-0x20, S-0x40):
        old = segs[idx]
        segs[idx] = str(ord(ch))
        touched.append((idx, old, segs[idx]))
new_body = '\n'.join(segs).encode('utf-8')
old_body = vp.read(vp.find("charlist_CH","txt"))
assert len(new_body) == len(old_body), (len(new_body), len(old_body))
vp.data[cl_off:cl_off+len(new_body)] = new_body
for idx, o, n in touched:
    print("  charlist[%d]: %s -> %s" % (idx, o, n))
vp.save(OUT_P)
print("✓ patch charlist 已更新，md5", hashlib.md5(open(OUT_P,'rb').read()).hexdigest())

# ---------- ③ common vf3: 三处字形重指 ----------
for ch in ('徒','录','弹'):
    S = NEW[ch]; src = TARGET_IDX[ch]
    u, w = cuv(vc, src); r = crc_(vc, src)
    for idx in (S-0x20, S-0x40):
        struct.pack_into('<i', vc.data, co+0xAF6C+idx*4, u)
        struct.pack_into('<i', vc.data, co+0xDB18+idx*4, w)
        struct.pack_into('<IIII', vc.data, co+0xD0+idx*16, *r)
vc.save(OUT_C)
print("\n✓ common vf3 重指 6 处，md5", hashlib.md5(open(OUT_C,'rb').read()).hexdigest())

# ---------- 校验 ----------
print("\n=== 校验 ===")
v2 = Vpp(OUT_C); e2 = v2.find("fnt_chinese","vf3_pc"); c2 = v2.data_start + e2['body']
def nUv(i): return (struct.unpack_from('<i', v2.data, c2+0xAF6C+i*4)[0],
                    struct.unpack_from('<i', v2.data, c2+0xDB18+i*4)[0])
vp2 = Vpp(OUT_P)
cl2 = [int(s) for s in vp2.read(vp2.find("charlist_CH","txt")).decode('utf-8').split('\n') if s.strip().isdigit()]
ok = True
for ch in ('徒','录','弹'):
    S = NEW[ch]; tgt = nUv(TARGET_IDX[ch])
    a, b = nUv(S-0x20), nUv(S-0x40)
    ca, cb = chr(cl2[S-0x20]), chr(cl2[S-0x40])
    good = (a==tgt and b==tgt and ca==ch and cb==ch)
    ok &= good
    print("  %r 新槽%d: vf3正常=%s vf3坏=%s 字表正常=%r 字表坏=%r  %s" % (
        ch,S,a,b,ca,cb,"OK" if good else "★"))
assert ok
# 确认无残留 2288/2325/2616
left=0
for e in vp2.entries():
    if e['ext']!='le_strings' or '_CH' not in e['name']: continue
    b=vp2.read(e)
    try: bc,c,oa,offs=file_offsets(b)
    except: continue
    body=vp2.data_start+e['body']; seen=set()
    for off in offs:
        sp=body+off+8
        if sp in seen: continue
        seen.add(sp)
        if not(body<sp<=len(vp2.data)-24): continue
        i=sp;n=len(vp2.data)
        while i+2<=n:
            x,y=vp2.data[i],vp2.data[i+1]
            if x==0 and y==0: break
            if (x<<8|y) in CUR_SLOT.values(): left+=1
            i+=2
print("  残留旧槽: %d (应0)" % left)
assert left==0
print("\n✓ v422 构建完成（候选，未部署）")
print("  新槽:", NEW)