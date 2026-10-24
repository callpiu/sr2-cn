# -*- coding: utf-8 -*-
"""
v525：地名双「区」修复（尾「区」→空格）

背景（v408/v411 定论）：
  · 暂停菜单地图界面会给地名单独追加一个「区」字（不经过 %ls 区 格式串）
  · 提示格式串「前往[format][color:teal]%ls 区[/format]」也追加「区」
  ⇒ 地名末字绝不能是「区」，否则显示成「住宅区 区」「老城 区」
  ⇒ 方案：把地名末尾的「区」换成空格（等长），格式串一个字不动

★ 当前基线是 v407（用户整目录备份回退所致），v411 的修改并不存在，
  本次是从零重做。

判定依据（英文原串自带 District 才译出「区」才合理）：
  英文自带 District  → 中文带「区」是对的，但要避免与界面追加的「区」重复
  英文不带 District  → 中文根本不该有「区」
  两条路径都会追加「区」⇒ 无论哪种，末字都要换成空格
"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC  = os.path.join(GAME, "patch.vpp_pc")
OUT  = r"F:\sr2-cn\_fix_candidates\patch_v525.vpp_pc"
BASE = "b654cb3cfd5020dbdf28f94cae671191"   # v524

assert hashlib.md5(open(SRC, 'rb').read()).hexdigest() == BASE, "线上不是 v524，中止"

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

# ---------- 规则：地名整串精确匹配，尾「区」→空格 ----------
# ★ 只处理"整串就是一个地名"的记录。
#   句子（如「正在进入禁区」「返回市区」「竞技场，贫民区」）不在此列，
#   它们的「区」是句内成分，界面追加的「区」只跟在孤立地名后面。
NAMES = [
    # —— 英文自带 District（原译「区」合理，但会与界面追加的重复）——
    ('工厂区',        'Factories District'),
    ('红灯区',        'Red Light District'),
    ('酒店码头区',     'Marina District'),
    ('码头区/博物馆区', 'Marina/Museum Districts'),
    ('Barrio 区',     'Barrio District'),
    ('巴里奥区',       'Barrio District'),
    ('市中心区',       'Downtown District'),
    ('斯蒂尔沃特核厂区','Stilwater Nuclear Plant District'),
    ('娱乐区',        'Entertainment District'),
    ('码头区',        'Wharfside District'),
    ('拖车公园区',     'Trailer Park District'),
    # —— 英文不带 District（本不该有「区」）——
    ('棚户区',        'Projects'),
    ('大学区',        'University'),
    ('住宅区',        'Residential'),
    ('办公区',        'Business District 近似'),
    ('工业区',        'Industrial'),
    ('老城区',        'Old Town / Downtown 旧区'),
    ('城郊扩建区',     'Suburbs Expansion'),
    ('街区',          'Hoods / Block'),
    ('未知街区',       'Unknown Block'),
    ('控制街区',       'Control Block'),
    ('兄弟街区',       'Frat Row'),
    # —— v524 引入的两个，末字也是「区」，同样会双区，一并处理 ——
    ('主城区',        'Downtown District（v524 由『市中心』改来）'),
    ('城郊',          'Suburbs（v524 由『郊区』改来）'),
]
NAME2 = {a: b for a, b in NAMES}

plan = []
stats = {}
for r in records:
    t = r['text']
    if t not in NAME2:
        continue
    new = t[:-1] + ' '          # 尾「区」→「 」
    assert len(new) == len(t), "长度不等: %r -> %r" % (t, new)
    plan.append((r, new))
    stats[t] = stats.get(t, 0) + 1

print("\n=== 替换计划（尾『区』→空格）===")
for k in sorted(stats, key=lambda x: -stats[x]):
    r_ = [x for x in plan if x[0]['text'] == k][0][0]
    print("  %-18s -> %-18r  x%d   (英文 %s)" % (k, k[:-1] + ' ', stats[k], NAME2[k]))
print("  合计 %d 条记录" % len(plan))

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
bad = 0
for k in sorted(stats):
    n_before = sum(1 for t in texts if t == k)
    n_after = sum(1 for t in texts if t == k[:-1] + ' ')
    mark = "OK" if (n_before == 0 and n_after == stats[k]) else "★"
    if mark == "★":
        bad += 1
    print("  [%s] %-18s 原样=%d  已改=%d" % (mark, k, n_before, n_after))
assert bad == 0, "有替换未生效"

print("\n=== 保留检查（句子里带『区』的，一律不该动）===")
for keep in ('正在进入禁区', '正在离开禁区', '第 9 区', '竞技场，贫民区', '返回市区'):
    print("    %-14s %d 条" % (keep, sum(1 for t in texts if t == keep)))

a0 = open(SRC, 'rb').read(); b0 = open(OUT, 'rb').read()
d = [i for i in range(len(a0)) if a0[i] != b0[i]]
print("\n文件大小 %d（未变）" % len(b0))
print("差异字节 %d" % len(d))
print("md5 %s" % hashlib.md5(b0).hexdigest())
