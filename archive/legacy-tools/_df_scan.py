# -*- coding: utf-8 -*-
"""用 ce_mini.scan_process 全内存搜索关键特征，判定运行时字表状态。"""
import sys, struct
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"F:/sr2-cn")
import ce_mini as C

pid = C.find_pid(); h = C.open_process(pid)
print("pid", pid)

# slots: charlist 索引 + 0x20, 以 u16 BE 存
def slots_be(s, table):
    out = b""
    for ch in s:
        idx = table.index(ord(ch))
        out += struct.pack(">H", idx + 0x20)
    return out

# 载入补丁表 & 官方表
def load_table(path, skip_header):
    raw = open(path, "rb").read()
    if skip_header:
        raw = raw[raw.index(32):]
    txt = raw.decode("ascii", "ignore")
    return [int(x) for x in txt.split() if x.strip().isdigit()]

patch = load_table(r"F:\sr2-cn\_charlist_patch.txt", False) if False else None

# 尝试直接找表文件
import os
cands = []
for p in ["F:/sr2-cn/patch.vpp_pc", "F:/sr2-cn/pristine/patch.vpp_pc"]:
    if os.path.exists(p):
        cands.append(p)
print("vpp:", cands)

patterns = [
    ("CH_你的", b"\x01\x93\x07\x4c", "你(403)的(1868) BE"),
    ("CH_弟兄们", b"\x04\x2b\x01\xc6\x01\x6c", "弟(1067)兄(454)们(364) BE"),
    ("tag_green_BE", "[format][color:green]".encode("utf-16-be"), "标签 BE"),
    ("乱码_任璨_LE", "任璨".encode("utf-16-le"), "乱码串 LE"),
    ("乱码_任璨_BE", "任璨".encode("utf-16-be"), "乱码串 BE"),
    ("CH_保护", b"\x01\xa7\x04\xc6", "保(423)护(1222) BE"),
    ("MSTRINGS", b"MSTRINGS", "DFEngine 标记"),
]
res, scanned, total, dt, nreg = C.scan_process(h, patterns, C.MAX_ADDR)
print("扫了 %.0f MB，%d 区域，%.1f 秒" % (scanned / 1e6, nreg, dt))
for nm, pat, note in patterns:
    hits = res.get(nm, [])
    print("\n[%s] %s -> %d 处" % (nm, note, len(hits)))
    for a in hits[:10]:
        print("    0x%08X" % a)
