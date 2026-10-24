# -*- coding: utf-8 -*-
"""
v526：圣徒街 -> 圣徽街（只改 4 条地图地名）

★ 只改【整串恰为『圣徒街』】的地图地名记录（4 条）。
  长句里的「圣徒街」「圣徒街区」以及「圣徒街教堂/车站/运河/阁楼/杀手」等
  复合地名一律不动 —— 用户选定范围。
  等长 3->3，偏移表/桶表零改动。
"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC  = os.path.join(GAME, "patch.vpp_pc")
OUT  = r"F:\sr2-cn\_fix_candidates\patch_v526.vpp_pc"
BASE = "8fa4cf3d88249de25addcfb9e2ac4e2b"   # v525

assert hashlib.md5(open(SRC, 'rb').read()).hexdigest() == BASE, "线上不是 v525，中止"

v = Vpp(SRC)
cl = [int(s) for s in v.read(v.find("charlist_CH", "txt")).decode('utf-8').split('\n') if s.strip().isdigit()]
S = {i + 0x20: cp for i, cp in enumerate(cl)}
c2s = {}
for i, cp in enumerate(cl):
    if cp >= 0x100:
        c2s.setdefault(chr(cp), i + 0x20)

def dec(sl):
    return ''.join(chr(x) if x < 0x100 else (chr(S[x]) if x in S else '<?%d>' % x) for x in sl)

def enc(text):
    out = []
    for ch in text:
        cp = ord(ch)
        if cp < 0x100:
            out.append(cp)
        else:
            assert ch in c2s, "字表缺字: %r" % ch
            out.append(c2s[ch])
    return out

OLD, NEW = '圣徒街', '圣徽街'
assert len(OLD) == len(NEW), "长度不等"
for ch in NEW:
    assert ch in c2s, "字表缺字: %r" % ch
print("目标字全部在字表中 ✓")

# ---------- 收集：只取整串恰为『圣徒街』的记录 ----------
plan = []
skipped = []
for e in v.entries():
    if e['ext'] != 'le_strings' or '_CH' not in e['name']:
        continue
    b = v.read(e)
    try:
        bc, c, oa, offs = file_offsets(b)
    except Exception:
        continue
    body = v.data_start + e['body']
    seen = set()
    for off in offs:
        sp = body + off + 4
        if sp in seen:
            continue
        seen.add(sp)
        if not (body < sp <= len(v.data) - 24):
            continue
        i = sp; n = len(v.data); sl = []
        while i + 2 <= n:
            x, y = v.data[i], v.data[i + 1]
            if x == 0 and y == 0:
                break
            sl.append((x << 8) | y); i += 2
        if not sl:
            continue
        t = dec(sl)
        if t == OLD:
            plan.append({'tbl': e['name'], 'off': off, 'sp': sp, 'slots': sl})
        elif OLD in t:
            skipped.append({'off': off, 'text': t})

print("\n=== 替换计划 ===")
print("  %s -> %s   整串精确匹配 %d 条" % (OLD, NEW, len(plan)))
for r in plan:
    print("    [%s] @0x%X" % (r['tbl'], r['off']))
print("\n  有意跳过（含『%s』但在长句/复合词里）%d 条：" % (OLD, len(skipped)))
for r in skipped[:6]:
    print("    @0x%-7X %r" % (r['off'], r['text'][:60]))
print("    ...（其余 %d 条同类）" % max(0, len(skipped) - 6))

# ---------- 写入 ----------
touched = set()
for r in plan:
    assert r['sp'] not in touched, "记录重叠 0x%X" % r['sp']
    touched.add(r['sp'])
    ns = enc(NEW)
    assert len(ns) == len(r['slots'])
    for j, sv in enumerate(ns):
        struct.pack_into('>H', v.data, r['sp'] + j * 2, sv)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'wb').write(v.data)
print("\n✓ 写出 %s" % OUT)

# ---------- 校验 ----------
assert len(v.data) == os.path.getsize(SRC), "大小变了！"
w = Vpp(OUT)
texts = []
for e in w.entries():
    if e['ext'] != 'le_strings' or '_CH' not in e['name']:
        continue
    b = w.read(e)
    try:
        bc, c, oa, offs = file_offsets(b)
    except Exception:
        continue
    body = w.data_start + e['body']
    seen = set()
    for off in offs:
        sp = body + off + 4
        if sp in seen:
            continue
        seen.add(sp)
        if not (body < sp <= len(w.data) - 24):
            continue
        i = sp; n = len(w.data); sl = []
        while i + 2 <= n:
            x, y = w.data[i], w.data[i + 1]
            if x == 0 and y == 0:
                break
            sl.append((x << 8) | y); i += 2
        if sl:
            texts.append(dec(sl))

n_old = sum(1 for t in texts if t == OLD)
n_new = sum(1 for t in texts if t == NEW)
print("\n=== 结果校验 ===")
print("  整串 '%s' = %d （应为 0）" % (OLD, n_old))
print("  整串 '%s' = %d （应为 %d）" % (NEW, n_new, len(plan)))
assert n_old == 0 and n_new == len(plan)

print("\n=== 保留检查（不该动的仍在）===")
for keep in ('圣徒街区', '圣徒街教堂', '圣徒街车站', '圣徒街运河', '圣徒街阁楼',
             '圣徒街杀手', '圣徒街超级公寓', '前往[format][color:teal]圣徒街[/format]'):
    print("    %-38s %d 条" % (keep, sum(1 for t in texts if keep in t)))

a0 = open(SRC, 'rb').read(); b0 = open(OUT, 'rb').read()
d = [i for i in range(len(a0)) if a0[i] != b0[i]]
print("\n文件大小 %d（未变）" % len(b0))
print("差异字节 %d （预期 4条 x 3字 x 2字节 = 24）" % len(d))
print("md5 %s" % hashlib.md5(b0).hexdigest())
