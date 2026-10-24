# -*- coding: utf-8 -*-
"""
扫描 static_CH 里"未汉化"的记录：同一个 32 位 ID 在 static_US 里的原文，
若CH 侧解码出来的文本 == 英文原文（或 CH 侧根本是纯 ASCII），即为漏翻。
"""
import struct, sys, json
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'

CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))
print('charlist', len(CL))


def D(slots):
    """slot序列 -> 文本"""
    out = []
    for x in slots:
        if x == 0:
            break
        if x < 0x20:
            out.append('\x01' if x == 1 else '\x02')
        elif x - 0x20 < len(CL):
            out.append(chr(CL[x - 0x20]))
        else:
            out.append('?')
    return ''.join(out)


def A(slots):
    """slot序列 -> ASCII（英文表）"""
    out = []
    for x in slots:
        if x == 0:
            break
        if 32 <= x < 0x7F:
            out.append(chr(x))
        else:
            return None
    return ''.join(out)


def scan(b):
    res = []
    i = 0
    n = len(b)
    while i + 2 <= n:
        j = i
        out = []
        while j + 2 <= n:
            x = struct.unpack_from('>H', b, j)[0]
            if x == 0:
                break
            out.append(x)
            j += 2
            if len(out) > 800:
                break
        if out:
            res.append((i, out))
            i = j + 2
        else:
            i += 2
    return res


v = Vpp(G + 'patch.vpp_pc')
ch_blob = v.read(v.find('static_CH', 'le_strings'))
CH = scan(ch_blob)
print('CH records', len(CH))

v2 = Vpp('F:/sr2-cn/_ref_第三方补丁/原始基准/patch_第三方原版.vpp_pc')
us_blob = v2.read(v2.find('static_US', 'le_strings'))
US = scan(us_blob)
print('US records', len(US))

# 按 ID 建索引（同一 ID 在两表指向同一条）
us_by_id = {}
for off, o in US:
    if len(o) >= 3:
        h = (o[0] << 16) | o[1]
        us_by_id.setdefault(h, (off, o[2:]))

print('US unique ids', len(us_by_id))

untranslated = []
pure_ascii = []
matched = 0
for off, o in CH:
    if len(o) < 3:
        continue
    h = (o[0] << 16) | o[1]
    txt = D(o[2:])
    if h in us_by_id:
        matched += 1
        uoff, uslots = us_by_id[h]
        us = A(uslots)
        if us is not None and txt == us:
            untranslated.append((off, h, us, len(o) - 2))
    # CH 侧本身是纯 ASCII（= 没汉化）
    if txt.isascii() and txt.strip():
        pure_ascii.append((off, h, txt, len(o) - 2))

print()
print('ID matched', matched)
print('CH文本==US原文 (漏翻):', len(untranslated))
print('CH 侧纯 ASCII (疑似漏翻):', len(pure_ascii))
print()

json.dump({'untranslated': [[a, b, c, d] for a, b, c, d in untranslated],
           'pure_ascii': [[a, b, c, d] for a, b, c, d in pure_ascii]},
          open('F:/sr2-cn/_untranslated.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

print('=== CH文本 == US原文 的漏翻记录（前80） ===')
for off, h, us, ln in untranslated[:80]:
    print('  %08X  ID=%08X  slots=%-3d %r' % (off, h, ln, us[:90]))

print()
print('=== CH 侧纯 ASCII（前60） ===')
for off, h, t, ln in pure_ascii[:60]:
    print('  %08X  ID=%08X  slots=%-3d %r' % (off, h, ln, t[:90]))