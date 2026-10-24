"""inject_experiment.py  --  v533 诊断用实机对照实验（一次性分辨三大根因）

把 static_CH 两条联机活动提示串替换成受控测试串（无格式码），其余 12248 条不动：
  REC1 0x84F287ED -> "面包车耐久测试文本"  (已知能正常显示的汉字, 无格式码)  对照组
  REC2 0x10AF1E62 -> "你的弟兄们需要你的保护" (原文汉字, 去格式码)          测格式码假设

判读:
  两条都正常   -> 格式码是祸首; 修复=给活动提示串剥 [format][color][/format]
  REC1正常REC2乱 -> 特定汉字问题(少见, 跟进)
  REC1就乱      -> 活动提示 UI 对所有中文都乱(UI/字体绑定问题)

安全: 先备份当前 patch.vpp_pc -> .v532_before_exp.bak; 追加式写入+重定点。
"""
import sys, struct, shutil, os
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp
import rebuild_mirror as rm

P = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
BAK = P + '.v532_before_exp.bak'

# ---- backup current deployed patch (v532) ----
if not os.path.exists(BAK):
    shutil.copy2(P, BAK)
    print('BACKUP ->', BAK)
else:
    print('backup already exists:', BAK)

vpp = Vpp(P)
rm.vpp = vpp

# ---- charlist for slot-encoding test strings ----
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
            idx = CP2IDX.get(cp)
            if idx is None:
                raise ValueError('char NOT in charlist_CH: %r U+%04X' % (ch, cp))
            out += struct.pack('>H', idx + 0x20)
    return bytes(out)

TEST = {
    0x84F287ED: '面包车耐久测试文本',      # REC1 control (known-good chars, no tags)
    0x10AF1E62: '你的弟兄们需要你的保护',   # REC2 tag-strip test (homies chars, no tags)
}

# ---- monkeypatch ch_text_map to inject test strings ----
_orig = rm.ch_text_map
def patched(name):
    m = _orig(name)
    if name == 'static_CH':
        for h, s in TEST.items():
            m[h] = encode(s)
            print('inject %s <- %r' % (hex(h), s))
    return m
rm.ch_text_map = patched

# ---- rebuild static_CH with injected strings ----
new_blob, nb, count, _ = rm.rebuild('static_US', 'static_CH')
print('rebuilt static_CH: nb=%d count=%d size=%d' % (nb, count, len(new_blob)))
rm.verify_blob('static_CH(exp)', new_blob, 'static_US')

# ---- deploy: append + repoint ----
e = vpp.find('static_CH', 'le_strings')
vpp.replace_body_appended(e, new_blob)
vpp.save(P)
print('DEPLOYED ->', P, 'new file size', os.path.getsize(P))

# ---- verify by re-reading ----
vpp2 = Vpp(P)
d = vpp2.read(vpp2.find('static_CH', 'le_strings'))
magic, ver, nb2, count2 = struct.unpack_from('<IHHI', d, 0)
A0 = 12 + nb2 * 8
ptrs = [struct.unpack_from('<I', d, A0 + i * 4)[0] for i in range(count2)]
def dec(units):
    out = []
    for u in units:
        if u < 0x80:
            out.append(chr(u))
        else:
            idx = u - 0x20
            out.append(chr(CPS[idx]) if 0 <= idx < len(CPS) else '?')
    return ''.join(out)
byh = {}
for off in ptrs:
    id1, id2 = struct.unpack_from('<HH', d, off)
    h = (id1 << 16) | id2
    units = []
    o = off + 4
    while True:
        u = struct.unpack_from('>H', d, o)[0]; o += 2
        if u == 0: break
        units.append(u)
    byh[h] = dec(units)
for h, s in TEST.items():
    print('VERIFY %s -> %r (expect %r) %s' % (hex(h), byh.get(h), s,
          'OK' if byh.get(h) == s else 'MISMATCH!'))
