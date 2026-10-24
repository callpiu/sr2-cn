"""v420：把 platform_pc_CH 里 9 条旧 GameSpy 汉化串的 'GameSpy' 改为 'OpenSpy'。

注意：
- 'GameSpy'(7 ASCII) -> 'OpenSpy'(7 ASCII) 等长，ASCII 槽值直接改，零风险。
- 中文集（'输入 GameSpy 密码'）里 GameSpy 是 ASCII，替换后总长不变 ⇒ 完美等长。
先统计全部含 GameSpy 的 CH 记录，逐一核对。"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC  = os.path.join(GAME, "patch.vpp_pc")
BAK  = SRC + ".v419bak"
OUT  = r"F:\sr2-cn\_fix_candidates\patch_v420.vpp_pc"

v = Vpp(SRC)
e_cl = v.find("charlist_CH", "txt")
cl_lines = v.read(e_cl).decode('utf-8').split('\n')
S = {i+0x20: int(s) for i, s in enumerate(cl_lines) if s.strip().isdigit()}

def dec(sl):
    o=[]
    for s in sl:
        if s < 0x100: o.append(chr(s))
        else:
            cp = S.get(s); o.append(chr(cp) if cp else '<?%d>' % s)
    return ''.join(o)

GS = [ord(c) for c in "GameSpy"]          # 71,97,109,101,83,112,121
OS_ = [ord(c) for c in "OpenSpy"]         # 79,112,101,110,83,112,121

print("=== 扫描所有 _CH le_strings 中含 'GameSpy' 的记录 ===")
hits = []
for e in v.entries():
    if e['ext'] != 'le_strings' or '_CH' not in e['name']: continue
    b = v.read(e)
    try: bc, c, oa, offs = file_offsets(b)
    except: continue
    body_off = v.data_start + e['body']
    seen = set()
    for off in offs:
        sp = body_off + off + 8
        if sp in seen: continue
        seen.add(sp)
        if not (body_off < sp <= len(v.data) - 24): continue
        # 读 slots
        i = sp; n = len(v.data); sl = []
        while i + 2 <= n:
            x, y = v.data[i], v.data[i+1]
            if x == 0 and y == 0: break
            sl.append((x << 8) | y); i += 2
        if not sl: continue
        # 找 GameSpy 连续 7 槽
        for k in range(len(sl) - 6):
            if sl[k:k+7] == GS:
                hits.append((e['name'], off, sp, sl, k))
                break

print("共 %d 条含 GameSpy:\n" % len(hits))
for name, off, sp, sl, k in hits:
    print("  [%s] @0x%X  GameSpy起始位=%d" % (name, off, k))
    print("      %r" % dec(sl)[:110])

# 备份
if not os.path.exists(BAK):
    import shutil
    shutil.copy2(SRC, BAK)
    print("\n✓ 备份 v419 ->", BAK)
else:
    m = hashlib.md5(open(BAK,'rb').read()).hexdigest()
    print("\n备份已存在 md5=", m)

# ---- 等长替换 GameSpy -> OpenSpy ----
changed = 0
for name, off, sp, sl, k in hits:
    p = sp + k*2
    for j, ch in enumerate(OS_):
        cur = struct.unpack_from('>H', v.data, p + j*2)[0]
        assert cur == GS[j], (name, off, j, cur)
        struct.pack_into('>H', v.data, p + j*2, ch)
    changed += 1

print("\n✓ 替换 GameSpy->OpenSpy: %d 条（全部等长，ASCII 槽直改）" % changed)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
v.save(OUT)
print("✓ 写出:", OUT, " md5:", hashlib.md5(open(OUT,'rb').read()).hexdigest())

# ---- 校验 ----
v2 = Vpp(OUT)
print("\n=== 校验 ===")
assert v2.data_start == v.data_start
n_changed = 0; n_left = 0
for e in v2.entries():
    if e['ext'] != 'le_strings' or '_CH' not in e['name']: continue
    b = v2.read(e)
    try: bc, c, oa, offs = file_offsets(b)
    except: continue
    body_off = v2.data_start + e['body']
    seen = set()
    for off in offs:
        sp = body_off + off + 8
        if sp in seen: continue
        seen.add(sp)
        if not (body_off < sp <= len(v2.data) - 24): continue
        i = sp; n = len(v2.data); sl = []
        while i + 2 <= n:
            x, y = v2.data[i], v2.data[i+1]
            if x == 0 and y == 0: break
            sl.append((x << 8) | y); i += 2
        if not sl: continue
        for k2 in range(len(sl) - 6):
            if sl[k2:k2+7] == OS_:
                n_changed += 1
            if sl[k2:k2+7] == GS:
                n_left += 1
print("  含 OpenSpy 的记录段: %d" % n_changed)
print("  残留 GameSpy 段:     %d (应为0)" % n_left)
assert n_left == 0
# 打印几条确认
for e in v2.entries():
    if e['ext'] != 'le_strings' or '_CH' not in e['name']: continue
    b = v2.read(e)
    try: bc, c, oa, offs = file_offsets(b)
    except: continue
    body_off = v2.data_start + e['body']
    seen=set(); shown=0
    for off in offs:
        sp = body_off + off + 8
        if sp in seen: continue
        seen.add(sp)
        if not (body_off < sp <= len(v2.data) - 24): continue
        i=sp; n=len(v2.data); sl=[]
        while i+2<=n:
            x,y=v2.data[i],v2.data[i+1]
            if x==0 and y==0: break
            sl.append((x<<8)|y); i+=2
        if not sl: continue
        for k2 in range(len(sl)-6):
            if sl[k2:k2+7]==OS_:
                print("    %r"%dec(sl)[:100]); shown+=1; break
        if shown>=9: break
print("\n✓ v420 构建完成（候选，未部署）")