"""反推 SR2 字符串哈希：用 juiced_CH.cxt 的键 去撞 juiced le_strings 的 record u64 哈希。
测试多种常见算法（FNV1a/djb2/sdbm/crc32/CRC64 等）的 32/64 位变体。"""
import os, struct, glob

base = r"F:\sr2-cn\juicedsrc\Saints-Row-2-Juiced-Patch-main\Mods\JUICED - Strings"
ch_cxt = open(os.path.join(base,"juiced_CH.cxt"),'rb').read().decode('utf-8',errors='replace')
keys = []
lines = ch_cxt.split('\n')
i=0
while i < len(lines):
    if lines[i].startswith('[') and lines[i].endswith(']') and lines[i] != '':
        key = lines[i].strip()
        val = lines[i+1] if i+1 < len(lines) else ''
        keys.append((key, val))
        i += 2
    else:
        i += 1

# record 哈希（来自游戏 Mods 的 juiced_CH.le_strings）
jl = r"G:\SteamLibrary\steamapps\common\Saints Row 2\Mods\JUICED - Strings\juiced_CH.le_strings"
buf = open(jl,'rb').read()
magic,ver,buckets,count = struct.unpack_from('<IHHI',buf,0)
off_at = 16+buckets*8
rec_hashes = []
for k in range(count):
    off = struct.unpack_from('<I',buf,off_at+k*4)[0]
    if off+8 <= len(buf):
        rec_hashes.append(struct.unpack_from('<Q',buf,off)[0])
print("cxt keys(%d):"%len(keys), [k for k,_ in keys][:6], "...")
print("record hashes(%d):"%len(rec_hashes), [hex(h) for h in rec_hashes[:6]])

# 测试算法
def fnv1a32(s):
    h=0x811c9dc5
    for c in s.encode('utf-8'):
        h^=c; h=(h*0x01000193)&0xffffffff
    return h
def fnv1a64(s):
    h=0xcbf29ce484222325
    for c in s.encode('utf-8'):
        h^=c; h=(h*0x100000001b3)&0xffffffffffffffff
    return h
def djb2(s):
    h=5381
    for c in s.encode('utf-8'):
        h=((h*33)+c)&0xffffffff
    return h
def sdbm(s):
    h=0
    for c in s.encode('utf-8'):
        h=((c+h*65599))&0xffffffff
    return h

algos = {'fnv1a32':fnv1a32,'fnv1a64':fnv1a64,'djb2':djb2,'sdbm':sdbm}
for name,fn in algos.items():
    matched=0
    for key,_ in keys:
        v=fn(key)
        if name.endswith('64'):
            if v in rec_hashes: matched+=1
        else:
            if (v&0xffffffff) in [h&0xffffffff for h in rec_hashes]: matched+=1
    print("  %s 命中 %d/%d keys" % (name, matched, len(keys)))

# 另外：尝试把整个 key（带[]）或不含[] 都试
print("\n--- 变体：去[] 后 ---")
import re
def keyvar(key):
    return key.strip('[]')
for name,fn in algos.items():
    matched=0
    for key,_ in keys:
        v=fn(keyvar(key))
        if name.endswith('64'):
            if v in rec_hashes: matched+=1
        else:
            if (v&0xffffffff) in [h&0xffffffff for h in rec_hashes]: matched+=1
    print("  %s(strip[]) 命中 %d/%d" % (name, matched, len(keys)))
