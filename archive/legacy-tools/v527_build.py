# -*- coding: utf-8 -*-
"""
v527：任务列表里的「兄弟会任务」-> 「兄弟帮任务」（8 条）

★ 范围：仅任务列表的条目名，即【整串形如『兄弟会任务 N』或『兄弟会 任务N』】。
  其它 140+ 条含「兄弟会」的记录（帮派介绍、剧情台词、嘲讽/赞语、车辆、
  通缉度、据点、成员称呼等）一律不动 —— 用户选定范围。
  等长替换（会->帮），偏移表/桶表零改动。
"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC  = os.path.join(GAME, "patch.vpp_pc")
OUT  = r"F:\sr2-cn\_fix_candidates\patch_v527.vpp_pc"
BASE = "e7821a0aa4aee392458574896f26267e"   # v526

assert hashlib.md5(open(SRC, 'rb').read()).hexdigest() == BASE, "线上不是 v526，中止"

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

assert '帮' in c2s, "字表缺『帮』"
print("『帮』在字表中 slot=%d ✓" % c2s['帮'])

# ---------- 规则：整串匹配「兄弟会任务 N」/「兄弟会 任务N」 ----------
import re
PAT = re.compile(r'^兄弟会\s*任务\s*\d+$')

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
    if not PAT.match(t):
        if '兄弟会' in t:
            others += 1
        continue
    new = t.replace('兄弟会', '兄弟帮')
    assert len(new) == len(t), "长度不等: %r -> %r" % (t, new)
    plan.append((r, new))

print("\n=== 替换计划（任务列表条目名）===")
for r, new in plan:
    print("  [%s] @0x%-7X %r -> %r" % (r['tbl'], r['off'], r['text'], new))
print("  合计 %d 条" % len(plan))
print("\n  其它含『兄弟会』但按需求不改的记录：%d 条" % others)

# ---------- 写入 ----------
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
import re
old_left = sum(1 for t in texts if PAT.match(t))
new_ok = sum(1 for t in texts if re.match(r'^兄弟帮\s*任务\s*\d+$', t))
print("  『兄弟会任务 N』残留 = %d （应为 0）" % old_left)
print("  『兄弟帮任务 N』       = %d （应为 %d）" % (new_ok, len(plan)))
assert old_left == 0 and new_ok == len(plan)

print("\n=== 保留检查（不该动的仍在）===")
for keep in ('兄弟会', '兄弟会任务 11', '兄弟会 任务6', '欢迎加入兄弟会',
             '开始兄弟帮任务', '兄弟会成员：', '兄弟会藏身处'):
    print("    %-18s %d 条" % (keep, sum(1 for t in texts if keep in t)))

a0 = open(SRC, 'rb').read(); b0 = open(OUT, 'rb').read()
d = [i for i in range(len(a0)) if a0[i] != b0[i]]
print("\n文件大小 %d（未变）" % len(b0))
print("差异字节 %d （8条 x 1字 x 2字节 = 16）" % len(d))
print("md5 %s" % hashlib.md5(b0).hexdigest())
