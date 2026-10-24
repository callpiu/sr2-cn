# -*- coding: utf-8 -*-
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

cn = Vpp(os.path.join(G, "patch.vpp_pc"))
pv = Vpp(PR)
sets = {
 "CH2795": load_cl(cn.read(cn.find("charlist_CH", "txt"))),
 "CH_official": load_cl(pv.read(pv.find("charlist_CH", "txt"))),
}
D1 = "任璨偶巧位雄衡任璨伪该"
D2 = "任璨偶巧位校衡勾远藐乱携 伪该亡位通像匪冰挺拮"

for nm, (body, rev) in sets.items():
    print(f"===== 用 {nm} ({len(body)}) 反推 =====")
    for tag, D in (("D1", D1), ("D2", D2)):
        bs = []
        ok = True
        for ch in D:
            i = rev.get(ord(ch))
            if i is None: ok = False; break
            bs.append(i + 0x20)
        if not ok:
            print(f"  {tag}: 有字符不在 charlist 中"); continue
        raw = bytes(b & 0xFF for b in bs)
        print(f"  {tag} 反推字节: {' '.join(f'{b:02X}' for b in raw)}")
        for enc in ("utf-8", "gbk", "big5", "utf-16-be", "utf-16-le"):
            try:
                t = raw.decode(enc)
                print(f"      {enc:9s} -> {t!r}   <== 合法!")
            except Exception:
                pass
