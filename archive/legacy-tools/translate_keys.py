import sys, os, re, struct, shutil
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
W = r"F:\sr2-cn"; G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
J = os.path.join(G,"Mods","JUICED - Strings")
OUT = os.path.join(W,"_juice_fix","out4")

# ---- 检查新 key 的中文用字是否都在第三方字表里 ----
v = Vpp(os.path.join(W,"_juice_fix","patch.vpp_pc"))
CPS = set(int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit())
CAND = {
 "J_MOUSEFOV":   ["随FOV缩放鼠标灵敏度","鼠标灵敏度随FOV缩放","FOV影响鼠标灵敏度","鼠标灵敏度跟随FOV"],
 "J_FINEAIMONLY":["仅精确瞄准时","仅精细瞄准时","只在精细瞄准","仅瞄准模式"],
 "J_FOVMULT":    ["FOV倍率","FOV倍数","视野倍率","视场倍率"],
}
for k, vs in CAND.items():
    print("[%s]" % k)
    for s in vs:
        miss = [c for c in s if ord(c)>0x100 and ord(c) not in CPS]
        print("   %-22s %s" % (s, "OK" if not miss else "缺 "+"".join(miss)))
print()
# ---- 造两个版本：Chinese 翻译版 + width 20 备选 ----
ch = open(os.path.join(OUT,"juiced_CH.cxt"), encoding="utf-8").read()
CH = {"J_MOUSEFOV":"随FOV缩放鼠标灵敏度","J_FINEAIMONLY":"仅精确瞄准时","J_FOVMULT":"FOV倍率"}
new = ch
for k, val in CH.items():
    miss=[c for c in val if ord(c)>0x100 and ord(c) not in CPS]
    if miss:
        print("跳过 %s（缺 %s）" % (k,"".join(miss))); continue
    new = re.sub(r'(\[%s\]\r\n).*?(\r\n)' % k, r'\g<1>%s\g<2>' % val, new, count=1, flags=re.S)
open(os.path.join(OUT,"juiced_CH.cxt"),"wb").write(new.encode("utf-8"))
print("中文版 .cxt 写出 %d 字节" % len(new.encode("utf-8")))
for m in re.finditer(r'\[(J_MOUSEFOV|J_FINEAIMONLY|J_FOVMULT)\]\r\n(.*?)\r\n', new, re.S):
    print("   [%s] = %r" % (m.group(1), m.group(2)))
print()
# width 20 备选
SRC = os.path.join(W,"_juice_fix","patch.vpp_pc")
v2 = Vpp(SRC)
vf3 = bytearray(v2.read(v2.find("fnt_chinese","vf3_pc")))
for i in range(95):
    off = 0xD0 + i*16
    struct.pack_into("<h", vf3, off, 20)
    struct.pack_into("<h", vf3, off+12, 20)
v2.replace_body_appended(v2.find("fnt_chinese","vf3_pc"), bytes(vf3))
os.makedirs(os.path.join(W,"_juice_fix","out5"), exist_ok=True)
v2.save(os.path.join(W,"_juice_fix","out5","patch.vpp_pc"))
print("备选版 width=20 写出: %s" % os.path.join(W,"_juice_fix","out5","patch.vpp_pc"))
