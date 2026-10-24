import sys, struct, zlib
# known: display_name PISTOL_AMMO -> text 手枪弹药 -> hash 0xa4443217 (from static_CH record)
# test candidate hash functions
names={"PISTOL_AMMO":0xa4443217,"RIFLE_AMMO":0x5f74328a,"SHOTGUN_AMMO":0x68167528,
       "SMG_AMMO":0xc7a9987d,"SNIPER_AMMO":0x921ffa90,"RPG_AMMO":0x64630880}
def crc32u(s): return zlib.crc32(s.encode())&0xFFFFFFFF
def djb2(s):
    h=5381
    for c in s.encode(): h=((h*33)+c)&0xFFFFFFFF
    return h
def djb2x(s):
    h=5381
    for c in s.encode(): h=((h*33)^c)&0xFFFFFFFF
    return h
def sdbm(s):
    h=0
    for c in s.encode(): h=(c+(h<<6)+(h<<16)-h)&0xFFFFFFFF
    return h
for fn in [crc32u,djb2,djb2x,sdbm]:
    ok=all(fn(n)==h for n,h in names.items())
    print(f"{fn.__name__}: {'ALL MATCH' if ok else 'no'}  e.g. PISTOL_AMMO -> {fn('PISTOL_AMMO'):#010x} (want {names['PISTOL_AMMO']:#010x})")
