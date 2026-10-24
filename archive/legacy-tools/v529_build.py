# -*- coding: utf-8 -*-
"""
v529：整串『兄弟会』-> 『兄弟帮』（5 条）

★ 范围：只改【整串恰为『兄弟会』】的 5 条记录 —— 这是界面显示帮派名的位置。
  覆盖：报纸界面（黄色大字标题）、任务完成界面、帮派相关界面。
  其它 147 条含『兄弟会』的长句（剧情台词、成员称呼、通缉度、嘲讽赞语、
  车辆/性格/配乐、据点等）一律不动。
  等长替换，偏移表/桶表零改动。
"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC  = os.path.join(GAME, "patch.vpp_pc")
OUT  = r"F:\sr2-cn\_fix_candidates\patch_v529.vpp_pc"
BASE = "503946b452c043f34345e0fcd941df30"   # v528

assert hashlib.md5(open(SRC, 'rb').read()).hexdigest() == BASE, "线上不是 v528，中止"

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

OLD, NEW = '兄弟会', '兄弟帮'
assert len(OLD) == len(NEW), "长度不等"
# ★ c2s 的键是【单字符】，NEW 是多字串，必须逐字查（此前误写成 NEW in c2s）
for ch in NEW:
    assert ch in c2s, "字表缺字 %r" % ch
print("『%s』各字均在字表中: %s ✓" % (NEW, {ch: c2s[ch] for ch in NEW}))

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
others = 0
for r in records:
    t = r['text']
    if t == OLD:
        plan.append((r, NEW))
    elif OLD in t:
        others += 1

print("\n=== 替换计划（整串恰为『%s』）===" % OLD)
for r, new in plan:
    print("  [%s] @0x%-7X %r -> %r" % (r['tbl'], r['off'], r['text'], new))
print("  合计 %d 条" % len(plan))
print("\n  有意不改（含『%s』但在长句里）%d 条" % (OLD, others))

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
na = sum(1 for t in texts if t == OLD)
nb = sum(1 for t in texts if t == NEW)
print("  整串 %r = %d （应为 0）" % (OLD, na))
print("  整串 %r = %d （应为 %d）" % (NEW, nb, len(plan)))
assert na == 0 and nb == len(plan)

print("\n=== 保留检查（不该动的仍在）===")
for keep in ('兄弟会配乐', '兄弟会近战', '兄弟会性格', '兄弟会车辆',
             '兄弟会 1', '欢迎加入兄弟会', '兄弟会成员：',
             '开始兄弟帮任务', '兄弟帮任务 11'):
    print("    %-16s %d 条" % (keep, sum(1 for t in texts if keep in t)))

a0 = open(SRC, 'rb').read(); b0 = open(OUT, 'rb').read()
d = [i for i in range(len(a0)) if a0[i] != b0[i]]
print("\n文件大小 %d（未变）" % len(b0))
print("差异字节 %d （5条 x 1字）" % len(d))
print("md5 %s" % hashlib.md5(b0).hexdigest())
