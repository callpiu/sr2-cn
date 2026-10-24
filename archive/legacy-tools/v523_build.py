# -*- coding: utf-8 -*-
"""
v523：专有名词 + 用语统一修正（等长槽值替换，不改结构）

专有名词（全表）：
  圣徒七人 -> 七圣集结
  Rounds 广场购物中心 -> Rounds 广场购物商城
  新亨内凯娱乐中心 -> 新亨内凯娱乐天地
  斯蒂尔沃特大学学生会 -> 斯蒂尔沃特大学学生楼
  开始兄弟会任务 -> 开始兄弟帮任务
用语（限定语境）：
  获得 -> 赚到   仅限「金钱 / 现金 / 声望」语境
  得分 -> 计分   仅限短串（HUD/标签），长句教程不动
"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC  = os.path.join(GAME, "patch.vpp_pc")
OUT  = r"F:\sr2-cn\_fix_candidates\patch_v523.vpp_pc"
BASE = "59db87697208f6f404d03278b6b0c4cd"   # 拆车厂修复版

assert hashlib.md5(open(SRC, 'rb').read()).hexdigest() == BASE, "线上不是拆车厂修复版，中止"

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

# ---------- 收集记录（4 字节头） ----------
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

# ---------- 规则定义 ----------
# 1) 专有名词：整串精确匹配
PROPER = [
    ('圣徒七人', '七圣集结'),
    ('Rounds 广场购物中心', 'Rounds 广场购物商城'),
    ('新亨内凯娱乐中心', '新亨内凯娱乐天地'),
    ('斯蒂尔沃特大学学生会', '斯蒂尔沃特大学学生楼'),
    ('开始兄弟会任务', '开始兄弟帮任务'),
    ('获得分数', '赚到分数'),        # 精确规则，避免被"得分→计分"切成"获计分数"
]
# 2) 「获得」→「赚到」：仅金钱/现金/声望语境
#    规则：紧跟在「获得」之后的词属于 {的, 了, %, 空格} 且该句含 金钱/现金/声望 之一
GAIN_WORDS = ('金钱', '现金', '声望', '奖励')
GAIN_OK_NEXT = ('的', '了', ' ', '%', '$', '现', '金', '声', '额', '一', '额')
def gain_ok(text):
    """判断一条记录里所有『获得』是否都该改成『赚到』"""
    idx = 0
    hits = []
    while True:
        i = text.find('获得', idx)
        if i < 0:
            break
        hits.append(i)
        idx = i + 2
    if not hits:
        return False
    # 该句必须含金钱/现金/声望，且不含这些不该搭配的词
    if not any(w in text for w in ('金钱', '现金', '声望')):
        return False
    for bad in ('奖牌', '金牌', '银牌', '铜牌', '勋章', '成就', '分数', '风格点数',
                '徽章', '道具', '衣服', '武器', '弹匣', '已拥有', '金星', '铜星', '银星'):
        if bad in text:
            return False
    return True

# 3) 「得分」→「计分」：仅短串（HUD/标签），长句教程不动
SCORE_MAXLEN = 20      # 超过这个长度的串视为教程/说明长句，不动
def score_ok(text):
    return len(text) <= SCORE_MAXLEN

# ---------- 生成替换计划 ----------
plan = []   # (record, 新文本, 规则名)
stats = {}
for r in records:
    t = r['text']
    new = t
    rule = None
    # 专有名词（整串精确）
    for a, b in PROPER:
        if t == a:
            new = b; rule = '专名:' + a
            break
    if rule is None and '获得' in t and gain_ok(t):
        new = t.replace('获得', '赚到'); rule = '获得→赚到'
    if rule is None and '得分' in t and score_ok(t):
        new = new.replace('得分', '计分'); rule = '得分→计分'
    if rule is None or new == t:
        continue
    assert len(new) == len(t), "长度不等: %r -> %r" % (t, new)
    plan.append((r, new, rule))
    stats[rule] = stats.get(rule, 0) + 1

print("\n=== 替换计划 ===")
for k, v_ in sorted(stats.items(), key=lambda x: -x[1]):
    print("  %-46s %d 条" % (k, v_))
print("  合计 %d 条记录" % len(plan))

# ---------- 写入 ----------
changed = set()
for r, new, rule in plan:
    assert r['sp'] not in changed, "记录重叠: 0x%X" % r['sp']
    changed.add(r['sp'])
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
recs2 = []
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
            recs2.append(dec(sl))

alltxt = '\n'.join(recs2)
print("\n=== 结果校验 ===")
for a, b in PROPER:
    print("  %-24s 残留=%-4d 新增=%d" % (a, alltxt.count(a), alltxt.count(b)))
print("  获得 残留=%d   赚到=%d" % (alltxt.count('获得'), alltxt.count('赚到')))
print("  得分 残留=%d   计分=%d" % (alltxt.count('得分'), alltxt.count('计分')))

# 差异统计
a0 = open(SRC, 'rb').read(); b0 = open(OUT, 'rb').read()
d = [i for i in range(len(a0)) if a0[i] != b0[i]]
print("\n文件大小 %d（未变）" % len(b0))
print("差异字节 %d" % len(d))
print("md5 %s" % hashlib.md5(b0).hexdigest())
