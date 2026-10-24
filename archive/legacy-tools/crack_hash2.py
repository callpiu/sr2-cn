"""破解 le_strings 的 key->hash：游戏 GetStringHash @0xBF2BD0。
策略：patch.vpp_pc 里找一个同时含 key 明文与哈希的表（hash 与明文共存），
或者用已知的 SFIV string hash 变体。
先扫描所有 le_strings，看桶结构，并尝试已知 SR2 hash（crc32 / jenkins / FNV / 自定义）。
另外：liquor_store lua 里 DRUG_TWIN_DESC 若在 le_strings 中被引用，说明 le_strings 存的是
   hash->文本；key 明文不在 le_strings。我们需要反查 hash。
   Juiced 的 lua 用 string key，引擎内部把 key 哈希后查 le_strings。
   试着用常见 hash 计算 'DRUG_TWIN_DESC' 并在所有 le_strings 的 8-byte hash 字段里找命中。
"""
import sys, os, struct, glob, zlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def collect_hashes(path):
    hs=set()
    try: v=Vpp(path)
    except: return hs
    for e in v.entries():
        if e['ext']!='le_strings': continue
        b=v.read(e)
        try: bc,count,oa,offs=file_offsets(b)
        except: continue
        for off in offs:
            if 0<off<=len(b)-8:
                hs.add(struct.unpack_from('<Q',b,off)[0])
    return hs

all_hashes=set()
for path in glob.glob(os.path.join(GAME,"*.vpp_pc")):
    all_hashes |= collect_hashes(path)
print("收集到的 le_strings u64 哈希数:", len(all_hashes))

key=b"DRUG_TWIN_DESC"
def try_algos():
    res={}
    res['crc32']=zlib.crc32(key)&0xffffffff
    res['crc32_be']=(zlib.crc32(key)&0xffffffff)
    # FNV1a 32
    h=0x811c9dc5
    for c in key: h^=c; h=(h*0x01000193)&0xffffffff
    res['fnv1a32']=h
    # FNV1 32
    h=0x811c9dc5
    for c in key: h=(h*0x01000193)&0xffffffff; h^=c
    res['fnv1_32']=h
    # djb2
    h=5381
    for c in key: h=((h*33)+c)&0xffffffff
    res['djb2']=h
    # sdbm
    h=0
    for c in key: h=(c+(h<<6)+(h<<16)-h)&0xffffffff
    res['sdbm']=h
    # Jenkins one-at-a-time
    h=0
    for c in key:
        h=(h+c)&0xffffffff; h=(h+(h<<10))&0xffffffff; h^=h>>6
    h=(h+(h<<3))&0xffffffff; h^=h>>11; h=(h+(h<<15))&0xffffffff
    res['jenkins_oaat']=h
    return res

hits=[]
for name,val in try_algos().items():
    for cand in (val, val, struct.pack('<Q',val) and val):
        pass
    # le_strings hash 是 u64，可能低32位=该值，或高32位=该值
    lo = val
    hi = (val<<32) & 0xffffffffffffffff
    if lo in all_hashes: hits.append((name,'low32',hex(lo)))
    if hi in all_hashes: hits.append((name,'high32',hex(hi)))
    if val in all_hashes: hits.append((name,'exact',hex(val)))
print("直接命中:", hits if hits else "无")

# 打印若干 le_strings 哈希样例，人工找规律
print("\n哈希样例(前25):")
for h in list(sorted(all_hashes))[:25]:
    print("  0x%016X  lo32=0x%08X hi32=0x%08X" % (h, h&0xffffffff, (h>>32)&0xffffffff))
