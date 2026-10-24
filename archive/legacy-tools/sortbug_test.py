# -*- coding: utf-8 -*-
"""假说：引擎对码点表排序后二分查找，但用查得索引去索引未排序的图集顺序原表。
即 rendered = J[bisect(sorted(J), cp)]  （键排序、值错位）"""
import json, bisect

J = json.load(open(r"F:\sr2-cn\_day_2026-10-07\04_规则与数据\_expected_charlist.json"))
N = len(J)
S = sorted(J)                      # 引擎若排序，得到这个（含 35 个重复）

OBS = [("们",0x4EEC,0x4F4D),("你",0x4F60,0x4EFB),("保",0x4FDD,0x4F2A),
       ("兄",0x5144,0x5DE7),("弟",0x5F1F,0x5076),("护",0x62A4,0x8BE5),
       ("的",0x7684,0x74A8),("要",0x8981,0x8861),("需",0x9700,0x96C4)]

def test(name, fn):
    hits=0; det=[]
    for ch,cp,out in OBS:
        i = fn(cp)
        got = J[i] if 0<=i<N else None
        if got==out: hits+=1; det.append(f"{ch}:OK")
        else: det.append(f"{ch}:得U+{got:04X}" if got is not None else f"{ch}:越界{i}")
    print(f"[{name:28s}] {hits}/9  " + "  ".join(det))

print("=== 变体A: 排序表二分 -> 位置用于索引未排序原表 ===")
test("J[bisect_left(S,cp)]",      lambda cp: bisect.bisect_left(S,cp))
test("J[bisect_right(S,cp)]",     lambda cp: bisect.bisect_right(S,cp))
test("J[bisect_left(S,cp)]-1",    lambda cp: bisect.bisect_left(S,cp)-1)

print("\n=== 变体B: 未排序表二分(lo/hi=n-1, 返回lo) -> 索引排序表 ===")
def bs_lo(a,k):
    lo,hi=0,len(a)-1
    while lo<=hi:
        m=(lo+hi)//2
        if a[m]<k: lo=m+1
        else: hi=m-1
    return lo
test("S[bs_lo(J,cp)]", lambda cp: (lambda i: i if 0<=i<N else -1)(bs_lo(J,cp)))
test("S[bs_lo(J,cp)]-1", lambda cp: bs_lo(J,cp)-1)

print("\n=== 变体C: 双向错位  J[S.index(cp)] 类 ===")
def jpos(cp):
    try: return J.index(cp)
    except ValueError: return -1
def spos(cp):
    try: return S.index(cp)
    except ValueError: return -1
for ch,cp,out in OBS:
    jp, sp = jpos(cp), spos(cp)
    a = J[sp] if 0<=sp<N else None
    b = S[jp] if 0<=jp<N else None
    print(f"  {ch} U+{cp:04X}: J中@{jp} S中@{sp} | J[Spos]=U+{a:04X} S[Jpos]=U+{b:04X} | 期望U+{out:04X}")

print("\n=== 变体D: 常见引擎写法 lo=0,hi=N, while(lo<hi) mid=(lo+hi)/2, 表用J, 索引用S ===")
def bs_engine(a,k):
    lo,hi=0,len(a)
    while lo<hi:
        mid=(lo+hi)//2
        if a[mid]<k: lo=mid+1
        else: hi=mid
    return lo
test("J[bs_engine(S,cp)]", lambda cp: bs_engine(S,cp))
test("S[bs_engine(J,cp)]", lambda cp: (lambda i: i if 0<=i<N else -1)(bs_engine(J,cp)))
