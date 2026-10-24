# -*- coding: utf-8 -*-
"""转储内存里的 ASCII u16 数组，确定字表索引基准，并检查同一位置是正确码点还是错误码点。"""
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
import ce_mini as C

C.enable_debug_privilege()
pid = C.find_pid()
h = C.open_process(pid)

PAT = b"\x20\x00\x21\x00\x22\x00\x23\x00\x24\x00\x25\x00"
hits = []
chunk = 0x400000
ov = 64
lim = C.addr_limit(h)
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
            i = data.find(PAT, st)
            if i < 0:
                break
            st = i + 1
            hits.append(rbase + pos - len(prev) + i)
            if len(hits) >= 60:
                break
        prev = data[-ov:]
        pos += want
    if len(hits) >= 60:
        break
print("ASCII u16 LE 数组候选 %d 处" % len(hits))

KEY = {"们": 0x4EEC, "你": 0x4F60, "保": 0x4FDD, "兄": 0x5144, "弟": 0x5F1F,
       "的": 0x7684, "要": 0x8981, "需": 0x9700,
       "T位": 0x4F4D, "T任": 0x4EFB, "T伪": 0x4F2A, "T巧": 0x5DE7, "T偶": 0x5076,
       "T该": 0x8BE5, "T璨": 0x74A8, "T衡": 0x8861, "T雄": 0x96C4,
       "C作": 0x4F5C, "C倒": 0x5012, "C健": 0x5065, "C像": 0x50CF}

for a in hits:
    raw = C.read_mem(h, a, 0x2000)
    if raw is None or len(raw) < 0x2000:
        continue
    arr = struct.unpack("<4096H", raw)
    # ASCII 连续段长度
    n_ascii = 0
    for k in range(95):
        if arr[k] == 0x20 + k:
            n_ascii += 1
        else:
            break
    # 找关键码点位置
    found = {}
    for nm, cp in KEY.items():
        for k in range(len(arr)):
            if arr[k] == cp:
                found[nm] = k
                break
    # 是否还有非 ASCII 内容
    nz = sum(1 for v in arr if v != 0)
    print("\n0x%08X  ascii连排=%d  非零u16=%d/4096" % (a, n_ascii, nz))
    print("   码点位置: %s" % (found,))
    if n_ascii >= 90 and nz > 2000:
        # 像是字表：打印 320..400 区间
        seg = arr[320:400]
        print("   [320:400] = %s" % " ".join("%04X" % v for v in seg))
        # 与正确字表比对
        import re
        sys.path.insert(0, r"F:/sr2-cn")
        import sr2lib as S
        G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
        vp = S.Vpp(os.path.join(G, "patch.vpp_pc"))
        clbuf = vp.read(vp.find("charlist_CH", "txt"))
        CL = [int(x) for x in re.findall(rb"\d+", clbuf)]
        # 找基准：arr[k] == CL[0]=32 且 arr[k+1]==33...
        base = None
        for k in range(0, 200):
            if arr[k] == 32 and arr[k + 1] == 33 and arr[k + 2] == 34:
                base = k
                break
        if base is not None:
            same = sum(1 for i in range(min(2795, 4096 - base)) if arr[base + i] == CL[i])
            print("   ★ 基准 base=%d, 与正确字表相同项=%d/2795" % (base, same))
            if same < 2795:
                diff = [(i, CL[i], arr[base + i]) for i in range(min(2795, 4096 - base)) if arr[base + i] != CL[i]]
                print("     前10处差异(idx, 正确, 实际): %s" % diff[:10])

C.k32.CloseHandle(h)
