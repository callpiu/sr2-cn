# -*- coding: utf-8 -*-
# diag41: 字节流错位模拟—— subtitle 渲染器按字节流读 slot 的假设
import sys, struct, shutil
sys.path.insert(0, 'F:/sr2-cn')
import sr2lib

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
shutil.copy(GAME + r'\patch.vpp_pc.v532_before_exp.bak', r'F:/sr2-cn/_tmp_v532.vpp_pc')
vb = sr2lib.Vpp(r'F:/sr2-cn/_tmp_v532.vpp_pc')
blob = vb.read(vb.find('static_CH', 'le_strings'))

CPS = [int(l) for l in vb.read(vb.find('charlist_CH', 'txt'))
       .decode('utf-8').split('\n') if l.strip().isdigit()]
CHR = ''.join(chr(c) for c in CPS)

def rec_bytes(h):
    id1, id2 = h >> 16, h & 0xFFFF
    p = struct.pack('<HH', id1, id2)
    i = blob.find(p)
    off = i + 4
    out = b''
    while off + 2 <= len(blob):
        v = struct.unpack_from('>H', blob, off)[0]
        off += 2
        if v == 0:
            break
        out += struct.pack('>H', v)
    return out

G1 = '任璨偶巧位雄衡任璨伪该'
G2 = '任璨偶巧位校衡勾远藐乱携伪该亡位通像匪冰挺拮'

def decode_stream(data, byte_off, endian, tag_mode):
    """Read u16 stream from data[byte_off:], decode slots via CPS.
    tag_mode='keep': decode everything. 'skip-ascii': skip units <0x100."""
    out = []
    off = byte_off
    while off + 2 <= len(data):
        v = struct.unpack_from(endian, data, off)[0]
        off += 2
        if v == 0:
            break
        if v < 0x100:
            if tag_mode == 'keep':
                out.append(chr(v) if 32 <= v < 127 else '?')
            continue
        if v - 0x20 < len(CHR):
            out.append(CHR[v - 0x20])
        else:
            out.append('?')
    return ''.join(out)

for name, h, garb in (('REC1', 0x84F287ED, G1), ('REC2', 0x10AF1E62, G2)):
    d = rec_bytes(h)
    print(f'=== {name} (target: {garb}) ===')
    for bo in (0, 1):
        for en, ename in (('>H', 'BE'), ('<H', 'LE')):
            for tm in ('skip-ascii', 'keep'):
                s = decode_stream(d, bo, en, tm)
                mark = ' <<<< MATCH' if garb in s else ''
                print(f'  off={bo} {ename} {tm:10s}: {s}{mark}')
