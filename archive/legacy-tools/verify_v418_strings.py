"""v418 解码验证：从构建产物抽取关键串，分别用 正确路径(slot-0x20) 与 坏路径(slot-0x40) 解码，
确认 徒/录/弹 在两条路径都正确显示。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, SHIFT

OUT = r"F:\sr2-cn\_fix_candidates\patch_v418.vpp_pc"
v = Vpp(OUT)

# charlist -> idx:codepoint
e_cl = v.find("charlist_CH", "txt")
cl = v.read(e_cl).decode('utf-8').split('\n')
clmap = {i: int(cl[i]) for i in range(len(cl)) if cl[i].strip().isdigit()}

def decode_slots(vals, path):
    """path='ok' -> slot-0x20 ; path='bad' -> slot-0x40"""
    sub = SHIFT if path == 'ok' else 0x40
    out = []
    for x in vals:
        if x < 0x100:
            out.append(chr(x))
        else:
            cp = clmap.get(x - sub)
            out.append(chr(cp) if cp else '\ufffd')
    return ''.join(out)

# 读某条 _CH le_strings 的全部记录
def iter_records(v, name):
    e = v.find(name, "le_strings")
    b = v.read(e)
    bc, count, oa, offs = file_offsets(b)
    body_off = v.data_start + e['body']
    seen = set()
    for off in offs:
        sp = body_off + off + 8
        if sp in seen:
            continue
        seen.add(sp)
        i = sp
        n = len(v.data)
        vals = []
        while i + 2 <= n:
            b0, b1 = v.data[i], v.data[i+1]
            if b0 == 0 and b1 == 0:
                yield vals
                break
            vals.append((b0<<8)|b1)
            i += 2

targets = ['圣徒街', '霰弹枪', '登录', '须登录']
for tname in ('static_CH', 'platform_pc_CH'):
    print("=== %s ===" % tname)
    hits = 0
    for vals in iter_records(v, tname):
        s_ok = decode_slots(vals, 'ok')
        if any(k in s_ok for k in targets):
            s_bad = decode_slots(vals, 'bad')
            flag = "OK" if s_ok == s_bad else "DIFF"
            print("  [%s] %r" % (flag, s_ok[:50]))
            if s_ok != s_bad:
                print("       坏路: %r" % s_bad[:50])
            hits += 1
    print("  (命中 %d 条含目标关键词)" % hits)
