# -*- coding: utf-8 -*-
"""乱码反推：若显示字 d = CL_B[ CL_A.rev[正确字] ]，则正确字 = CL_A[ CL_B.rev[d] ]。
   对所有 (A,B) 组合试一遍。"""
import os, sys, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G  = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
PR = r"F:/sr2-cn/pristine/patch.vpp_pc"

def load_cl(buf):
    nums = [int(x) for x in re.findall(rb'\d+', buf)]
    if nums and nums[0] == len(nums) - 1: nums = nums[1:]
    rev = {}
    for i, cp in enumerate(nums): rev.setdefault(cp, i)
    return nums, rev

cn = Vpp(os.path.join(G, "patch.vpp_pc")); pv = Vpp(PR)
S = {"CH2795": load_cl(cn.read(cn.find("charlist_CH","txt")))}
for nm in ["charlist_JP","charlist_CZ","charlist_PL","charlist_RU","charlist_SK"]:
    e = cn.find(nm,"txt")
    if e: S[nm] = load_cl(cn.read(e))
S["CH2838off"] = load_cl(pv.read(pv.find("charlist_CH","txt")))

D1 = "任璨偶巧位雄衡任璨伪该"
D2 = "任璨偶巧位校衡勾远藐乱携 伪该亡位通像匪冰挺拮"
print("观测乱码 D1:", D1)
print("观测乱码 D2:", D2)

for an, (ab, ar) in S.items():
    for bn, (bb, br) in S.items():
        out1, out2 = [], []
        ok = True
        for D, out in ((D1, out1), (D2, out2)):
            for ch in D:
                if ch == ' ': out.append(' '); continue
                j = br.get(ord(ch))          # 引擎按 B 表把显示字反解成索引
                if j is None or j >= len(ab): ok = False; break
                out.append(chr(ab[j]))       # 编码时用的是 A 表
            if not ok: break
        if ok:
            t1, t2 = ''.join(out1), ''.join(out2)
            # 只打印"看起来像中文句子"的（含常见字）
            common = sum(1 for c in t1+t2 if 0x4E00 <= ord(c) <= 0x9FFF)
            if common >= 8:
                print(f"\n[A={an} 编码 / B={bn} 解码]")
                print(f"   正确1 = {t1}")
                print(f"   正确2 = {t2}")
