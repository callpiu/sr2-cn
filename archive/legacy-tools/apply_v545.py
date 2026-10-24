# -*- coding: utf-8 -*-
"""
v545：修正Freckle Bitch's 菜单的 3 处误译+ 补翻载具名 Swallow
全部是「等长或缩短」→ 尾部余量填 0000 提前终止，文件长度与表结构不变。
★★ 只改 static_CH.le_strings 及其【表外松散副本】，其它语言表零改动。
"""
import struct, hashlib, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

P = 'G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc'
BASE = 'c91a4ff4e2fab9a3522d4724922791d7'

CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))
IDX = {}
for i, cp in enumerate(CL):
    IDX.setdefault(cp, i)

def S(ch):
    assert ord(ch) in IDX, '字表缺字: %s' % ch
    return IDX[ord(ch)] + 0x20

def pack(s):
    return b''.join(struct.pack('>H', S(c)) for c in s)

buf = bytearray(open(P, 'rb').read())
assert hashlib.md5(bytes(buf)).hexdigest() == BASE, 'baseline mismatch'
orig = bytes(buf)
orig_len = len(buf)

v = Vpp(P)
ds = v.data_start if hasattr(v, 'data_start') else 0x9000
ENT = {}
for e in v.entries():
    ENT[e['name'] + '.' + e['ext']] = (ds + e['body'], ds + e['body'] + e['size'])

def owner(pos):
    for nm, (a, b) in ENT.items():
        if a <= pos < b:
            return nm
    return None

def allowed(pos):
    nm = owner(pos)
    return nm is None or nm == 'static_CH.le_strings'

# (记录ID, 旧文本, 新文本, 依据)
#★ 按 32 位 ID 精确定位，绝不按文本搜全表！
#  「拳头」在表里有两条不同 ID：AA0A5EB8=The Fist(汉堡)要改；
#  B45D9039=Fist(别处) 是正确译名，不能碰。
RULES = [
    (0x7B506169, '大飞燕', '大可乐', "Big Swallow = 一杯可乐（说明:A styrofoam cup of cola）"),
    (0xAA0A5EB8, '拳头', '大堡',     'The Fist = 巨型汉堡（big-ass burger is huge）'),
    (0xDC924324, '鸡胸', '鸡块',     'Chicken Bazooms = 椭圆炸鸡块'),
    (0x8BC04EFE, 'Swallow', '燕子',  '载具名 Swallow'),
    # ★ 顺带补翻菜单里另外 3 个漏翻项（截图只看到 4 个，实际全菜单还有 3 个）
    (0xAE7B1522, "小 Gyro",   '小卷',  "Lil' Gyro = 一小块肉夹皮塔饼（现译留了英文）"),
    (0x52826B3D, 'Sum Old Guy', '老家伙', 'Sum Old Guy = 熟成到极致的小食'),
    (0xC1F94540, 'Sum Yung Guy', '小伙子', 'Sum Yung Guy = 刚出锅的小食'),
]

print('=== 译名表 ===')
for hid, old, new, why in RULES:
    po, pn = pack(old), pack(new)
    print('  ID=%08X %-10s -> %-8s (%d->%d slot, %s)' % (hid, old, new, len(po) // 2,
          len(pn) // 2, '缩短' if len(pn) < len(po) else ('等长' if len(pn) == len(po) else '★变长')))
    assert len(pn) <= len(po), '必须不扩容: %s' % old

# 表内：按 ID 定位记录起点（text_at = 记录起点 + 4）
CH_LO, CH_HI = ENT['static_CH.le_strings']
blob = v.read(v.find('static_CH', 'le_strings'))

def scan(b):
    res = []; i = 0; n = len(b)
    while i + 2 <= n:
        j = i; out = []
        while j + 2 <= n:
            x = struct.unpack_from('>H', b, j)[0]
            if x == 0: break
            out.append(x); j += 2
            if len(out) > 600: break
        if out: res.append((i, out)); i = j + 2
        else: i += 2
    return res

CH = scan(blob)
by_id = {}
for off, o in CH:
    if len(o) > 2:
        by_id.setdefault((o[0] << 16) | o[1], []).append((off, o))

n = 0
print()
print('=== 表内替换（按 ID 定位）===')
for hid, old, new, why in RULES:
    rows = by_id.get(hid)
    assert rows, 'ID=%08X 未找到' % hid
    for off, o in rows:
        assert len(o) > 2
        # slot<0x20 是控制符区（0x20=空格、0x27=撇号），按码点还原
        text = ''.join(
            (chr(x) if x < 0x20 else chr(CL[x - 0x20])) if (x < 0x20 or x - 0x20 < len(CL))
            else '?' for x in o[2:])
        assert text == old, 'ID=%08X 现文本 %r != %r' % (hid, text, old)
        n_slot = len(o) - 2# 文本占用的 slot 数
        new_bytes = pack(new)
        assert len(new_bytes) // 2 <= n_slot, \
            'ID=%08X 需扩容 (%d -> %d slot)' % (hid, n_slot, len(new_bytes) // 2)
        abs_text = CH_LO + off + 4
        pat = pack(old)
        assert bytes(buf[abs_text:abs_text + len(pat)]) == pat, 'ID=%08X 字节不匹配' % hid
        assert bytes(buf[abs_text + n_slot * 2:abs_text + n_slot * 2 + 2]) == b'\x00\x00'
        buf[abs_text:abs_text + n_slot * 2] = new_bytes + b'\x00' * (n_slot * 2 - len(new_bytes))
        n += 1
        print('  %08X ID=%08X %-10s -> %s' % (abs_text, hid, old, new))

# 表外松散副本：按 ID 也定位不到，改用「旧文本 + 属主过滤 + 排除表内已改」
print()
print('=== 表外松散副本 ===')
done_abs = set()
for off, o in CH:
    if len(o) > 2:
        done_abs.add(CH_LO + off + 4)
for hid, old, new, why in RULES:
    pat = pack(old) + b'\x00\x00'
    pn = pack(new)
    k = 0
    while True:
        k = bytes(buf).find(pat, k)
        if k < 0:
            break
        if not allowed(k) or k in done_abs:
            k += 2
            continue
        buf[k:k + len(pat)] = pn + b'\x00' * (len(pat) - len(pn))
        n += 1
        print('  %08X ID=%08X %-10s -> %s  (%s)' % (k, hid, old, new,
              owner(k) or '表外松散区'))
        k += len(pn)

print()
print('合计替换:', n, '处')

out = bytes(buf)
print()
print('=== 断言其它语言表零改动 ===')
for nm, (a, b) in ENT.items():
    if 'le_strings' not in nm or nm == 'static_CH.le_strings':
        continue
    assert out[a:b] == orig[a:b], nm
print('   ★ 通过')
changed = sorted({nm for nm, (a, b) in ENT.items() if out[a:b] != orig[a:b]})
print('   实际修改条目:', changed)
assert len(out) == orig_len, '文件长度变了！'
open(P, 'wb').write(out)
print()
print('size', len(out), '(unchanged)')
print('new md5', hashlib.md5(out).hexdigest())