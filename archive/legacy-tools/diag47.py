# -*- coding: utf-8 -*-
# diag47: 用历史字表验证乱码映射——找满足约束的旧字表
import sys, re, struct, glob, os
sys.path.insert(0, 'F:/sr2-cn')
import sr2lib

# 约束（修正对齐后，去除冲突项）：
# 方向A: 渲染用旧序O, 记录用新序编码:  O[g] = 屏幕字  (g=新表slot-0x20)
# 方向B: 记录用旧序O编码, 渲染用新序:  O[rank(屏幕字)] = 真字  即 O[r] = true
CONS_A = {371: '任', 1836: '璨', 1035: '偶', 422: '巧', 332: '位', 2667: '雄',
          391: '亡', 1190: '位', 324: '通', 428: '匪', 2531: '冰', 2280: '挺',
          479: '拮', 581: '勾', 2357: '远', 470: '藐', 1963: '乱', 1792: '携',
          1127: '伪', 2790: '该', 478: '衡'}
# 方向B: O[rank(屏幕字)] = 真字
CONS_B = {336: '你', 1784: '的', 410: '弟', 967: '兄', 362: '们', 2656: '需',
          301: '保', 2514: '他', 543: '免', 458: '遭', 1243: '袭', 1221: '击',
          535: '去', 2491: '谈', 2234: '几', 287: '笔', 1292: '生', 354: '意',
          2342: '，', 2268: '要'}

def check(tag, chars):
    if not chars:
        return
    n = len(chars)
    a = sum(1 for g, c in CONS_A.items() if g < n and chars[g] == c)
    b = sum(1 for r, c in CONS_B.items() if r < n and chars[r] == c)
    mark = ' <<<<<<<' if max(a, b) >= 5 else ''
    print(f'{tag}: n={n} 方向A {a}/{len(CONS_A)}  方向B {b}/{len(CONS_B)}{mark}')
    if max(a, b) >= 5:
        d = CONS_A if a >= b else CONS_B
        s = min(d)
        print('   sample:', [(g, chars[g], d[g]) for g in list(d)[:6]])

# --- txt files ---
for f in [r'F:/sr2-cn/_day_2026-10-07/04_规则与数据/字表_第三方简体_charlist_CH.txt',
          r'F:/sr2-cn/_juice_fix/charlist_CH.txt']:
    if os.path.exists(f):
        t = open(f, encoding='utf-8', errors='replace').read()
        if t.strip().startswith('﻿'):
            t = t[1:]
        # format? lines of codepoints or actual chars?
        lines = t.strip().split('\n')
        if all(l.strip().isdigit() for l in lines[:5] if l.strip()):
            chars = [chr(int(l)) for l in lines if l.strip().isdigit()]
        else:
            chars = [c for c in t if not c.isspace() and c != '/']
        check(os.path.basename(f), chars)

# --- bin files ---
for f in [r'F:/sr2-cn/fontwork/charlist_final.bin', r'F:/sr2-cn/fontwork/charlist_new.bin']:
    if os.path.exists(f):
        d = open(f, 'rb').read()
        for en in ('<H', '>H'):
            vals = struct.unpack(f'{en[0]}{len(d)//2}H'.replace('{len(d)//2', ''), d[:len(d)//2*2]) if False else list(struct.unpack('<'+str(len(d)//2)+'H', d[:len(d)//2*2]))
            if all(0 < v < 0x30000 for v in vals[:50]):
                check(os.path.basename(f) + '<H', [chr(v) for v in vals if v])

# --- archive charlist_CH dirs ---
for f in glob.glob(r'F:/sr2-cn/_archive/output*/charlist_CH'):
    d = open(f, 'rb').read()
    txt = d.decode('utf-8', 'replace')
    lines = [l for l in txt.split('\n') if l.strip().isdigit()]
    if len(lines) > 100:
        check(f.split('_archive')[-1], [chr(int(x)) for x in lines])

# --- vpp backups: extract charlist_CH ---
for f in [r'F:/sr2-cn/pristine/patch.vpp_pc',
          r'F:/sr2-cn/SR2_简体中文补丁_v4/backup_original/patch.vpp_pc',
          r'F:/sr2-cn/SR2_简体中文补丁_v4/patch.vpp_pc',
          r'F:/sr2-cn/SR2_简体中文补丁_v8/patch.vpp_pc',
          r'F:/sr2-cn/SR2_简体中文补丁_v8/backup_original/patch.vpp_pc']:
    if not os.path.exists(f):
        continue
    try:
        vp = sr2lib.Vpp(f)
        e = vp.find('charlist_CH', 'txt')
        if e is None:
            print(os.path.basename(os.path.dirname(f)) + ': no charlist_CH')
            continue
        txt = vp.read(e).decode('utf-8', 'replace')
        lines = [l for l in txt.split('\n') if l.strip().isdigit()]
        check(f.split('sr2-cn')[-1], [chr(int(x)) for x in lines])
    except Exception as ex:
        print(f, 'ERR', ex)
