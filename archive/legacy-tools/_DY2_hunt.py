import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def cl(p):
    v = Vpp(p); e = v.find("charlist_CH","txt")
    t = v.read(e).decode('utf-8','replace').replace('\r','').split('\n')
    return [int(s) for s in t if s.strip().isdigit()]

nums_M = cl(os.path.join(G,"patch.vpp_pc"))            # 2795
nums_O = cl(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig") # 2838

WRONG = [0x4EFB,0x74CF,0x5076,0x5DE7,0x4F4D,0x96C4,0x8861]   # wrong chars observed on screen
RIGHT = [0x4F60,0x7684,0x5F1F,0x5144,0x4EEC,0x9700,0x8981]   # correct characters: you, de, di, xiong, men, xu, yao
idxR = [nums_M.index(x) for x in RIGHT]
print("correct index in my table:", idxR)

pats = {
 "A: my-table code+32":  b"".join(struct.pack("<H", i+32) for i in idxR),
 "B: raw unicode":       b"".join(struct.pack("<H", c) for c in RIGHT),
 "C: official-table +32": b"".join(struct.pack("<H", nums_O.index(c)+32 if c in nums_O else 0) for c in RIGHT),
 "D: wrong-char my-table +32": b"".join(struct.pack("<H", nums_M.index(c)+32) for c in WRONG),
 "E: wrong-char unicode":      b"".join(struct.pack("<H", c) for c in WRONG),
}
for k,p in pats.items(): print("  pat %s = %s" % (k, p.hex()))

targets = []
for f in ("common.vpp_pc","patch.vpp_pc","textures.vpp_pc"):
    targets.append(("VPP:"+f, os.path.join(G,f)))
root = r"G:\SteamLibrary\steamapps\common\Saints Row 2\Mods"
for dp,_,fns in os.walk(root):
    for fn in fns:
        if 'strings' in fn.lower() or 'charlist' in fn.lower():
            targets.append(("LOOSE:"+fn, os.path.join(dp,fn)))

def scan_bytes(tag, b):
    for k,p in pats.items():
        i = b.find(p)
        if i >= 0: print("  [HIT %s] %s  @%d" % (k, tag, i))

for tag, p in targets:
    if p.lower().endswith((".lua",".ini",".txt",".log")): continue
    if p.endswith("hud_msg.lua"): continue
    try:
        if os.path.isfile(p):
            b = open(p,'rb').read()
            scan_bytes("FILE:"+tag, b)
        else:
            v = Vpp(p)
            for e in v.entries():
                if 'string' in e.get('ext','') or 'string' in e['name']:
                    scan_bytes("%s:%s.%s"%(tag,e['name'],e.get('ext','')), v.read(e))
    except Exception as ex:
        print("  ERR %s %s" % (tag, ex))
print("done")
