"""diag26.py -- 把文件里所有【中文】static 块的目标记录就地改成无格式码测试串

引擎读的 static_CH 不是 entry 指向的块(实测读 29353344 等历史/原始块), 所以此前改不生效。
数据本身正确(你的弟兄们需要你的保护), 屏幕乱码是 [format][color] 标记导致解析错位。
策略: 枚举所有 static 量级块, 解码目标 hash, 仅对【含 CJK 的中文块】就地改文本
  REC1 -> 面包车耐久测试文本  (对照: 已知好字, 无格式码)
  REC2 -> 你的弟兄们需要你的保护 (测: 原文汉字, 无格式码)
不动 id / 记录总长, 仅替换 units+终止符。
"""
import sys, struct, os, hashlib
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp

P = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
data = bytearray(open(P, 'rb').read())
print('file size =', len(data))

vpp = Vpp(P)
clbuf = vpp.read(vpp.find('charlist_CH', 'txt'))
text = clbuf.decode('ascii', 'replace'); end = text.find('//ENDOFFILE')
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

def parse(base):
    if base + 12 > len(data): return None
    magic, ver, nb, count = struct.unpack_from('<IHHI', data, base)
    if magic != 0xA84C7F73: return None
    if not (1 <= nb <= 8192 and 1000 <= count <= 13000): return None
    A0 = 12 + nb * 8
    if A0 + count * 4 > len(data) - base: return None
    ptrs = [struct.unpack_from('<I', data, base + A0 + k * 4)[0] for k in range(count)]
    return (nb, count, A0, ptrs)

def decode(rec_abs):
    o = rec_abs + 4; s = ''; g = 0
    while o + 2 <= len(data) and g < 4000:
        u = struct.unpack_from('>H', data, o)[0]; o += 2; g += 1
        if u == 0: break
        s += chr(u) if u < 0x80 else chr(CPS[u - 0x20]) if 0 <= u - 0x20 < len(CPS) else '?'
    return s

def is_cjk(s):
    return any('\u2e80' <= c <= '\u9fff' or '\uff00' <= c <= '\uffef' for c in s)

n_edit = 0
for base in occ:
    r = parse(base)
    if not r: continue
    nb, count, A0, ptrs = r
    for p in ptrs:
        ra = base + p
        if ra + 4 > len(data): continue
        id1, id2 = struct.unpack_from('<HH', data, ra)
        h = (id1 << 16) | id2
        if h not in TARGETS: continue
        cur = decode(ra)
        if not is_cjk(cur):
            continue  # 只改中文块
        newunits = enc(TARGETS[h])
        # 原记录长度
        o = ra + 4; olen = 0; g = 0
        while o + 2 <= len(data) and g < 4000:
            u = struct.unpack_from('>H', data, o)[0]; o += 2; olen += 2; g += 1
            if u == 0: break
        orig_len = 4 + olen
        payload = struct.pack('<HH', id1, id2) + newunits + b'\x00\x00'
        if len(payload) > orig_len:
            print('!! %08X blob@%d rec@%d SKIP new>orig' % (h, base, ra)); continue
        data[ra:ra + len(payload)] = payload
        n_edit += 1
        print('EDITED %08X blob@%d rec@%d (nb=%d) %r -> %r' % (h, base, ra, nb, cur, TARGETS[h]))

open(P, 'wb').write(bytes(data))
print('written. total edits =', n_edit, ' md5 =', hashlib.md5(bytes(data)).hexdigest())

# 复验: 所有中文块的目标记录现在都应读成测试串
print('--- re-verify (Chinese blobs) ---')
for base in occ:
    r = parse(base)
    if not r: continue
    nb, count, A0, ptrs = r
    for p in ptrs:
        ra = base + p
        if ra + 4 > len(data): continue
        id1, id2 = struct.unpack_from('<HH', data, ra)
        h = (id1 << 16) | id2
        if h in TARGETS:
            cur = decode(ra)
            if is_cjk(cur):
                print('blob@%d nb=%d %08X -> %r' % (base, nb, h, cur))
