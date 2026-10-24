"""v418 构建：修复 HUD/地图/武器名/登录 三处坏字（徒/录/弹）的渲染错位。

根因：部分控件走 char = charlist[slot-0x40]（多减 0x20），导致
  徒(slot1090)->建 / 录(slot1077)->底 / 弹(slot1073)->床。
  该 bug 对任何字符都成立，改名/追加字槽均无效；vf3 偏移被 EXE 硬编码引用，不能增删条目。

安全修法（已验证字表有 301 个从未被引用的空闲索引，且 196 对 (X,X+32) 都空闲）：
  选空闲对 (X, X+32)，把 charlist[X]、charlist[X+32]、vf3[U/V][X]、vf3[U/V][X+32]、
  vf3<IIII>[X]、vf3<IIII>[X+32] 全部重指成目标字（徒/录/弹）的字形/码点。
  目标串的字槽由 旧->新：徒1090->2288 / 录1077->2325 / 弹1073->2616。
  正确路径 slot-0x20 = X+32 -> 目标字；坏路径 slot-0x40 = X -> 目标字。两条路径都显示正确字，
  且不牺牲任何真实汉字、不改 vf3 布局（只改数组值）、不动 4MB 图集。
  已验证：DLC/juiced/patch 内均不引用这 6 个索引或 3 个新槽 -> 零冲突。

另：双胞胎/OpenSpy 见脚本末尾说明（本次不处理，留待后续）。
"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, SHIFT

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC  = os.path.join(GAME, "patch.vpp_pc")
BAK  = SRC + ".v417bak"
OUT  = r"F:\sr2-cn\_fix_candidates\patch_v418.vpp_pc"
V417_MD5 = "24920a5c9f3b7b5daba33b402989bb03"

# ---- 映射 ----
OLD2NEW = {1090: 2288, 1077: 2325, 1073: 2616}          # 旧槽 -> 新槽
NEW2CH  = {2288: '徒', 2325: '录', 2616: '弹'}          # 新槽 -> 字（用于校验）
# 重指索引(X) -> (目标字, 源字形索引src)；X 与 X+0x20 成对
REP = {
    2224: ('徒', 1058), 2256: ('徒', 1058),
    2261: ('录', 1045), 2293: ('录', 1045),
    2552: ('弹', 1041), 2584: ('弹', 1041),
}

# ---- 备份（存在则校验后跳过）----
if os.path.exists(BAK):
    m = hashlib.md5(open(BAK, 'rb').read()).hexdigest()
    assert m == V417_MD5, "已有 .v417bak 但 md5 不匹配 (%s)，中止以防覆盖" % m
    print("✓ 备份已存在且 md5 正确，跳过复制")
else:
    import shutil
    shutil.copy2(SRC, BAK)
    print("✓ 备份 v417 ->", BAK)

v = Vpp(SRC)
orig_md5 = hashlib.md5(v.data).hexdigest()
print("v417 md5:", orig_md5, "(应==", V417_MD5, ")")
assert orig_md5 == V417_MD5, "源文件不是 v417，中止"

# ---- 1) charlist：字节级行替换（5位->5位，长度不变，保留 LF）----
e_cl = v.find("charlist_CH", "txt")
raw_cl = v.read(e_cl)
segs = raw_cl.split(b'\n')
for X, (ch, src) in REP.items():
    segs[X] = str(ord(ch)).encode('ascii')
new_body = b'\n'.join(segs)
assert len(new_body) == len(raw_cl), "charlist 长度变化 %d -> %d" % (len(raw_cl), len(new_body))
cl_off = v.data_start + e_cl['body']
v.data[cl_off:cl_off + len(new_body)] = new_body
print("✓ charlist 重指 6 行:", {X: NEW2CH[2288] if X in (2224,2256) else (NEW2CH[2325] if X in (2261,2293) else NEW2CH[2616]) for X in REP})

# ---- 2) vf3：原地改 U/V + <IIII>（只改值，不动偏移）----
e_vf3 = v.find("fnt_chinese", "vf3_pc")
vf3_off = v.data_start + e_vf3['body']
n3 = struct.unpack_from('<I', v.data, vf3_off + 0x08)[0]
assert n3 == 2795, n3
def get_src(src):
    U = struct.unpack_from('<i', v.data, vf3_off + 0xAF6C + src*4)[0]
    V = struct.unpack_from('<i', v.data, vf3_off + 0xDB18 + src*4)[0]
    rec = struct.unpack_from('<IIII', v.data, vf3_off + 0xD0 + src*16)
    return U, V, rec
src_cache = {}
for X, (ch, src) in REP.items():
    if src not in src_cache:
        src_cache[src] = get_src(src)
for X, (ch, src) in REP.items():
    U, V, rec = src_cache[src]
    struct.pack_into('<i', v.data, vf3_off + 0xAF6C + X*4, U)
    struct.pack_into('<i', v.data, vf3_off + 0xDB18 + X*4, V)
    struct.pack_into('<IIII', v.data, vf3_off + 0xD0 + X*16, *rec)
print("✓ vf3 重指 6 个字形 (U/V/<IIII>) @索引", sorted(REP))

# ---- 3) 字符串：_CH le_strings 全局替换旧槽 -> 新槽（只在 slot 流内，1:1 等长）----
def read_slots(buf, pos):
    """从 buf 的 pos 处读取 0x0000 终止的 uint16-BE slot 流，返回 list[int]；遇界外返回 None。"""
    n = len(buf)
    out = []
    i = pos
    while i + 2 <= n:
        b0, b1 = buf[i], buf[i + 1]
        if b0 == 0 and b1 == 0:
            return out
        out.append((b0 << 8) | b1)
        i += 2
    return None

changed_recs = 0
total_recs = 0
tables_touched = {}
for e in v.entries():
    nm = e['name']
    if 'CH' not in nm or e['ext'] != 'le_strings':
        continue
    bc, count, oa, offs = file_offsets(v.read(e))
    body_off = v.data_start + e['body']
    # 按物理偏移 sp 去重：同一 record（可能被多个 offset 别名引用）只处理一次
    seen_sp = set()
    for off in offs:
        sp = body_off + off + 8
        if sp in seen_sp:
            continue
        seen_sp.add(sp)
        if not (body_off < sp <= len(v.data) - 24):
            continue
        vals = read_slots(v.data, sp)
        if not vals:
            continue
        if not any(x in OLD2NEW for x in vals):
            continue
        total_recs += 1
        newvals = [OLD2NEW.get(x, x) for x in vals]
        assert len(newvals) == len(vals)
        for j, sv in enumerate(newvals):
            struct.pack_into('>H', v.data, sp + j*2, sv)
        # 写后回读校验
        cur2 = struct.unpack_from('>%dH' % len(newvals), v.data, sp)
        if list(cur2) != newvals:
            print("  !! 写后回读不一致 @%s off=0x%X sp=0x%X" % (nm, off, sp))
            raise SystemExit(1)
        changed_recs += 1
        tables_touched[nm] = tables_touched.get(nm, 0) + 1
print("✓ 字符串替换：改动 %d 条记录（命中替换 %d）" % (changed_recs, total_recs))
print("  各表改动:", tables_touched)

# ---- 4) 保存候选 ----
os.makedirs(os.path.dirname(OUT), exist_ok=True)
v.save(OUT)
new_md5 = hashlib.md5(open(OUT, 'rb').read()).hexdigest()
print("✓ 写出候选:", OUT)
print("  md5:", new_md5, " 大小:", len(v.data))

# ---- 5) 全量校验 ----
print("\n=== 校验 ===")
v2 = Vpp(OUT)
# 5a) charlist 重指正确
e_cl2 = v2.find("charlist_CH", "txt")
raw2 = v2.read(e_cl2)
segs2 = raw2.decode('utf-8').split('\n')
cl_map = {i: int(segs2[i]) for i in range(len(segs2)) if segs2[i].strip().isdigit()}
for X, (ch, src) in REP.items():
    assert cl_map.get(X) == ord(ch), "charlist[%d] 未改 %s vs %s" % (X, cl_map.get(X), ord(ch))
print("  [✓] charlist 6 行重指正确")
# 5b) vf3 重指正确
e_vf3_2 = v2.find("fnt_chinese", "vf3_pc")
vo2 = v2.data_start + e_vf3_2['body']
for X, (ch, src) in REP.items():
    U0, V0, r0 = src_cache[src]
    Ux = struct.unpack_from('<i', v2.data, vo2 + 0xAF6C + X*4)[0]
    Vx = struct.unpack_from('<i', v2.data, vo2 + 0xDB18 + X*4)[0]
    rx = struct.unpack_from('<IIII', v2.data, vo2 + 0xD0 + X*16)
    assert (Ux, Vx) == (U0, V0) and rx == r0, "vf3[%d] 未重指" % X
print("  [✓] vf3 6 字形重指正确")
# 5c) 双路径解码验证：新槽在正确/坏路径都得到目标字
print("  [校验] 新槽双路径：", end=" ")
for ns, ch in NEW2CH.items():
    c_ok = cl_map.get(ns - SHIFT) == ord(ch)      # 正确路径 slot-0x20
    b_ok = cl_map.get(ns - 0x40) == ord(ch)       # 坏路径 slot-0x40
    print("%s 正确=%s 坏=%s" % (ch, c_ok, b_ok), end="  ")
    assert c_ok and b_ok, "%s 双路径失败" % ch
print()
# 5d) 全量扫描：旧槽应清零，新槽应存在且双路径正确
leftover_old = 0
new_present = {ns: 0 for ns in NEW2CH}
for e in v2.entries():
    nm = e['name']
    if 'CH' not in nm or e['ext'] != 'le_strings':
        continue
    b = v2.read(e)
    bc, count, oa, offs = file_offsets(b)
    body_off = v2.data_start + e['body']
    seen_sp = set()
    for off in offs:
        sp = body_off + off + 8
        if sp in seen_sp:
            continue
        seen_sp.add(sp)
        if not (0 < off <= len(b) - 24):
            continue
        vals = read_slots(b, off + 8)
        if not vals:
            continue
        for x in vals:
            if x in OLD2NEW:
                leftover_old += 1
            if x in new_present:
                new_present[x] += 1
print("  [校验] 残留旧槽计数:", leftover_old, "(应为 0)")
assert leftover_old == 0, "仍有旧槽未被替换"
print("  [校验] 新槽出现次数:", new_present, "(应 >0)")
assert all(n > 0 for n in new_present.values())
print("  [✓] 全量校验完成，v418 构建成功（候选，未部署）")
print("\n★ 部署：确认候选无误后，将 OUT 复制到游戏目录覆盖 patch.vpp_pc（已备份 v417bak）")
