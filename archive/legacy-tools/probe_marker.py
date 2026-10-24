# -*- coding: utf-8 -*-
"""探针实验：把 REC1 的 5 个显示位（slot 0,1,23,24,25 = 你的弟兄们）换成 CL[340..344]。
若转换是实时读 slot 表，内存缓冲区 0x3D33A164 会变成新字的转换结果。
"""
import sys, struct, re
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

# REC1 特征: ] 需要你的保护
FEAT = re.compile(re.escape(LEslots([0x5D, 0x0A8B, 0x0918, 0x0193, 0x074C, 0x01A7, 0x04C6])))
hits = scan(FEAT)
if not hits:
    print('未找到 REC1'); sys.exit(1)
a = hits[0]
slot0 = a - 34 * 2          # ']' 是 slot34
raw = C.read_mem(h, slot0, 41 * 2)
cur = [struct.unpack_from('<H', raw, i * 2)[0] for i in range(41)]
DISP = [0, 1, 23, 24, 25]
print('REC1 slot0 = 0x%X' % slot0)
print('当前显示位 slot:', ' '.join('%04X' % cur[k] for k in DISP))
print('当前显示位字  :', ''.join(chr(C.CL[s - 0x20]) for k in DISP for s in [cur[k]]))

NEW = [340, 341, 342, 343, 344]
newchars = ''.join(chr(C.CL[i]) for i in NEW)
print('探针新字 CL[340..344] = %s  slot = %s' % (newchars, ' '.join('%04X' % (i + 0x20) for i in NEW)))

buf = b''.join(struct.pack('<H', i + 0x20) for i in NEW)
import ctypes as _ct
n = 0
for k in DISP:
    ok = C.WriteProcessMemory(h, _ct.c_void_p(slot0 + k * 2), buf[DISP.index(k) * 2:DISP.index(k) * 2 + 2], 2, None)
    n += 1 if ok else 0
print('写入 %d/5 个 slot' % n)

raw2 = C.read_mem(h, slot0, 41 * 2)
cur2 = [struct.unpack_from('<H', raw2, i * 2)[0] for i in range(41)]
print('写后显示位 slot:', ' '.join('%04X' % cur2[k] for k in DISP))
print('写后显示位字  :', ''.join(chr(C.CL[s - 0x20]) for k in DISP for s in [cur2[k]]))
print('完整 slot 流   :', ' '.join('%04X' % s for s in cur2))
