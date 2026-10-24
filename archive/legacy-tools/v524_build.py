# -*- coding: utf-8 -*-
"""
v524：有货即达 / 主城区 / 城郊 / 年龄档"老"   —— 全部等长替换，零结构风险

  有货必达       -> 有货即达    3 条（全表精确匹配）
  市中心         -> 主城区     32 条（全表精确替换，等长3->3）
  郊区           -> 城郊       33 条（全表精确替换，等长2->2）
  旧（年龄档）   -> 老          2 条（同文双记录，精确匹配整串=='旧'）
"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC  = os.path.join(GAME, "patch.vpp_pc")
OUT  = r"F:\sr2-cn\_fix_candidates\patch_v524.vpp_pc"
BASE = "af27de344ca40a28a4fb5895569aad70"   # v523

assert hashlib.md5(open(SRC, 'rb').read()).hexdigest() == BASE, "线上不是 v523，中止"

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

# ---------- 收集 ----------
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
            records.append({'tbl': e['name'], 'off': off, 'sp': sp, 'slots': sl})
print("CH 记录总数: %d" % len(records))
for r in records:
    r['text'] = dec(r['slots'])

# ---------- 规则 ----------
# 整串精确匹配
EXACT = [
    ('有货必达', '有货即达'),
    ('旧', '老'),          # ★ 年龄档：整串就是单个"旧"；"依旧/旧酒吧/旧曲目"等均不受影响
]
# 全文子串替换（等长）
# ★ 「市中心区」(4字) 排除：等长条件下改成「主城区区」是叠字，改成「主城区」又短 1 字
#   需要变长/变短 = 重建数据区，风险高。5 条保持原样并已在报告中列出。
SUB = [
    ('市中心', '主城区'),   # 3->3 等长：Downtown District 的对应译名
    ('郊区', '城郊'),       # 2->2 等长
]
SKIP = [('市中心区',)]

plan = []
stats = {}
skipped = []
for r in records:
    t = r['text']
    new = t
    rule = None
    for a, b in EXACT:
        if t == a:
            new = b; rule = '整串:%s->%s' % (a, b); break
    if rule is None:
        if any(s in t for s in SKIP[0]):
            skipped.append(r)
            continue
        for a, b in SUB:
            if a in t:
                new = new.replace(a, b)
                rule = rule or ('子串:%s->%s' % (a, b))
    if rule is None or new == t:
        continue
    assert len(new) == len(t), "长度不等: %r -> %r" % (t, new)
    plan.append((r, new, rule))
    stats[rule] = stats.get(rule, 0) + 1

print("\n=== 替换计划 ===")
for k, n in sorted(stats.items()):
    print("  %-30s %d 条" % (k, n))
print("  合计 %d 条记录" % len(plan))
if skipped:
    print("\n  ⚠ 跳过 %d 条（含『市中心区』，等长条件下无法改成通顺词）：" % len(skipped))
    for r in skipped:
        print("     @0x%-7X %r" % (r['off'], r['text'][:70]))

# ---------- 写入 ----------
touched = set()
for r, new, rule in plan:
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
alltxt = '\n'.join(texts)
print("\n=== 结果校验 ===")
for a, b in [('有货必达', '有货即达'), ('市中心', '主城区'), ('郊区', '城郊'), ('旧', '老')]:
    print("  %-8s 残留=%-4d 新增=%d" % (a, alltxt.count(a), alltxt.count(b)))
print("  整串 '旧' 记录数 = %d （应为 0）" % sum(1 for t in texts if t == '旧'))
print("  整串 '老' 记录数 = %d （应为 2）" % sum(1 for t in texts if t == '老'))
# 确认不该动的还在
print("\n  保留检查（旧词应仍存在）：")
for keep in ('旧酒吧', '依旧逍遥法外', '移除旧曲目', '旧播放列表', '怀旧', '旧肉类加工厂', '旧纹身'):
    print("    %-14s %d 条" % (keep, alltxt.count(keep)))

a0 = open(SRC, 'rb').read(); b0 = open(OUT, 'rb').read()
d = [i for i in range(len(a0)) if a0[i] != b0[i]]
print("\n文件大小 %d（未变）" % len(b0))
print("差异字节 %d" % len(d))
print("md5 %s" % hashlib.md5(b0).hexdigest())
