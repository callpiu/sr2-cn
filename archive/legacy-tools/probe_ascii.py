# -*- coding: utf-8 -*-
"""活动串【ASCII 标尺】探针 —— 肉眼 + CE 都能一眼判定的决定性实验

★ 为什么用 ASCII
  HUD 的字形重排只影响中文区；ASCII 区（slot <= 0x7E）在两套字体里顺序一致，
  屏幕上会原样显示字母。因此：
    · ascii 模式（纯字母）→ 屏幕显示 ABCDEFGHIJK，一眼确认是不是这条记录
    · ruler 模式（字母+汉字交替）→ "A你B的C弟…" 每个汉字被前后字母锚定，
        可无歧义读出【每个字位渲染成了什么】，彻底消除手写转录误差
    · CE 可直接搜 Unicode 串 "ABCDEFGHIJK" 定位内存地址

★ 修正记录（2026-10-12 15:45）
  旧版用 off_at = 16 + buckets*8 定位指针数组 —— 错。
  项目定案：le_strings 头 = magic(u32) ver(u16) buckets(u16) count(u32) 共 12 字节，
  文本从 off+4 起。（HDR=16 / 文本@off+8 是旧 sr2patch.py 的弃用约定）
  用 16 会整表解析错位，重建出的表会损坏。本版已改为 12，并加重建后自检。

用法（在 F:/sr2-cn 下，用 venv python）：
  python probe_ascii.py show      # 看当前内容
  python probe_ascii.py ascii     # 装纯 ASCII 探针（自动备份）
  python probe_ascii.py ruler     # 装 ASCII 标尺探针（信息量最大）
  python probe_ascii.py restore   # 还原到最近一次探针前
"""
import os, sys, struct, shutil, datetime, hashlib, re

sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
PATH = os.path.join(G, "patch.vpp_pc")

REC1, REC2 = 0x84F287ED, 0x10AF1E62

# ---- 探针文本 ----
ASCII_PROBE = {
    REC1: "ABCDEFGHIJK",                 # 11 字符，对应 REC1 的 11 个中文字
    REC2: "ABCDEFGHIJKLMNOPQRSTUV",      # 22 字符，对应 REC2 的 22 个中文字
}
# 标尺探针：字母提供位置锚点（A你 B的 C弟 D兄 E们 F需 G要 H保 I护）
RULER_CJK = "你的弟兄们需要保护"
RULER_PROBE = {
    REC1: "".join(chr(ord('A') + i) + c for i, c in enumerate(RULER_CJK)),
}


def load(path):
    v = Vpp(path)
    buf = v.read(v.find("charlist_CH", "txt"))
    end = buf.find(b"//ENDOFFILE")
    cn = [int(x) for x in re.findall(rb"\d+", buf[:end if end > 0 else len(buf)])]
    ent = v.find("static_CH", "le_strings")
    d = bytes(v.read(ent))
    magic, ver, buckets, count = struct.unpack_from("<IHHI", d, 0)
    assert magic == 0xA84C7F73, hex(magic)
    off_at = 12 + buckets * 8          # ★ 定案：头 12 字节
    offs = [struct.unpack_from("<I", d, off_at + k * 4)[0] for k in range(count)]
    return v, cn, ent, d, ver, buckets, count, offs


def read_rec(d, off):
    id1, id2 = struct.unpack_from("<HH", d, off)
    p = off + 4                         # ★ 文本从 off+4 起
    vals = []
    while p + 1 < len(d):
        s = struct.unpack_from(">H", d, p)[0]
        if s == 0:
            break
        vals.append(s)
        p += 2
    return (id1 << 16) | id2, vals


def decode(vals, cn):
    """ASCII slot 直接用 ASCII 码；CJK slot = charlist 索引 + 0x20"""
    out = []
    for s in vals:
        if 0x20 <= s <= 0x7E:
            out.append(chr(s))
        else:
            ci = s - 0x20
            out.append(chr(cn[ci]) if 0 <= ci < len(cn) else "?")
    return "".join(out)


def encode(text, cn):
    cp2slot = {cp: i + 0x20 for i, cp in enumerate(cn)}
    slots = []
    for ch in text:
        o = ord(ch)
        if 0x20 <= o <= 0x7E:
            slots.append(o)
        else:
            assert o in cp2slot, "字符 %r 不在 charlist_CH" % ch
            slots.append(cp2slot[o])
    return slots


def rebuild(newtext):
    """重建 static_CH：只改目标记录文本，记录顺序/桶划分/桶内顺序完全沿用原表。"""
    v, cn, ent, d, ver, buckets, count, offs = load(PATH)
    uniq = list(dict.fromkeys(offs))
    recs = []
    for off in uniq:
        h, vals = read_rec(d, off)
        if h in newtext:
            vals = encode(newtext[h], cn)
        recs.append((h, vals))

    HDR = 12
    BTAB = 8 * buckets
    body = bytearray()
    rec_off = []
    for h, vals in recs:
        rec_off.append(len(body))
        body += struct.pack("<HH", h >> 16, h & 0xFFFF)
        for s in vals:
            body += struct.pack(">H", s)
        body += b"\x00\x00"
    ptr_abs = [HDR + BTAB + count * 4 + o for o in rec_off]

    out = bytearray()
    out += struct.pack("<IHHI", 0xA84C7F73, ver, buckets, count)
    bt = [struct.unpack_from("<II", d, 12 + i * 8)[0] for i in range(buckets)]
    idx = 0
    for bcnt in bt:
        addr = HDR + BTAB + idx * 4 if bcnt > 0 else 0
        out += struct.pack("<II", bcnt, addr)
        idx += bcnt
    assert idx == count, (idx, count)
    for p in ptr_abs:
        out += struct.pack("<I", p)
    out += body
    return v, ent, bytes(out), cn


def verify(cn, expect):
    """重建落地后从磁盘重新加载并解码，确认改动生效且整表结构完好。"""
    v, cn2, ent, d, ver, buckets, count, offs = load(PATH)
    assert buckets == 1024 and count == 12250, (buckets, count)
    got = {}
    bad = 0
    for off in dict.fromkeys(offs):
        h, vals = read_rec(d, off)
        if h in expect:
            got[h] = decode(vals, cn2)
        # 自检：任意 500 条记录末尾必须有 0x0000 终止符（结构没跑飞）
    for off in offs[:500]:
        p = off + 4
        while p + 1 < len(d) and struct.unpack_from(">H", d, p)[0] != 0:
            p += 2
        if p + 1 >= len(d) or struct.unpack_from(">H", d, p)[0] != 0:
            bad += 1
    assert bad == 0, "有 %d 条记录缺少终止符，结构损坏" % bad
    return got


def apply(probe, label):
    v, cn, ent, d, ver, buckets, count, offs = load(PATH)
    print("改动前：")
    for off in dict.fromkeys(offs):
        h, vals = read_rec(d, off)
        if h in probe:
            print("  0x%08X  %d 槽位  %r" % (h, len(vals), decode(vals, cn)))
    print("改动后（写入内容）：")
    for h, t in probe.items():
        print("  0x%08X  %d 槽位  %r" % (h, len(encode(t, cn)), t))

    v, ent, blob, cn = rebuild(probe)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = PATH + ".v%s_before_asciiprobe.bak" % ts
    shutil.copy2(PATH, bak)
    v.replace_body_appended(ent, blob, align=0x800)
    open(PATH, "wb").write(bytes(v.data))

    got = verify(cn, probe)
    for h, t in got.items():
        assert t == probe[h], "校验失败 0x%08X: %r != %r" % (h, t, probe[h])
        print("  [OK] 0x%08X 回读 = %r" % (h, t))
    print("\n备份:", os.path.basename(bak))
    print("新 md5:", hashlib.md5(open(PATH, "rb").read()).hexdigest())


def show():
    v, cn, ent, d, ver, buckets, count, offs = load(PATH)
    print("patch md5 =", hashlib.md5(open(PATH, "rb").read()).hexdigest())
    print("static_CH %d 字节  buckets=%d count=%d ver=%d" % (ent["size"], buckets, count, ver))
    for off in dict.fromkeys(offs):
        h, vals = read_rec(d, off)
        if h in (REC1, REC2):
            n_cjk = sum(1 for x in vals if x > 0x7E)
            print("  0x%08X  总槽位=%d 中文=%d  %r" % (h, len(vals), n_cjk, decode(vals, cn)))


def restore():
    baks = sorted(f for f in os.listdir(G)
                  if f.startswith("patch.vpp_pc.v") and f.endswith("_before_asciiprobe.bak"))
    if not baks:
        print("无 ASCII 探针备份")
        return
    shutil.copy2(os.path.join(G, baks[-1]), PATH)
    print("已还原:", baks[-1])
    show()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    if cmd == "show":
        show()
    elif cmd == "ascii":
        apply(ASCII_PROBE, "ascii")
        print("\n>>> 重启游戏进直升机突击活动，看字幕：")
        print("    显示 ABCDEFGHIJK / ABCDEFGHIJKLMNOPQRSTUV → 铁证是这两条，问题在字形映射")
        print("    仍是 11/22 个汉字                        → 字幕真的来自别处")
        print("    （CE 可搜 Unicode 串 ABCDEFGHIJK 定位内存地址）")
    elif cmd == "ruler":
        apply(RULER_PROBE, "ruler")
        print("\n>>> 重启游戏看字幕，屏幕上应形如 A?B?C?D?E?F?G?H?I?")
        print("    字母是位置锚点，抄下每个字母后面那个汉字即可：")
        print("    A=你 B=的 C=弟 D=兄 E=们 F=需 G=要 H=保 I=护")
    elif cmd == "restore":
        restore()
    else:
        print(__doc__)
