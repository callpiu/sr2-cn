# -*- coding: utf-8 -*-
"""把 257 条漏翻按类别分组，区分「该翻」与「不该翻」"""
import json, re

d = json.load(open('F:/sr2-cn/_untranslated.json', encoding='utf-8'))
rows = d['untranslated']
print('total untranslated:', len(rows))

# 分类规则
CATS = [
    ('format_tag', re.compile(r'\[format\]|\[color|\[image:|\[scale|^\s*$')),
    ('code_id', re.compile(r'^[a-z_0-9]+$')),          # projects_hood03 / hotelmarina_hood02
    ('cust_variant', re.compile(r'CUST_VARIANT_MATERIAL')),
    ('format_str', re.compile(r'^[\*%{}\[\]\s\d:+/xX\.\-]*$')),  # 纯符号模板
    ('radio', re.compile(r'Volition\s*\d|Skeeters\s*\d|KRHYME|GDHC|Ezzzy|Loops|Doo Rag|Rhombus|4\s*20',
                         re.I)),
    ('weapon', re.compile(r'Ultimax|XMAC|\bSAW\b|AR-?50|AR200|XS-2|SKR-9|12 Gauge|Kobra|Zebra|Razor|Titan\b',
                          re.I)),
    ('skill', re.compile(r'Eta Omicron|Ankh|Pi Mu Sigma|Sigma\b|HeliGood|Encanto|Serendipity',
                         re.I)),
]

buckets = {}
unclassified = []
for off, h, txt, ln in rows:
    cat = None
    for name, rx in CATS:
        if rx.search(txt):
            cat = name
            break
    if cat is None:
        unclassified.append((off, h, txt, ln))
        cat = 'TO_TRANSLATE'
    buckets.setdefault(cat, []).append((off, h, txt, ln))

for k in sorted(buckets, key=lambda x: -len(buckets[x])):
    print('%-14s %d' % (k, len(buckets[k])))

print()
print('############ 待翻译判定（TO_TRANSLATE） %d 条 ############' % len(unclassified))
seen = {}
for off, h, txt, ln in unclassified:
    key = re.sub(r'\s+\d+$', '', txt).strip()
    seen.setdefault(key, []).append(('%08X' % off, h, txt, ln))

for k in sorted(seen):
    v = seen[k]
    print('  %-32s x%d   %s' % (k, len(v), v[0][2][:60]))

json.dump({k: v for k, v in seen.items()}, open('F:/sr2-cn/_todo_shops.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)