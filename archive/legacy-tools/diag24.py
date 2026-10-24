"""diag24.py -- 定位并就地改写文件里所有含目标串的 le_strings 记录副本 (健壮版)

引擎不跟随 entry 重定向, 读的是 v532 遗留/原始的 static_CH 块。
扫描所有 magic=0xA84C7F73, 用「下一个 magic 位置」作为块边界剔除假阳性,
解析指针数组, 找出 hash=0x84F287ED/0x10AF1E62 的记录绝对偏移, 在原位把文本
替换成测试串 (id 不变, 仅替换 units+终止符), 不动记录总长。
"""
import sys, struct, os, hashlib
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp

P = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
data = bytearray(open(P, 'rb').read())
print('file size =', len(data))

vpp = Vpp(P)
clbuf = vpp.read(vpp.find('charlist_CH', 'txt'))
text = clbuf.decode('ascii', 'replace')
end = text.find('//ENDOFFILE')
CPS = [int(x) for x in text[:end].split() if x.isdigit()]
CP2IDX = {cp: i for i, cp in enumerate(CPS)}

def enc(s):
    o = bytearray()
    for ch in s:
        cp = ord(ch)
        o += struct.pack('>H', cp if cp < 0x80 else CP2IDX[cp] + 0x20)
    return bytes(o)

TARGETS = {0x84F287ED: '面包车耐久测试文本',
           0x10AF1E62: '你的弟兄们需要你的保护'}
MAGIC = struct.pack('<I', 0xA84C7F73)

occ = []
i = 0
while True:
    j = data.find(MAGIC, i)
    if j < 0: break
    occ.append(j); i = j + 1
print('magic occurrences:', len(occ), [hex(o) for o in occ[:20]])

def parse_blob(base):
    if base + 12 > len(data): return None
    magic, ver, nb, count = struct.unpack_from('<IHHI', data, base)
    if magic != 0xA84C7F73: return None
    if not (1 <= nb <= 8192 and 1 <= count <= 200000): return None
    A0 = 12 + nb * 8
    if A0 + count * 4 > len(data) - base: return None
    ptrs = [struct.unpack_from('<I', data, base + A0 + k * 4)[0] for k in range(count)]
    nxt = next((o for o in occ if o > base), len(data))
    bound = nxt - base
    if not ptrs: return None
    if max(ptrs) + 4096 > bound:
        return None
    # 抽样解码前 3 条, 必须都能在 <=200 units 内遇到 0x0000 终止
    for k in range(min(3, count)):
        ra = base + ptrs[k]
        if ra + 4 > nxt: return None
        o = ra + 4; n = 0
        while o + 2 <= nxt and n < 200:
            u = struct.unpack_from('>H', data, o)[0]; o += 2; n += 1
            if u == 0: break
        else:
            return None
    return (nb, count, A0, ptrs, bound)

found = {}
for base in occ:
    r = parse_blob(base)
    if not r: continue
    nb, count, A0, ptrs, bound = r
    for p in ptrs:
        ra = base + p
        if ra + 4 > len(data): continue
        id1, id2 = struct.unpack_from('<HH', data, ra)
        h = (id1 << 16) | id2
        if h in TARGETS:
            found.setdefault(h, []).append((base, ra, nb, count))
            print('FOUND %08X  blob@%d  rec@%d  nb=%d count=%d' % (h, base, ra, nb, count))

print('per-hash copies:', {hex(k): len(v) for k, v in found.items()})

n_edit = 0
for h, recs in found.items():
    newunits = enc(TARGETS[h])
    id1 = (h >> 16) & 0xFFFF
    id2 = h & 0xFFFF
    for (base, ra, nb, count) in recs:
        o = ra + 4; olen = 0; guard = 0
        while o + 2 <= len(data) and guard < 4000:
            u = struct.unpack_from('>H', data, o)[0]; o += 2; olen += 2; guard += 1
            if u == 0: break
        orig_len = 4 + olen
        payload = struct.pack('<HH', id1, id2) + newunits + b'\x00\x00'
        if len(payload) > orig_len:
            print('!! %08X rec@%d new(%d)>orig(%d) SKIP' % (h, ra, len(payload), orig_len))
            continue
        data[ra:ra + len(payload)] = payload
        n_edit += 1
        print('EDITED %08X rec@%d orig_len=%d new_len=%d' % (h, ra, orig_len, len(payload)))

open(P, 'wb').write(bytes(data))
print('written. edits=%d  md5=%s' % (n_edit, hashlib.md5(bytes(data)).hexdigest()))

# 复验
def dec(at):
    o = at + 4; s = ''; guard = 0
    while o + 2 <= len(data) and guard < 4000:
        u = struct.unpack_from('>H', data, o)[0]; o += 2; guard += 1
        if u == 0: break
        s += chr(u) if u < 0x80 else chr(CPS[u - 0x20]) if 0 <= u - 0x20 < len(CPS) else '?'
    return s
print('--- re-verify ---')
for base in occ:
    r = parse_blob(base)
    if not r: continue
    nb, count, A0, ptrs, bound = r
    for p in ptrs:
        ra = base + p
        if ra + 4 > len(data): continue
        id1, id2 = struct.unpack_from('<HH', data, ra)
        h = (id1 << 16) | id2
        if h in TARGETS:
            print('blob@%d rec@%d -> %r' % (base, ra, dec(ra)))
