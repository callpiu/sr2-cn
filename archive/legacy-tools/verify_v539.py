import struct, hashlib, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
P = G + 'patch.vpp_pc'
new = open(P, 'rb').read()
ob = open(G + 'patch.vpp_pc.before_v539.bak', 'rb').read()
print('md5', hashlib.md5(new).hexdigest(), 'size', len(new), '== old size', len(ob))
assert len(new) == len(ob)

diff = [i for i in range(len(new)) if new[i] != ob[i]]
print('diff bytes', len(diff))

CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))

def S(w):
    return struct.pack('>H', CL.index(ord(w)) + 0x20)

def dec(b):
    out = []
    for i in range(0, len(b) - 1, 2):
        x = struct.unpack_from('>H', b, i)[0]
        if x == 0:
            out.append('|')
        elif x < 0x20:
            out.append('^%02X' % x)
        elif x - 0x20 < len(CL):
            out.append(chr(CL[x - 0x20]))
        else:
            out.append('?')
    return ''.join(out)

v = Vpp(P)
print()
print('=== voice_script_CH 中 Father 相关记录全览 ===')
blob = v.read(v.find('voice_script_CH', 'le_strings'))
i = 0
res = []
while i + 2 <= len(blob):
    j = i
    out = []
    while j + 2 <= len(blob):
        x = struct.unpack_from('>H', blob, j)[0]
        if x == 0:
            break
        out.append(x)
        j += 2
        if len(out) > 500:
            break
    if out:
        res.append((i, out))
        i = j + 2
    else:
        i += 2
print('records', len(res))
n_f = n_s = 0
for off, s in res:
    txt = s[2:] if len(s) > 2 else s
    t = dec(struct.pack('>' + 'H' * len(txt), *txt))
    if '父亲' in t or '神父' in t:
        if '父亲' in t:
            n_f += 1
        if '神父' in t:
            n_s += 1
        print('  %08X  %s' % (off, t[:120]))
print('含父亲记录数', n_f, ' 含神父记录数', n_s)

print()
print('=== 整文件残留检查 ===')
print('神父 残留', new.count(S('神') + S('父')))
print('父亲 命中', new.count(S('父') + S('亲')))

print()
print('=== v538/v537 回归 ===')
sblob = v.read(v.find('static_CH', 'le_strings'))
r2 = []
i = 0
while i + 2 <= len(sblob):
    j = i
    out = []
    while j + 2 <= len(sblob):
        x = struct.unpack_from('>H', sblob, j)[0]
        if x == 0:
            break
        out.append(x)
        j += 2
        if len(out) > 500:
            break
    if out:
        r2.append(out)
        i = j + 2
    else:
        i += 2
allt = '\n'.join(dec(struct.pack('>' + 'H' * len(s), *s)) for s in r2)
for kw in ['指定辩护律师', '霰弹枪', '弹药', '市郊', '三街圣徒', '兄弟会', '主城区']:
    print('  %-8s %d' % (kw, allt.count(kw)))
for kw in ['散筒枪', '火料', '填料', '兄弟帮', '城郊']:
    print('  BAD %-8s %d' % (kw, allt.count(kw)))
print('  市郊 记录:', [dec(struct.pack('>' + 'H' * len(s[2:]), *s[2:])) for s in r2
                       if len(s) > 2 and s[0] == 0x3DC0 and s[1] == 0xDFCC])