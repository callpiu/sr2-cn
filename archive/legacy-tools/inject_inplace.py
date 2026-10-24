"""inject_inplace.py -- 原地覆盖版对照实验（判定引擎是否无视 entry 重定向）

步骤:
  1. 从 .v532_before_exp.bak 恢复 patch.vpp_pc (干净 v532, entry->原地 v532 块)
  2. 用 rm.rebuild 生成「v532 内容 + 2 条测试串替换」的新 blob
  3. 新 blob 必须 <= v532 body 大小; 原地写入同一绝对偏移, 尾部补零到原大小
     => 入口字段 / 文件总长 / 目录 完全不动, 只有块内记录字节变化
  4. 回读校验 + md5
判读:
  重启后字幕变了 -> 引擎无视 entry 重定向(或定位方式另有机制), 以后一律原地写
  重启后字幕没变 -> 该 UI 根本不从 patch.vpp_pc 的 static_CH 读这条文本
"""
import sys, struct, shutil, os, hashlib
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp
import rebuild_mirror as rm

P   = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
BAK = P + '.v532_before_exp.bak'

def md5f(p): return hashlib.md5(open(p,'rb').read()).hexdigest()

# ---- 1. restore clean v532 ----
shutil.copy2(BAK, P)
print('restored', P, '<-', os.path.basename(BAK), ' md5 =', md5f(P))

vpp = Vpp(P)
rm.vpp = vpp
ent = vpp.find('static_CH', 'le_strings')
old_size = ent['size']
abs_off  = vpp.data_start + ent['body']
print('v532 static_CH: rel=%d abs=%d size=%d' % (ent['body'], abs_off, old_size))
assert abs_off == 48076800, 'unexpected abs offset!'

# ---- charlist ----
clbuf = vpp.read(vpp.find('charlist_CH', 'txt'))
text = clbuf.decode('ascii', 'replace')
end = text.find('//ENDOFFILE')
CPS = [int(x) for x in text[:end].split() if x.isdigit()]
CP2IDX = {cp: i for i, cp in enumerate(CPS)}

def encode(s):
    out = bytearray()
    for ch in s:
        cp = ord(ch)
        if cp < 0x80:
            out += struct.pack('>H', cp)
        else:
            out += struct.pack('>H', CP2IDX[cp] + 0x20)
    return bytes(out)

TEST = {
    0x84F287ED: '面包车耐久测试文本',      # REC1
    0x10AF1E62: '你的弟兄们需要你的保护',   # REC2
}

# ---- 2. rebuild blob = v532 content with 2 test strings ----
_orig = rm.ch_text_map
def patched(name):
    m = _orig(name)
    if name == 'static_CH':
        for h, s in TEST.items():
            m[h] = encode(s)
    return m
rm.ch_text_map = patched
new_blob, nb, count, _ = rm.rebuild('static_US', 'static_CH')
rm.ch_text_map = _orig
print('new blob: nb=%d count=%d size=%d  (v532 body size=%d)' % (nb, count, len(new_blob), old_size))
assert len(new_blob) <= old_size, 'new blob bigger than v532 body - cannot in-place!'

# ---- 3. in-place write: only bytes inside the body change ----
data = bytearray(open(P, 'rb').read())
data[abs_off : abs_off + len(new_blob)] = new_blob
pad = old_size - len(new_blob)
if pad:
    data[abs_off + len(new_blob) : abs_off + old_size] = b'\x00' * pad
assert len(data) == os.path.getsize(BAK), 'file length changed! %d vs %d' % (len(data), os.path.getsize(BAK))
open(P, 'wb').write(bytes(data))
print('in-place written, file length unchanged =', len(data))

# ---- 4. verify ----
v2 = Vpp(P)
e2 = v2.find('static_CH', 'le_strings')
assert (e2['body'], e2['size']) == (ent['body'], ent['size']), 'entry fields changed!'
d = v2.read(e2)
magic, ver, nb2, count2 = struct.unpack_from('<IHHI', d, 0)
A0 = 12 + nb2 * 8
ptrs = [struct.unpack_from('<I', d, A0 + i*4)[0] for i in range(count2)]
def dec(off):
    id1, id2 = struct.unpack_from('<HH', d, off)
    units = []; o = off + 4
    while True:
        u = struct.unpack_from('>H', d, o)[0]; o += 2
        if u == 0: break
        units.append(u)
    h = (id1 << 16) | id2
    s = ''
    for u in units:
        s += chr(u) if u < 0x80 else chr(CPS[u - 0x20]) if 0 <= u - 0x20 < len(CPS) else '?'
    return h, s
byh = dict(dec(off) for off in ptrs)
for h, s in TEST.items():
    got = byh.get(h)
    print('VERIFY %08X -> %r  %s' % (h, got, 'OK' if got == s else 'MISMATCH!'))
# spot check an unrelated record
h2, s2 = dec(ptrs[0])
print('spot check ptr[0]: %08X %r' % (h2, s2[:20]))
print('count=%d nb=%d  total records=%d' % (count2, nb2, len(ptrs)))
print('FINAL md5 =', md5f(P))

# ---- bonus: does loose DLC table contain the homies text? ----
import glob
pats = {
    '弟兄们': encode('弟兄们'),
    '免遭袭击': encode('免遭袭击'),
}
for f in [r'G:\SteamLibrary\steamapps\common\Saints Row 2\DLC\Text\dlc_ch.le_strings'] + \
         glob.glob(r'G:\SteamLibrary\steamapps\common\Saints Row 2\Mods\**\*.le_strings', recursive=True):
    if os.path.isfile(f):
        b = open(f, 'rb').read()
        hits = [k for k, p in pats.items() if p in b]
        print('DLC/Mods check:', os.path.basename(f), len(b), 'hits:', hits or 'none')
