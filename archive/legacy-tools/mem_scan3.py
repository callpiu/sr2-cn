# -*- coding: utf-8 -*-
"""内存扫描 v3 —— 修复相对偏移 bug（锚点偏移改为相对于最小索引锚点，基准无关）。
正对照必须命中，否则扫描链仍无效。"""
import sys, os, struct, time, re
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
import ce_mini as C
import sr2lib as S

C.enable_debug_privilege()
pid = C.find_pid()
h = C.open_process(pid)
lim = C.addr_limit(h)

CORRECT = {332: 0x4EEC, 371: 0x4F60, 391: 0x4FDD, 422: 0x5144, 1035: 0x5F1F,
           1190: 0x62A4, 1836: 0x7684, 2296: 0x8981, 2667: 0x9700}
WRONG = {332: 0x4F4D, 371: 0x4EFB, 391: 0x4F2A, 422: 0x5DE7, 1035: 0x5076,
         1190: 0x8BE5, 1836: 0x74A8, 2296: 0x8861, 2667: 0x96C4}
COMMON = {332: 0x4F5C, 359: 0x5012, 371: 0x5065, 390: 0x50CF, 1003: 0x5FD7,
          1158: 0x633D, 1804: 0x76EF, 2264: 0x91CC, 2635: 0x9664}

# 两锚点近距离对（用于快速过滤 + 基准无关）
def scan_array(pairs, stride, endian, label, results, maxhits=80):
    fmt = ("<" if endian == "LE" else ">") + ("H" if stride == 2 else "I")
    items = sorted(pairs.items())
    i0 = items[0][0]
    base_b = struct.pack(fmt, items[0][1])
    rest = [((i - i0) * stride, struct.pack(fmt, cp)) for i, cp in items[1:]]
    chunk = 0x400000
    ov = 1 << 16
    for rbase, size, prot in C.enum_regions(h, lim):
        pos = 0
        prev = b""
        while pos < size:
            want = min(chunk, size - pos)
            raw = C.read_mem(h, rbase + pos, want)
            if raw is None:
                pos += want
                prev = b""
                continue
            data = prev + raw
            st = 0
            while True:
                i = data.find(base_b, st)
                if i < 0:
                    break
                st = i + 1
                if all(data[i + off:i + off + len(b)] == b for off, b in rest):
                    results.append((label, rbase + pos - len(prev) + i, prot))
                    if len(results) >= maxhits:
                        return
            prev = data[-ov:]
            pos += want

t0 = time.time()
res = []
for name, pairs in (("CORRECT", CORRECT), ("WRONG", WRONG), ("COMMON", COMMON)):
    for stride in (2, 4):
        for en in ("LE", "BE"):
            before = len(res)
            scan_array(pairs, stride, en, "%s_%s_%d" % (name, en, stride), res)
            print("  %-8s stride%d %s -> +%d 处 (累计%d, %.0fs)"
                  % (name, stride, en, len(res) - before, len(res), time.time() - t0))

print("\n=== 命中 %d 处 ===" % len(res))
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
vp = S.Vpp(os.path.join(G, "patch.vpp_pc"))
CL = [int(x) for x in re.findall(rb"\d+", vp.read(vp.find("charlist_CH", "txt")))]
CP2I = {cp: i for i, cp in enumerate(CL)}
for lb, a, prot in res:
    raw = C.read_mem(h, a, 0x100)
    if raw is None:
        continue
    # 判断基准：该地址存的码点对应字表哪个 idx
    v0 = struct.unpack_from("<H" if lb.endswith("_LE_2") or "_LE_" in lb else ">H", raw, 0)[0] if "_2" in lb else None
    info = ""
    if raw[1] == 0 and raw[0] != 0:      # LE 形态
        vals = struct.unpack("<128H", raw[:256])
        info = "LE值[0:6]=%s" % [hex(v) for v in vals[:6]]
        if vals[0] in CP2I:
            info += "  base=字表idx%d" % CP2I[vals[0]]
    elif raw[0] == 0 and raw[1] != 0:
        vals = struct.unpack(">128H", raw[:256])
        info = "BE值[0:6]=%s" % [hex(v) for v in vals[:6]]
        if vals[0] in CP2I:
            info += "  base=字表idx%d" % CP2I[vals[0]]
    print("   %-20s 0x%08X prot=0x%-3X %s" % (lb, a, prot, info))

print("\n总耗时 %.0f 秒" % (time.time() - t0))
C.k32.CloseHandle(h)
