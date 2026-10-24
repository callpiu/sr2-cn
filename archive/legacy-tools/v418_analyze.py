"""v418 综合核查：
  1) vf3 真实结构（显式 U/V 数组 + 0xD0 记录），确认追加字槽可否零改图集；
  2) juiced_CH.le_strings 用 2795 与 2838 两套字表分别解码，判定 OpenSpy 乱码根因；
  3) 徒/录/弹 三个坏字在全部 _CH le_strings 的出现次数与位置；
  4) 定位 双胞胎/双份/食物 double 串。
"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units, SHIFT

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC = os.path.join(GAME, "patch.vpp_pc")
v = Vpp(SRC)
print("patch md5:", hashlib.md5(v.data).hexdigest())

# ---------- charlist ----------
e_cl = v.find("charlist_CH", "txt")
nums = [int(x) for x in v.read(e_cl).decode('utf-8', 'replace').split()
        if x.strip().lstrip('-').isdigit()]
cl = nums[1:] if (nums and nums[0] == len(nums) - 1) else nums
N = len(cl)
print("charlist N =", N, " 首数:", nums[0])
CP2IDX = {c: i for i, c in enumerate(cl)}
def slotof(ch):
    i = CP2IDX.get(ord(ch))
    return None if i is None else i + SHIFT
for ch in "徒录弹建底床 ":
    print("  %s cp=0x%X idx=%s slot=%s" % (ch, ord(ch), CP2IDX.get(ord(ch)), slotof(ch)))

# ---------- vf3 结构 ----------
vf3 = bytearray(v.read(v.find("fnt_chinese", "vf3_pc")))
print("\n== vf3 基本信息 ==")
print("  len =", len(vf3), " magic =", vf3[:4])
n3 = struct.unpack_from('<I', vf3, 0x08)[0]
print("  count@0x08 =", n3)
print("  头部 0x00..0x30:", vf3[:0x30].hex())
# 0xD0 处第一条记录（idx0）
print("  0xD0 记录(idx0) 16B:", vf3[0xD0:0xD0+16].hex())
# idx 1058 (徒) 记录
o_徒 = 0xD0 + 1058 * 16
print("  0xD0+1058*16 (徒) 16B:", vf3[o_徒:o_徒+16].hex(),
      struct.unpack_from('<IIII', vf3, o_徒))
# 试 U@0xAF6C V@0xDB18
try:
    U = list(struct.unpack_from('<%di' % n3, vf3, 0xAF6C))
    V = list(struct.unpack_from('<%di' % n3, vf3, 0xDB18))
    print("  U@0xAF6C[1058]=", U[1058], " V@0xDB18[1058]=", V[1058])
    print("  U@0xAF6C[0]=", U[0], " V[0]=", V[0])
    # 0xD0 记录第三字段是否等于某 U/V？
    rec0 = struct.unpack_from('<IIII', vf3, 0xD0 + 1058*16)
    print("  徒记录=(spacing,byteWidth,offset,kerning)=", rec0)
    print("  -> 是否 offset==V[1058]? ", rec0[2] == V[1058], " spacing==U[1058]?", rec0[0]==U[1058])
except Exception as e:
    print("  U/V 解析失败:", e)

# 整体布局推断：0xD0 之后到 0xAF6C 有多少字节 = (0xAF6C-0xD0) = 用于记录？
print("  0xD0..0xAF6C 字节数 =", 0xAF6C - 0xD0, " = N*16?", 0xAF6C-0xD0 == n3*16)
print("  U 数组末 = 0xAF6C + n3*4 =", 0xAF6C + n3*4, " hex 0x%X" % (0xAF6C + n3*4))
print("  V 数组末 = 0xDB18 + n3*4 =", 0xDB18 + n3*4, " hex 0x%X" % (0xDB18 + n3*4))
print("  vf3 总长 0x%X" % len(vf3))

# ---------- juiced 解码 ----------
print("\n== juiced_CH.le_strings 解码 ==")
jp = os.path.join(GAME, "Mods", "JUICED - Strings", "juiced_CH.le_strings")
jb = open(jp, 'rb').read()
print("  juiced le_strings 大小:", len(jb), " magic:", jb[:4].hex())
b, c, oa, offs = file_offsets(jb)
print("  buckets=%d count=%d" % (b, c))

def decode_with(offsets_blob, clist, label):
    print("  --- 用 %s 字表解码 ---" % label)
    from sr2patch import CharList
    CL = CharList(clist)
    dd = offsets_blob
    n = len(dd)
    cnt = 0
    for off in dict.fromkeys(offs):
        if not (0 < off <= n - 10):
            continue
        u, end = read_units(dd, off + 8)
        if u is None:
            continue
        t = ""
        bad = False
        for vv, _ in u:
            if vv < 0x100:
                t += chr(vv)
            else:
                ch = CL.char(vv)
                if ch is None:
                    t += '\ufffd'
                    bad = True
                else:
                    t += ch
        cnt += 1
        print("    [%d] %r %s" % (off, t, " <<<越界" if bad else ""))
    print("  共 %d 条" % cnt)

# 2795 字表（patch 内）
decode_with(jb, cl, "2795(patch)")
# 2838 字表（第三方简体）
f2838 = r"F:\sr2-cn\_day_2026-10-07\04_规则与数据\字表_第三方简体_charlist_CH.txt"
c2838 = [int(l) for l in open(f2838, encoding='utf-8').read().split('\n') if l.strip().isdigit()]
print("  2838 字表条数:", len(c2838))
decode_with(jb, c2838, "2838(第三方)")

# ---------- 坏字出现次数 ----------
print("\n== 徒/录/弹 在全部 _CH le_strings 的出现 ==")
def decode_table(name, blob, clist):
    b, c, oa, offs = file_offsets(blob)
    out = []
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(blob) - 24):
            continue
        u, end = read_units(blob, off + 8)
        if u is None:
            continue
        t = "".join(chr(vv) if vv < 0x100 else (chr(clist[vv-SHIFT]) if 0 <= vv-SHIFT < len(clist) else '\ufffd') for vv, _ in u)
        out.append((off, t, [vv for vv, _ in u]))
    return out

target_slots = {slotof('徒'): '徒', slotof('录'): '录', slotof('弹'): '弹'}
for e in v.entries():
    nm = e['name']
    if 'CH' in nm and e['ext'] == 'le_strings' and nm not in ('charlist_CH',):
        blob = v.read(e)
        recs = decode_table(nm, blob, cl)
        hits = []
        for off, t, slots in recs:
            for s in slots:
                if s in target_slots:
                    hits.append((off, target_slots[s], t))
                    break
        if hits:
            print("  [%s] 命中 %d 条" % (nm, len(hits)))
            for off, ch, t in hits[:5]:
                print("      @0x%X %s : %r" % (off, ch, t))
            if len(hits) > 5:
                print("      ... 其余 %d 条略" % (len(hits)-5))

# ---------- 双胞胎/双份/食物 ----------
print("\n== 双胞胎/双份/食物串搜索 ==")
for e in v.entries():
    nm = e['name']
    if 'CH' in nm and e['ext'] == 'le_strings' and nm not in ('charlist_CH',):
        blob = v.read(e)
        recs = decode_table(nm, blob, cl)
        for off, t, slots in recs:
            if ('胞胎' in t) or ('双份' in t) or ('double' in t.lower()) or ('食物' in t and len(t) < 20):
                print("  [%s] @0x%X %r" % (nm, off, t))
