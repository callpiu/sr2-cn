# -*- coding: utf-8 -*-
"""决定性探针 3：REC1 -> 11 个 ASCII 字母，REC2 -> 22 个 ASCII 字母。

判别力
    屏幕原显示 11 个【汉字】。换成 11 个【拉丁字母】后：
      - 屏幕变成 ABCDEFGHIJK  -> 字幕来自 REC1（问题在字形映射）
      - 仍是 11 个汉字        -> 字母不可能渲染成汉字 -> 字幕不是 REC1

用 sr2patch 里已验证的解析器（file_offsets / read_units）。

用法
    python probe_ascii2.py apply
    python probe_ascii2.py restore
    python probe_ascii2.py show
"""
import os, sys, struct, shutil, datetime, hashlib

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
PATH = os.path.join(G, "patch.vpp_pc")
TARGETS = {0x84F287ED: "ABCDEFGHIJK", 0x10AF1E62: "ABCDEFGHIJKLMNOPQRSTUV"}


def load():
    v = Vpp(PATH)
    cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
    S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}
    ent = v.find("static_CH", "le_strings")
    d = bytes(v.read(ent))
    b, c, oa, offs = file_offsets(d)
    return v, S, ent, d, b, c, offs


def read_rec(d, off):
    """返回 (hash, slots)。hash 从记录头的 4 字节取（小端 u32）。"""
    id1, id2 = struct.unpack_from("<HH", d, off)
    h = (id1 << 16) | id2
    u, _ = read_units(d, off + 8)
    return h, [x for x, _ in u]


def show():
    v, S, ent, d, b, c, offs = load()
    print("static_CH: %d 字节, buckets=%d count=%d, 唯一记录=%d" %
          (ent["size"], b, c, len(set(offs))))
    print("patch md5:", hashlib.md5(open(PATH, "rb").read()).hexdigest())
    for off in [o for o in dict.fromkeys(offs) if 0 < o <= len(d) - 10]:
        h, slots = read_rec(d, off)
        if h in TARGETS:
            print("  0x%08X  %d 槽位  %r" %
                  (h, len(slots), "".join(S.get(x, "·") for x in slots)))


def apply():
    v, S, ent, d, b, c, offs = load()
    uniq = [o for o in dict.fromkeys(offs) if 0 < o <= len(d) - 10]
    # 先记录原 bucket 的 bcnt 序列
    bt = [struct.unpack_from("<II", d, 12 + i * 8)[0] for i in range(b)]
    # 重建记录体
    body = bytearray()
    rec_off = []
    for off in uniq:
        h, slots = read_rec(d, off)
        if h in TARGETS:
            slots = [ord(ch) for ch in TARGETS[h]]
        rec_off.append(len(body))
        body += struct.pack("<HH", h >> 16, h & 0xFFFF)
        for s in slots:
            body += struct.pack(">H", s)
        body += b"\x00\x00"
    HDR = 12
    BTAB = 8 * b
    ptr_abs = [HDR + BTAB + c * 4 + o for o in rec_off]
    out = bytearray()
    out += struct.pack("<IHHI", 0xA84C7F73, 1, b, c)
    idx = 0
    for bcnt in bt:
        addr = HDR + BTAB + idx * 4 if bcnt > 0 else 0
        out += struct.pack("<II", bcnt, addr)
        idx += bcnt
    assert idx == c, (idx, c)
    for p in ptr_abs:
        out += struct.pack("<I", p)
    out += body

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = PATH + ".v%s_before_asciiprobe.bak" % ts
    shutil.copy2(PATH, bak)
    v.replace_body_appended(ent, bytes(out), align=0x800)
    open(PATH, "wb").write(bytes(v.data))
    print("备份:", os.path.basename(bak))
    print("新 md5:", hashlib.md5(open(PATH, "rb").read()).hexdigest())
    print()
    show()


def restore():
    baks = sorted(f for f in os.listdir(G)
                  if f.startswith("patch.vpp_pc.v") and f.endswith("_before_asciiprobe.bak"))
    if not baks:
        print("无备份")
        return
    shutil.copy2(os.path.join(G, baks[-1]), PATH)
    print("已还原:", baks[-1])
    show()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    {"show": show, "apply": apply, "restore": restore}[cmd]()
