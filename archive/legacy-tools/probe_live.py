# -*- coding: utf-8 -*-
"""免重启内存探针：直接改 REC1 的 5 个显示位 slot。

用法:
    python probe_live.py locate          # 定位 REC1 内存副本
    python probe_live.py set <i0> <i1> <i2> <i3> <i4>
                                        # 把显示位 0,1(你的) 23,24,25(弟兄们) 的
                                        # slot 设为 charlist 索引 i0..i4 (自动+0x20)
    python probe_live.py restore         # 恢复磁盘原文
    python probe_live.py readbuf         # 读渲染缓冲（搜最新 5 字串）
"""
import sys, struct, re, time
sys.path.insert(0, "F:/sr2-cn/stub")
sys.path.insert(0, "F:/sr2-cn")
import ce_mini as C

C.enable_debug_privilege()
pid = C.find_pid()
h = C.open_process(pid)
lim = C.addr_limit(h)

# REC1 磁盘 slot 流（40 个 slot）
SLOT0 = [0x0193, 0x074C] + [0x005B, 0x0066, 0x006F, 0x0072, 0x006D, 0x0061, 0x0074,
                            0x005D, 0x005B, 0x0063, 0x006F, 0x006C, 0x006F, 0x0072,
                            0x003A, 0x0067, 0x0072, 0x0065, 0x0065, 0x006E, 0x005D] + \
        [0x042B, 0x01C6, 0x016C] + \
        [0x005B, 0x002F, 0x0066, 0x006F, 0x0072, 0x006D, 0x0061, 0x0074, 0x005D] + \
        [0x0A8B, 0x0918, 0x0193, 0x074C, 0x01A7, 0x04C6]
# 显示位（渲染缓冲"你的弟兄们"对应的 slot 下标）
DISP = [0, 1, 23, 24, 25]


def le_slots(sl):
    return b"".join(struct.pack("<H", s) for s in sl)


def locate():
    """特征 = [/format] 后跟 需要你的保护（REC1 独有）"""
    pat = re.escape(le_slots([0x5D, 0x0A8B, 0x0918, 0x0193, 0x074C, 0x01A7, 0x04C6]))
    hits = []
    for base, size, prot in C.enum_regions(h, lim):
        off = 0
        while off < size:
            n = min(32 * 1024 * 1024, size - off)
            raw = C.read_mem(h, base + off, n)
            if not raw:
                break
            for m in re.finditer(pat, raw):
                hits.append(base + off + m.start())
            off += n
    return hits


def verify(addr_fe):
    # 特征流从 slot34('[/format]' 的 ']') 开始
    start = addr_fe - 34 * 2
    raw = C.read_mem(h, start, len(SLOT0) * 2)
    cur = [struct.unpack_from("<H", raw, i * 2)[0] for i in range(len(SLOT0))]
    ok = all(a == b for a, b in zip(cur, SLOT0))
    return start, cur, ok


def write_slots(start, idxs):
    """idxs: 5 个 charlist 索引，写到 DISP 位置"""
    for k, i in zip(DISP, idxs):
        slot = (i + 0x20) & 0xFFFF
        buf = struct.pack("<H", slot)
        written = ctypes.c_size_t(0) if False else None
        C.WriteProcessMemory(h, ctypes.c_void_p(start + k * 2), buf, 2, None)


import ctypes


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "locate"
    hits = locate()
    print("REC1 内存副本: %d 处 %s" % (len(hits), ["0x%X" % x for x in hits]))
    if not hits:
        return
    a = hits[0]
    start, cur, ok = verify(a)
    print("记录起始 0x%X  与磁盘原文一致: %s" % (start, ok))
    if not ok:
        print("!! 当前内容已被改过，列出差异:")
        for i, (x, y) in enumerate(zip(cur, SLOT0)):
            if x != y:
                print("   slot%-3d mem=%04X disk=%04X" % (i, x, y))
    if cmd == "locate":
        return
    if cmd == "restore":
        for k in DISP:
            C.WriteProcessMemory(h, ctypes.c_void_p(start + k * 2),
                                 struct.pack("<H", SLOT0[k]), 2, None)
        _, cur2, ok2 = verify(a)
        print("已恢复原文, 一致=%s" % ok2)
        return
    if cmd == "set":
        idxs = [int(x) for x in sys.argv[2:7]]
        assert len(idxs) == 5
        for k, i in zip(DISP, idxs):
            C.WriteProcessMemory(h, ctypes.c_void_p(start + k * 2),
                                 struct.pack("<H", (i + 0x20) & 0xFFFF), 2, None)
        _, cur2, _ = verify(a)
        print("已写入, 显示位现为:",
              "".join(chr(C.CL[s - 0x20]) for s in [cur2[k] for k in DISP]))
        return
    if cmd == "readbuf":
        return


if __name__ == "__main__":
    main()
