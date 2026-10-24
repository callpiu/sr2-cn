# -*- coding: utf-8 -*-
"""HUD 字幕乱码 - 地面真相：磁盘精确文本 + 内存缓存串精确码点。

不依赖截图认字。磁盘解出 REC1/REC2 的 slot 序列，内存读出缓存 UTF-16LE 串，
两者对齐即得精确的 slot->codepoint 映射（无转录误差）。
"""
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
import sr2lib
import ce_mini as CE
from ctypes import wintypes, byref, sizeof

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"


def hexs(b):
    return " ".join("%02X" % c for c in b)


def dec(raw):
    """slot BE 流 -> 文本"""
    out = []
    for i in range(0, len(raw) - 1, 2):
        s = struct.unpack_from(">H", raw, i)[0]
        if s == 0:
            break
        if 0x20 <= s <= 0x7E:
            out.append(chr(s))
        else:
            j = s - 0x20
            out.append(chr(cps[j]) if 0 <= j < len(cps) else "?%04X" % s)
    return "".join(out)


# ================= Part 1: 磁盘地面真相 =================
vp = sr2lib.Vpp(os.path.join(G, "patch.vpp_pc"))
clbuf = vp.read(vp.find("charlist_CH", "txt"))
cps = [int(x) for x in clbuf.decode("utf-8", "replace").split() if x.strip().isdigit()]
print("[charlist] %d 项  首=%s  尾=%s" % (len(cps), cps[:3], cps[-3:]))

sc = None
for e in vp.entries():
    if e["name"].lower() == "static_ch":
        sc = e
        break
print("[static_CH] name=%s ext=%s size=%d" % (sc["name"], sc["ext"], sc["size"]))
blob = vp.read(sc)
print("[static_CH] magic=%s len=%d" % (blob[:4].hex(), len(blob)))

RECS = [(0x84F2, 0x87ED, "REC1"), (0x10AF, 0x1E62, "REC2")]
disk = {}
for id1, id2, label in RECS:
    pat = struct.pack("<HH", id1, id2)
    st, hits = 0, []
    while True:
        i = blob.find(pat, st)
        if i < 0:
            break
        hits.append(i)
        st = i + 1
    print("\n[%s] hash=0x%08X  命中 %d 处: %s" % (label, (id1 << 16) | id2, len(hits),
                                              ["0x%X" % x for x in hits]))
    for off in hits:
        raw = blob[off + 4:off + 4 + 300]
        txt = dec(raw)
        slots = []
        for i in range(0, 240, 2):
            s = struct.unpack_from(">H", raw, i)[0]
            if s == 0:
                break
            slots.append(s)
        print("   @0x%X  文本(%d字): %s" % (off, len(txt), txt))
        print("   slots: %s" % " ".join("%04X" % s for s in slots))
        print("   term : %s" % hexs(blob[off + 4 + len(slots) * 2:off + 4 + len(slots) * 2 + 4]))
        if label not in disk:
            disk[label] = (off, txt, slots)

# ================= Part 2: 内存缓存串（精确码点） =================
print("\n" + "=" * 70)
print("Part 2: 内存缓存串")
print("=" * 70)
CE.enable_debug_privilege()
pid = CE.find_pid()
h = CE.open_process(pid)
print("[mem] pid=%d" % pid)


def prot_of(addr):
    mbi = CE.MEMORY_BASIC_INFORMATION()
    r = CE.VirtualQueryEx(h, CE.ctypes.c_void_p(addr), byref(mbi), sizeof(mbi))
    if not r:
        return None
    return mbi.Protect, mbi.State


PROT_NAME = {0x02: "RO", 0x04: "RW", 0x20: "EXEC_RO", 0x40: "EXEC_RW",
             0x80: "WC", 0x01: "NOACCESS"}
pats = [
    ("garbled5_LE", "任璨偶巧位".encode("utf-16-le"), "缓存乱码串前5字(内存实证)"),
    ("intended_LE", "你的弟兄们".encode("utf-16-le"), "正确文本(预期0命中)"),
]
res, scanned, total, dt, nreg = CE.scan_process(h, pats, CE.addr_limit(h))
for name, pat, note in pats:
    print("\n【%s】命中 %d 处  %s" % (name, len(res[name]), note))
    for a in res[name]:
        p = prot_of(a)
        print("   0x%08X  prot=%s" % (a, PROT_NAME.get(p[0], hex(p[0])) if p else "?"))

# 对每个命中 dump 大段上下文，完整解出缓存串
for a in res.get("garbled5_LE", []):
    print("\n" + "-" * 70)
    print("★ 缓存串 @0x%08X 详细上下文：" % a)
    raw = CE.read_mem(h, a - 48, 320)
    if raw is None:
        print("   读取失败")
        continue
    for off in range(0, 320, 16):
        ch = raw[off:off + 16]
        print("   %08X  %-47s  %s" % (a - 48 + off, hexs(ch),
              "".join(chr(c) if 32 <= c < 127 else "." for c in ch)))
    # 从 a-48 起按 UTF-16LE 解
    print("\n   从 0x%08X 起 UTF-16LE 解码:" % (a - 48))
    s = raw.decode("utf-16-le", "replace")
    print("   %r" % s)
    # 尝试找长度前缀：a 前 2 字节
    pre = CE.read_mem(h, a - 2, 2)
    if pre:
        ln = struct.unpack("<H", pre)[0]
        print("   a-2 长度前缀 = %d (字节) -> %d 字符" % (ln, ln // 2))
CE.CloseHandle = getattr(CE, "CloseHandle", None)
try:
    CE.k32.CloseHandle(h)
except Exception:
    pass
print("\n完成。")
