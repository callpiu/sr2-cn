# -*- coding: utf-8 -*-
# 用所有语言的 charlist 反解坏记录的 slot，找哪个字表能产生截图乱码
import struct, sys, glob
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
REC1 = [0x193,0x74c,0x42b,0x1c6,0x16c,0xa8b,0x918,0x1a7,0x4c6]  # 你的弟兄们需要保护(9字)
REC2 = [0x193,0x74c,0x42b,0x1c6,0x16c,0x918,0x1fe,0x265,0x955,0x1f6,0x7cb,0x720,0x487,0xb06,0x1a7,0x4c6,0x164,0x16c,0x1cc,0xa03,0x908,0x1ff]
TARGET = "任璨傅巧位校衡勾远覫乱携"   # 截图记录2前12个屏字

# 收集所有 vpp 里的 charlist*
files = glob.glob(G + r"\*.vpp_pc")
charlists = {}   # name -> CPS list
for f in files:
    try:
        vp = Vpp(f)
    except Exception:
        continue
    for e in vp.entries():
        n = e['name'] or ""
        if "charlist" in n.lower():
            try:
                raw = vp.read(e)
                cps = [int(l) for l in raw.decode("utf-8", "ignore").split("\n") if l.strip().isdigit()]
                if len(cps) > 100:
                    charlists[f"{n}.{e['ext']}"] = cps
            except Exception as ex:
                print(f"  读取失败 {n}: {ex}")
print(f"找到 {len(charlists)} 个 charlist: {list(charlists)}")

def dec(cps, slots):
    N = len(cps)
    return ''.join(chr(cps[s-0x20]) if 0x20 <= s-0x20 < N else f'[{s:04X}]' for s in slots)

for n, cps in charlists.items():
    d1 = dec(cps, REC1)
    d2 = dec(cps, REC2)
    mark = " <<<< 命中!" if all(ch in TARGET for ch in d2[:12]) else ""
    print(f"\n--- {n} (N={len(cps)}){mark}")
    print(f"  REC1: {d1!r}")
    print(f"  REC2: {d2[:16]!r}")
