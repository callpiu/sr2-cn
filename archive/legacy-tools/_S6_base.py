# -*- coding: utf-8 -*-
import sys, struct, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(GAME + r"\patch.vpp_pc")
raw = pv.read(pv.find("static_CH"))
rawcl = open(r'F:\sr2-cn\_cur_charlist.txt', 'rb').read()
m = re.search(rb'count=(\d+)\r?\n', rawcl)
cl = [int(x) for x in re.findall(rb'\d+', rawcl[m.end():])]
pos = {cp: i + 1 for i, cp in enumerate(cl)}   # slot = index+1 ?
pos0 = {cp: i for i, cp in enumerate(cl)}
print("charlist len", len(cl))

SUBJ = {403:'你',1868:'的',1067:'弟',454:'兄',364:'们',2699:'需',2328:'要',423:'保',1222:'护'}
HUD  = {1887:'直',582:'升',1447:'机',1977:'突',511:'击',1004:'已',911:'完',1178:'成',440:'停',2708:'靠'}
print("--- charlist index of expected char ---")
for grp, d in (('SUBJ', SUBJ), ('HUD', HUD)):
    for slot, ch in d.items():
        idx1 = pos.get(ord(ch)); idx0 = pos0.get(ord(ch))
        print("%s slot=%4d ch=%s idx0=%s idx0+1=%s diff(slot-idx0)=%s" %
              (grp, slot, ch, idx0, idx1, None if idx0 is None else slot - idx0))
