"""v419 修正版②：按【原始槽位数】重建 juiced_CH.le_strings。

★上一版（814B）的问题：把 rec10 从 'OpenSpy'(7槽) 改成 '正在登录 OpenSpy'(12槽)，
  而 Juiced 会自己在前后拼接 ⇒ 屏幕显示成 "璃傲正在登录 OpenSpy"（前缀是 Juiced 加的）。
  ⇒ 【必须保持 Juiced 的拼接骨架】：每条只提供"片段"，不能写成完整句子。

★ 正确策略：
  1) 头部、桶表原字节照抄（v419 崩溃教训）
  2) 保持 Juiced 原有拼接结构：`<自定义片段> OpenSpy <自定义片段>`
     只把其中的【越界槽位 <?NNNN>】换成合法中文，长度可略增但必须 ≤ 原版可接受范围。
     —— 更保守：长度严格等于原槽位数。
  3) rec11 的损坏 offset(0xA5EDEEAF) 原样保留，绝不"修正"

★ 各条目标（长度=原槽位数）：
  rec10 (7槽)  'OpenSpy'                     → 保持 'OpenSpy'（已是合法 ASCII，无需改）
  rec8  (14槽) 'OpenSpy E-mail'              → 'OpenSpy 电子邮箱'？ 需算长度
  ...
"""
import struct, os, sys, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC  = os.path.join(GAME, "Mods", "JUICED - Strings", "juiced_CH.le_strings.orig762.bak")
OUT  = r"F:\sr2-cn\_fix_candidates\juiced_CH.v419fix.le_strings"

v = Vpp(os.path.join(GAME, "patch.vpp_pc"))
cl_lines = v.read(v.find("charlist_CH", "txt")).decode('utf-8').split('\n')
cl = [int(s) for s in cl_lines if s.strip().isdigit()]
c2s, S = {}, {}
for i, cp in enumerate(cl):
    if cp >= 0x100: c2s.setdefault(chr(cp), i + 0x20)
    S[i + 0x20] = cp

data = bytearray(open(SRC, 'rb').read())
magic, ver, buckets, count = struct.unpack_from('<IHHI', data, 0)
HDR, BT = 16, buckets * 8
off_at = HDR + BT
BUCKET_ORIG = bytes(data[HDR:HDR+BT])
offs = [struct.unpack_from('<I', data, off_at + k*4)[0] for k in range(count)]

def read_slots(buf, pos):
    n=len(buf); out=[]; i=pos
    while i+2<=n:
        x,y=buf[i],buf[i+1]
        if x==0 and y==0: return out
        out.append((x<<8)|y); i+=2
    return out
def dec(sl):
    o=[]
    for s in sl:
        if s<0x100: o.append(chr(s))
        else:
            cp=S.get(s); o.append(chr(cp) if cp else '<?%d>'%s)
    return ''.join(o)
def encode(t):
    out=[]
    for ch in t:
        cp=ord(ch)
        if cp<0x100: out.append(cp)
        else:
            s=c2s.get(ch)
            if s is None: raise ValueError("字表缺字 %r"%ch)
            out.append(s)
    return out

recs=[]
for off in offs:
    if off+8 > len(data):
        recs.append((off,None,None)); continue
    h=struct.unpack_from('<Q',data,off)[0]
    recs.append((off,h,read_slots(data,off+8)))

OP=[79,112,101,110,83,112,121]   # "OpenSpy"

# ★ 目标：保持【Juiced 拼接骨架】——片段形式，不写成完整句子。
#   允许变长（Juiced 按 Label 取片段，前后由它自己拼）。
#   关键禁区：rec10 只能是"片段"，不能写成 '正在登录 OpenSpy' 这种完整句，
#   否则 Juiced 再拼前缀 ⇒ 屏幕上出现 "璃傲正在登录 OpenSpy"。
TARGETS = {
 0xC6EC1896: "OpenSpy ID",
 0x2840CF1D: "重输 OpenSpy 密码",
 0x4BFF620D: "你已与 OpenSpy 断开",
 0x2E971EEE: "OpenSpy 连接丢失。\n返回主菜单",
 0x70F326B6: "OpenSpy 名称",
 0xD3305375: "mail",
 0x54559450: "好友：%i/%i，获得[format][color:green]$%i[/format]，%ls级表现",
 0x55709960: "OpenSpy 密码",
 0x3E2123B9: "OpenSpy 电子邮箱",
 0xDECC9455: "重输 OpenSpy 密码",
 0x1FE19653: "OpenSpy",          # ★保持纯片段
}

print("=== 编码校验（字表齐否 / 骨架检查）===")
plan = []; bad = False
for k, (off, h, sl) in enumerate(recs):
    if h is None: continue
    lo = h & 0xffffffff
    if lo not in TARGETS: continue
    t = TARGETS[lo]
    miss = [ch for ch in t if ord(ch) >= 0x100 and ch not in c2s]
    if miss: bad = True
    print(" rec%-2d lo=0x%08X 原%2d槽 -> %2d槽 %s %r%s" % (
        k, lo, len(sl), len(t), "OK" if not miss else "★缺字", t,
        ("  缺:%r" % miss) if miss else ""))
    plan.append((k, off, h, t))
if bad:
    print("\n★ 有缺字，未写入。"); sys.exit(1)

# ---- 构建：桶表/头部照抄，重排 offset 表 + 数据区 ----
HDR_SZ = 16
data_start = HDR_SZ + BT + count * 4
new, sizes, new_offs = [], [], []
cur = data_start
for k, (off, h, sl) in enumerate(recs):
    if h is None:
        # ★ 损坏记录：offset 原样保留（不重排），不占数据区
        new.append((h, None)); new_offs.append(off); sizes.append(0)
        continue
    lo = h & 0xffffffff
    if lo in TARGETS:
        sl = encode(TARGETS[lo])
    new.append((h, sl)); new_offs.append(cur)
    sizes.append(8 + len(sl)*2 + 2)
    cur += sizes[-1]

out = bytearray(cur)
struct.pack_into('<IHHI', out, 0, magic, ver, buckets, count)
out[HDR:HDR+BT] = BUCKET_ORIG
for k, noff in enumerate(new_offs):
    struct.pack_into('<I', out, off_at + k*4, noff)
for (h, sl), noff in zip(new, new_offs):
    if h is None or sl is None: continue
    struct.pack_into('<Q', out, noff, h)
    p = noff + 8
    for s in sl:
        struct.pack_into('>H', out, p, s); p += 2
    struct.pack_into('>H', out, p, 0)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'wb').write(out)
print("\n✓ 写出 %s" % OUT)
print("  size %d -> %d  md5=%s" % (len(data), len(out), hashlib.md5(out).hexdigest()))

print("\n=== 校验 ===")
print("  头部一致:", bytes(out[:HDR]) == bytes(data[:HDR]))
print("  桶表一致:", bytes(out[HDR:HDR+BT]) == BUCKET_ORIG)
print("  rec11 offset 原样:", hex(new_offs[11]))
tot = 0
for k, (off, h, sl) in enumerate(recs):
    if h is None:
        print("  rec%-2d offset=0x%X 原样保留" % (k, new_offs[k])); continue
    noff = new_offs[k]
    ns = read_slots(out, noff + 8)
    nb = sum(1 for s in ns if s >= 0x100 and S.get(s) is None)
    tot += nb
    print("  rec%-2d 越界=%d %r" % (k, nb, dec(ns)[:55]))
print("\n  总越界槽: %d" % tot)