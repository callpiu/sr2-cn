# -*- coding: utf-8 -*-
import sys, os, hashlib
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp, parse_charlist

def get_cl(path, label):
    v = Vpp(path)
    for e in v.entries():
        if (e["name"] or "") == "charlist_CH":
            raw = v.read(e)
            print("\n[%s] charlist_CH.%s  %d B md5=%s" % (label, e["ext"], len(raw), hashlib.md5(raw).hexdigest()[:12]))
            try:
                cps = parse_charlist(raw)
                print("   解析出 %d 个码位" % len(cps))
                return cps, raw
            except Exception as ex:
                print("   parse_charlist 失败: %s" % ex)
                return None, raw
    print("\n[%s] 无 charlist_CH" % label)
    return None, None

print("=== pristine/patch.vpp_pc (原版) ===")
cpsA, rawA = get_cl(r"F:/sr2-cn/pristine/patch.vpp_pc", "原版")
print("=== _zip92 (最初汉化) ===")
cpsB, rawB = get_cl(r"F:/sr2-cn/_zip92/黑道圣徒2简体汉化补丁/patch.vpp_pc", "汉化")
print("=== 游戏当前 patch.vpp_pc ===")
cpsC, rawC = get_cl(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc", "当前")

IDX = [371, 1836, 1035, 422, 332, 2667, 2296, 391, 1190]
EXP = "你的弟兄们需要保护"
OBS = "任璨偶巧位雄衡伪该"

def show(cps, label):
    if cps is None: return
    print("\n%s (共 %d 字) 前 10: %s" % (label, len(cps), "".join(chr(c) for c in cps[:10])))
    s = "".join(chr(cps[i]) if i < len(cps) else "?" for i in IDX)
    print("   索引 %s -> %s" % (IDX, s))
    print("   期望: %s" % EXP)
    print("   观测: %s" % OBS)

show(cpsA, "原版 charlist")
show(cpsB, "汉化 charlist")
show(cpsC, "当前 charlist")
