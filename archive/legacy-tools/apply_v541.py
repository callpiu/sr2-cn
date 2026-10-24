# -*- coding: utf-8 -*-
"""
v541：汉化剩余地名与商店名（static_CH 内27 条 + 表外松散副本）
策略：全部是「缩短」→ 写入新 slot 后把余量 slot 填 0000 提前终止。
     不改表长度、不动哈希桶指针。
★★★ 只允许改 static_CH.le_strings 及其【表外松散副本】，
    严禁触碰其它语言表（US/DK/SE/FR/JP/CZ/ES/IT/NL/PL/RU）。
"""
import struct, hashlib, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

P = 'G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc'
BASE = 'e71c1d338e6bb6da7b2b603903c312d7'

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
orig_len = len(buf)

v = Vpp(P)
ds = v.data_start if hasattr(v, 'data_start') else 0x9000
ENT = {}
for e in v.entries():
    ENT[e['name'] + '.' + e['ext']] = (ds + e['body'], ds + e['body'] + e['size'])

CH_LO, CH_HI = ENT['static_CH.le_strings']
print('static_CH.le_strings 范围: %08X .. %08X' % (CH_LO, CH_HI))

# ==== 译名表 ====
MAP = {
    '3rd Street 1': '三街 1',
    '3rd Street 2': '三街 2',
    'Adept Way': '环能路',
    'Barrio': '唐人街',
    'Carbuncle Carls': '红宝石卡尔',
    'Dong Tea': '凉茶',
    'Donut Holes': '甜甜圈洞',
    'Elysian Fields': '至乐田',
    'Filmore': '菲尔莫尔',
    'Fox Drive': '狼径',
    'Hackenshack': '哈根沙克',
    'Harrowgate': '哈罗盖特',
    "Heaven's Helpers": '天堂助手',
    'Heaven Bound': '天堂限定',
    'Hoodieville': '帽衫镇',
    'Jacks or Better': '好牌优于一切',
    'Jacks or Higher': '更大的对子',
    'Lesalle': '拉萨勒',
    'Quinbecca': '昆比卡',
    'Rebadeaux': '雷巴多',
    'Ruin Island': '废墟岛',
    'Stoughton': '斯托顿',
    'Taps and Tips': '啤酒与小费',
    'Technically Legal': '法律边缘',
    'Wondermart 1': '神奇超市 1',
}

def owner(pos):
    for nm, (a, b) in ENT.items():
        if a <= pos < b:
            return nm
    return None

# ===== 第一步：static_CH 表内（entry 范围内）逐条改 =====
blob = v.read(v.find('static_CH', 'le_strings'))

def scan(b):
    res = []; i = 0; n = len(b)
    while i + 2 <= n:
        j = i; out = []
        while j + 2 <= n:
            x = struct.unpack_from('>H', b, j)[0]
            if x == 0: break
            out.append(x); j += 2
            if len(out) > 800: break
        if out: res.append((i, out)); i = j + 2
        else: i += 2
    return res

CH = scan(blob)
targets = []
for off, o in CH:
    if len(o) < 3: continue
    en = ''
    ok = True
    for x in o[2:]:
        if 0x20 <= x - 0x20 < len(CL) and CL[x - 0x20] < 128:
            en += chr(CL[x - 0x20])
        else:
            ok = False; break
    if ok and en in MAP:
        targets.append((off, en))

print()
print('表内待改:', len(targets))
n_in = 0
for off, en in targets:
    abs_at = CH_LO + off + 4
    j = off + 4
    old = []
    while j + 2 <= len(blob):
        x = struct.unpack_from('>H', blob, j)[0]
        if x == 0: break
        old.append(x); j += 2
    old_pat = bytes(buf[abs_at:abs_at + len(old) * 2])
    assert old_pat == pack(en), (hex(abs_at), en)
    assert buf[abs_at + len(old) * 2:abs_at + len(old) * 2 + 2] == b'\x00\x00'
    new_slots = pack(MAP[en])
    assert len(new_slots) < len(old_pat)
    buf[abs_at:abs_at + len(old_pat)] = new_slots + b'\x00' * (len(old_pat) - len(new_slots))
    n_in += 1
    print('   %08X %-22s -> %s' % (abs_at, en, MAP[en]))
print('表内已改:', n_in)

# ===== 第二步：表外松散副本（不属于任何 entry）=====
print()
n_out = 0
for en, cn in MAP.items():
    old_pat = pack(en)
    new_slots = pack(cn)
    i = 0
    while True:
        i = bytes(buf).find(old_pat, i)
        if i < 0: break
        # 必须是「完整记录尾部」：紧跟 0000
        endpos = i + len(old_pat)
        if buf[endpos:endpos + 2] != b'\x00\x00':
            i += 2; continue
        nm = owner(i)
        if nm is not None:
            # 在某个 entry 内：只有 static_CH 才允许改
            if nm != 'static_CH.le_strings':
                i += 2; continue
            # static_CH 内已在第一步改过，理论上不会命中；若命中说明有额外副本
        newp = new_slots + b'\x00' * (len(old_pat) - len(new_slots))
        buf[i:endpos + 2] = newp + b'\x00\x00'
        n_out += 1
        print('   %08X %-22s -> %-14s (%s)' % (i, en, cn, nm or '表外松散区'))
        i += len(newp)
print('表外/额外副本已改:', n_out)

# ===== 第三步：断言其它语言表零改动 =====
print()
b2 = bytes(buf)
for nm, (a, b) in ENT.items():
    if 'le_strings' not in nm or nm == 'static_CH.le_strings':
        continue
    assert b2[a:b] == bytes(open(P, 'rb').read())[a:b], nm
print('★ 其它所有 le_strings 表零改动，已断言')

assert len(b2) == orig_len, '文件长度变了！'
open(P, 'wb').write(b2)
print()
print('size', len(b2), '(unchanged)')
print('new md5', hashlib.md5(b2).hexdigest())