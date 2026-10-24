# -*- coding: utf-8 -*-
"""双段探针：绿色段(你的弟兄们, slot 0/1/23/24/25) 写一组标记，
黑色段(需要你的保护, slot 35..40) 写另一组标记。触发后看屏幕哪段变。"""
import sys, struct, re, ctypes
sys.path.insert(0, 'F:/sr2-cn/stub'); sys.path.insert(0, 'F:/sr2-cn')
import ce_mini as C

C.CL = C.load_charlist()
C.enable_debug_privilege()
pid = C.find_pid()
if pid is None:
    print('游戏未运行'); sys.exit(1)
h = C.open_process(pid); lim = C.addr_limit(h)
print('pid', pid)

def LEslots(sl):
    return b''.join(struct.pack('<H', s) for s in sl)

def scan(pat, maxh=10):
    hits = []
    for base, size, prot in C.enum_regions(h, lim):
        off = 0
        while off < size:
            n = min(32 * 1024 * 1024, size - off)
            raw = C.read_mem(h, base + off, n)
            if not raw:
                break
            for m in pat.finditer(raw):
                hits.append(base + off + m.start())
                if len(hits) >= maxh:
                    return hits
            off += n
    return hits

FEAT = re.compile(re.escape(LEslots([0x5D, 0x0A8B, 0x0918, 0x0193, 0x074C, 0x01A7, 0x04C6])))
hits = scan(FEAT)
if not hits:
    print('未找到 REC1'); sys.exit(1)
slot0 = hits[0] - 34 * 2
raw = C.read_mem(h, slot0, 41 * 2)
cur = [struct.unpack_from('<H', raw, i * 2)[0] for i in range(41)]

GREEN = [0, 1, 23, 24, 25]        # 你的弟兄们
BLACK = [35, 36, 37, 38, 39, 40]  # 需要你的保护
gidx = [345, 346, 347, 348, 349]  # 绿段标记
bidx = [351, 352, 353, 354, 355, 356]  # 黑段标记
print('绿段标记 CL[345..349] = %s' % ''.join(chr(C.CL[i]) for i in gidx))
print('黑段标记 CL[351..356] = %s' % ''.join(chr(C.CL[i]) for i in bidx))
print('当前绿段:', ''.join(chr(C.CL[cur[k] - 0x20]) for k in GREEN))
print('当前黑段:', ''.join(chr(C.CL[cur[k] - 0x20]) for k in BLACK))

def wr(pos_list, idxs):
    n = 0
    for k, i in zip(pos_list, idxs):
        buf = struct.pack('<H', (i + 0x20) & 0xFFFF)
        if C.WriteProcessMemory(h, ctypes.c_void_p(slot0 + k * 2), buf, 2, None):
            n += 1
    return n

print('写入绿段 %d/5, 黑段 %d/6' % (wr(GREEN, gidx), wr(BLACK, bidx)))
raw2 = C.read_mem(h, slot0, 41 * 2)
cur2 = [struct.unpack_from('<H', raw2, i * 2)[0] for i in range(41)]
print('写后绿段:', ''.join(chr(C.CL[cur2[k] - 0x20]) for k in GREEN))
print('写后黑段:', ''.join(chr(C.CL[cur2[k] - 0x20]) for k in BLACK))
print('完整 slot 流:', ' '.join('%04X' % s for s in cur2))
