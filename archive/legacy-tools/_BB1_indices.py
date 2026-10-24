# -*- coding: utf-8 -*-
import sys, struct
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from _vpp import Vpp
GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
gv = Vpp(GAME)
def parse_charlist(buf):
    out=[]
    for ln in buf.decode('latin-1').splitlines():
        s=ln.strip()
        if not s or s.startswith('//') or s.startswith('count'): continue
        try: out.append(int(s))
        except: pass
    return out
cl = parse_charlist(gv.read(gv.find('charlist_CH')))
inv = {}
for i,c in enumerate(cl):
    inv.setdefault(c, i)

# 正确字 -> slot ; 观察到的乱码字
pairs = [('你',403,'任'),('的',1868,'璨'),('弟',1067,'偶'),('兄',454,'巧'),
         ('们',364,'位'),('需',2699,'雄'),('要',2328,'衡'),('保',423,'伪'),('护',1222,'该')]
print('char  slot  idx=slot-32  true_idx  shown  shown_idx  shown_idx-(slot-32)')
for ch, slot, shown in pairs:
    ti = inv.get(ord(ch), -1)
    si = inv.get(ord(shown), -1)
    print(f'  {ch}   {slot:5d}  {slot-32:5d}     {ti:5d}    {shown}    {si:5d}    {si-(slot-32) if si>=0 else "NA"}')
print()
print('index_of 任 =', inv.get(ord('任')), ' 你 =', inv.get(ord('你')))
print('index_of 璨 =', inv.get(ord('璨')), ' 的 =', inv.get(ord('的')))
print('charlist[336]=', chr(cl[336]) if 336<len(cl) else '?', 'charlist[371]=', chr(cl[371]) if 371<len(cl) else '?')
print('charlist[403]=', chr(cl[403]) if 403<len(cl) else '?')
print('charlist[1784]=', chr(cl[1784]), 'charlist[1836]=', chr(cl[1836]))
print()
# 检查是否存在固定偏移 k: si = (slot) - k 或 si = (slot-32) - k
for k in range(0, 80):
    ok = all(inv.get(ord(sh),-1) == (slot-32)-k for _,slot,sh in pairs)
    if ok: print('固定偏移成立: shown_idx = (slot-32) -', k)
for k in range(0, 80):
    ok = all(inv.get(ord(sh),-1) == slot-k for _,slot,sh in pairs)
    if ok: print('固定偏移成立: shown_idx = slot -', k)
# 打印前 20 个 ASCII 之后的项，看 charlist 开头结构
print('cl[0:40] =', cl[0:40])
print('cl chars[0:40] =', ''.join(chr(c) for c in cl[0:40]))
