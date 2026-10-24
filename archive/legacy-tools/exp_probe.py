"""★决定性实验（简洁版）★：不改图集，只改 common vf3 里两个候选索引的 U/V，
把它们指向两个【极易辨认】的现有汉字字形。进游戏一看就知道取哪个。

  徒 的字位候选： idx1058（徒自己） vs idx1026（建）
  录：             idx1045（录自己） vs idx1013（底）
  弹：             idx1041（弹自己） vs idx1009（床）

做法：把"目标自己"的索引指成 '山' 的字形；把"坏字"的索引指成 '川' 的字形。
  ⇒ 界面上「徒」显示 山 ⇒ 取 1058（我的修法方向对）
  ⇒ 界面上「徒」显示 川 ⇒ 取 1026（游戏确实走了坏路径，我的重指应该有效才对）
  ⇒ 显示别的字       ⇒ 取的是第三个未知索引，需要继续找
"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
COMMON = os.path.join(GAME, "common.vpp_pc")
OUT_C = r"F:\sr2-cn\_fix_candidates\exp_common.vpp_pc"

vp = Vpp(os.path.join(GAME, "patch.vpp_pc"))
cl = [int(s) for s in vp.read(vp.find("charlist_CH","txt")).decode('utf-8').split('\n') if s.strip().isdigit()]
c2s = {}
for i, cp in enumerate(cl):
    if cp >= 0x100: c2s.setdefault(chr(cp), i + 0x20)

vc = Vpp(COMMON)
e = vc.find("fnt_chinese","vf3_pc"); co = vc.data_start + e['body']
NC = struct.unpack_from('<I', vc.data, co + 0x08)[0]
def cuv(i): return (struct.unpack_from('<i', vc.data, co+0xAF6C+i*4)[0],
                    struct.unpack_from('<i', vc.data, co+0xDB18+i*4)[0])

SHAN = c2s['山'] - 0x20   # 山 的 vf3 索引
CHUAN = c2s['火'] - 0x20  # 火（代替川）
print("山 vf3 idx=%d U/V=%s" % (SHAN, cuv(SHAN)))
print("火 vf3 idx=%d U/V=%s" % (CHUAN, cuv(CHUAN)))

# 每对：正常位 -> 山；坏位 -> 川
PAIRS = [
    ("徒", 1058, 1026),
    ("录", 1045, 1013),
    ("弹", 1041, 1009),
]
print("\n实验布置：")
for ch, ok_i, bad_i in PAIRS:
    struct.pack_into('<i', vc.data, co+0xAF6C+ok_i*4,  cuv(SHAN)[0])
    struct.pack_into('<i', vc.data, co+0xDB18+ok_i*4,  cuv(SHAN)[1])
    struct.pack_into('<i', vc.data, co+0xAF6C+bad_i*4, cuv(CHUAN)[0])
    struct.pack_into('<i', vc.data, co+0xDB18+bad_i*4, cuv(CHUAN)[1])
    print("  %r: vf3[%d]→山  vf3[%d]→火" % (ch, ok_i, bad_i))

os.makedirs(os.path.dirname(OUT_C), exist_ok=True)
vc.save(OUT_C)
print("\n写出", OUT_C, "md5", hashlib.md5(open(OUT_C,'rb').read()).hexdigest())
print("\n★ 进游戏看「圣徒街区」的徒字，显示的是【山】还是【火】？")
print("★ 这是决定性证据，能一次确定游戏走的是哪个索引。")