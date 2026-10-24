# -*- coding: utf-8 -*-
"""用 9 组 (源字 -> 渲染格号) 反推 SUI 用的字符表顺序"""
import os, sys, struct, functools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _vpp import Vpp
GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def load_cl(name):
    v = Vpp(os.path.join(GAME, 'patch.vpp_pc'))
    e = v.find(name)
    if not e: return None
    b = v.read(e).decode('utf-8', 'replace')
    out = []
    for ln in b.replace('\r\n', '\n').split('\n'):
        ln = ln.strip()
        if not ln or ln.startswith('//') or '=' in ln: continue
        out.append(int(ln))
    return out

CL = load_cl('charlist_CH')
print("charlist_CH:", len(CL), "升序:", all(CL[i] < CL[i+1] for i in range(len(CL)-1)))

# 观察到的 (源字, 渲染格号) —— 来自 e066 截图，高置信
PAIRS = [('你',336), ('的',1784), ('弟',410), ('兄',967), ('们',362),
         ('需',2656), ('要',2268), ('保',354), ('护',2342)]
obs = {c: y for c, y in PAIRS}
chars = [c for c, _ in PAIRS]
print("观察:", obs)

def rank_table(keyfunc, name, desc=False):
    idx = sorted(range(len(CL)), key=lambda i: keyfunc(CL[i]), reverse=desc)
    rank = {}
    for r, i in enumerate(idx):
        if CL[i] not in rank:
            rank[CL[i]] = r
    ok = all(rank.get(ord(c)) == obs[c] for c in chars)
    return name, ok, [rank.get(ord(c)) for c in chars]

import hashlib
cands = []
cands.append(lambda cp: cp)
cands.append(lambda cp: str(cp))
cands.append(lambda cp: (len(str(cp)), cp))
cands.append(lambda cp: (len(str(cp)), str(cp)))
cands.append(lambda cp: (cp & 0xFF, cp >> 8))
cands.append(lambda cp: (cp >> 8, cp & 0xFF))
cands.append(lambda cp: bytes([cp & 0xFF, cp >> 8]))
cands.append(lambda cp: -cp)
cands.append(lambda cp: str(cp)[::-1])
cands.append(lambda cp: (cp * 2654435761) & 0xFFFFFFFF)
cands.append(lambda cp: int(hashlib.md5(str(cp).encode()).hexdigest(), 16))
cands.append(lambda cp: (cp * 31) & 0xFFFFFFFF)
cands.append(lambda cp: ((cp << 1) & 0xFFFF) | (cp >> 15))
cands.append(lambda cp: bin(cp)[::-1])
cands.append(lambda cp: (cp & 0xF, cp >> 4))
cands.append(lambda cp: (cp % 256, cp // 256))
try:
    cands.append(lambda cp: chr(cp).encode('gbk', 'replace'))
except Exception:
    pass

names = ['cp', 'str', '(len,cp)', '(len,str)', '(lo,hi)', '(hi,lo)', 'bytesLE', '-cp',
         'str_rev', 'murmur*', 'md5', '*31', 'rot16', 'bin_rev', '(low4,hi)', '(mod256,div)']
for f, n in zip(cands, names):
    for desc in (False, True):
        try:
            nm, ok, got = rank_table(f, n + (' DESC' if desc else ''), desc)
        except Exception as ex:
            continue
        if ok:
            print("!!! 命中:", nm)
        elif got and sum(1 for c in chars if got[chars.index(c)] == obs[c]) >= 3:
            print("   部分匹配(%d/9): %s %s" % (sum(1 for i, c in enumerate(chars) if got[i] == obs[c]), nm, got))
print("候选测试完毕")

# 另外: 测试 SUI 可能用的是 JPCharList / charlist_JP / charlist_SK
for nm in ['charlist_JP', 'charlist_SK', 'JPCharList']:
    other = load_cl(nm)
    if not other:
        print(nm, "无"); continue
    rank = {}
    for r, cp in enumerate(other):
        if cp not in rank: rank[cp] = r
    got = [rank.get(ord(c)) for c in chars]
    hit = sum(1 for i, c in enumerate(chars) if got[i] == obs[c])
    print("%-14s len=%-5d 匹配 %d/9  %s" % (nm, len(other), hit, got))
