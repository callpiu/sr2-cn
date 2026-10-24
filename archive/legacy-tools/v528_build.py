# -*- coding: utf-8 -*-
"""
v528：霰弹枪 -> 散筒枪（3 条）、子弹 -> 火料（7 条）

★ 只改【整串恰为『霰弹枪』】与【整串恰为『子弹』】的记录 ——
  即武器列表条目名与 HUD 弹药标签。
  长句里的『霰弹枪弹药』『霰弹枪命中率』『减少子弹伤害』『把子弹留给恶司』
  等一律不动（按需求是"枪械列表/弹药"范围）。
  等长替换，偏移表/桶表零改动。
"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC  = os.path.join(GAME, "patch.vpp_pc")
OUT  = r"F:\sr2-cn\_fix_candidates\patch_v528.vpp_pc"
BASE = "602587cf0f72384cb1789be1803a4f51"   # v527

assert hashlib.md5(open(SRC, 'rb').read()).hexdigest() == BASE, "线上不是 v527，中止"

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

# 整串精确匹配规则
RULES = [('霰弹枪', '散筒枪'), ('子弹', '火料')]
MAP = dict(RULES)
for a, b in RULES:
    assert len(a) == len(b), "长度不等: %s / %s" % (a, b)
    for ch in b:
        assert ch in c2s, "字表缺字: %r" % ch
print("目标字全部在字表中，等长 ✓")

records = []
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
        if sl:
            records.append({'tbl': e['name'], 'off': off, 'sp': sp, 'slots': sl,
                            'text': dec(sl)})

plan = []
kept = {'霰弹枪': 0, '子弹': 0}
for r in records:
    t = r['text']
    if t not in MAP:
        for k in kept:
            if k in t:
                kept[k] += 1
        continue
    new = MAP[t]
    plan.append((r, new))

print("\n=== 替换计划（整串精确匹配）===")
for a, b in RULES:
    n = sum(1 for r, x in plan if r['text'] == a)
    print("  %s -> %s   %d 条" % (a, b, n))
for r, new in plan:
    print("    [%s] @0x%-7X %r -> %r" % (r['tbl'], r['off'], r['text'], new))
print("  合计 %d 条" % len(plan))
print("\n  有意保留（长句里仍含旧词）：霰弹枪 %d 条、子弹 %d 条" % (kept['霰弹枪'], kept['子弹']))

touched = set()
for r, new in plan:
    assert r['sp'] not in touched, "记录重叠 0x%X" % r['sp']
    touched.add(r['sp'])
    ns = enc(new)
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

print("\n=== 结果校验 ===")
for a, b in RULES:
    na = sum(1 for t in texts if t == a)
    nb = sum(1 for t in texts if t == b)
    print("  整串 %r = %d （应为 0）   整串 %r = %d （应为 %d）" % (a, na, b, nb, na))
    assert na == 0 and nb > 0

print("\n=== 保留检查（长句里的旧词应仍在）===")
for keep in ('霰弹枪弹药', '霰弹枪命中率', '霰弹枪击杀数', '短管双管霰弹枪',
             '减少子弹伤害', '把子弹留给恶司', '发射 %ls 发子弹'):
    print("    %-20s %d 条" % (keep, sum(1 for t in texts if keep in t)))

a0 = open(SRC, 'rb').read(); b0 = open(OUT, 'rb').read()
d = [i for i in range(len(a0)) if a0[i] != b0[i]]
print("\n文件大小 %d（未变）" % len(b0))
print("差异字节 %d （霰弹枪3条+子弹7条 = 10条 各变2字）" % len(d))
print("md5 %s" % hashlib.md5(b0).hexdigest())
