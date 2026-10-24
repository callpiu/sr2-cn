# -*- coding: utf-8 -*-
"""全盘搜错误字表 T_err。
硬约束（内存 dump 实测，100% 可靠）：
    T_err[332] = U+4F4D (位)
    T_err[371] = U+4EFB (任)
    T_err[391] = U+4F2A (伪)
    T_err[422] = U+5DE7 (巧)
    T_err[1035]= U+5076 (偶)
    T_err[1836]= U+74A8 (璨)
u16 连续数组时，(371-332)=39 项 => 字节间隔 78-2 = 76
"""
import sys, os, re, struct, glob, time
sys.path.insert(0, "F:/sr2-cn/stub")
sys.path.insert(0, "F:/sr2-cn")
import sr2lib as S

G = "G:/SteamLibrary/steamapps/common/Saints Row 2/"
P9 = [(332, 0x4F4D), (371, 0x4EFB), (391, 0x4F2A), (422, 0x5DE7),
      (1035, 0x5076), (1190, 0x8BE5), (1836, 0x74A8), (2296, 0x8861), (2667, 0x96C4)]


def pats(stride):
    out = []
    for en, tag in (("<", "LE"), (">", "BE")):
        a = struct.pack(en + "H", 0x4F4D)
        b = struct.pack(en + "H", 0x4EFB)
        gap = (371 - 332) * stride - stride
        out.append(("%s/s%d" % (tag, stride),
                    re.compile(re.escape(a) + b".{%d}" % gap + re.escape(b), re.S),
                    en, stride))
    return out


PATTERNS = pats(2) + pats(4)


def check(data, base_desc, out):
    for tag, pat, en, stride in PATTERNS:
        for m in pat.finditer(data):
            st = m.start()
            base = st - 332 * stride
            if base < 0:
                continue
            ok = 0
            det = []
            for i, u in P9:
                p = base + i * stride
                if p + 2 > len(data):
                    break
                v = struct.unpack_from(en + "H", data, p)[0]
                det.append(chr(v) if 32 <= v < 0xFFFE else "?")
                if v == u:
                    ok += 1
            if ok >= 4:
                out.append((base_desc, tag, base, ok, "".join(det)))
                print("   ★ %-40s [%s] 偏移 0x%X  %d/9  %s"
                      % (base_desc, tag, base, ok, "".join(det)), flush=True)


out = []
t0 = time.time()

# ---------- 1) 游戏目录散文件（含 exe/dll，完整读取） ----------
files = []
for root, dirs, fs in os.walk(G):
    for f in fs:
        p = os.path.join(root, f)
        try:
            sz = os.path.getsize(p)
        except Exception:
            continue
        if sz > 400 * 1024 * 1024:
            continue
        if f.lower().endswith((".exe", ".dll", ".bin", ".dat", ".cfg", ".ini",
                               ".txt", ".cxt", ".xtbl", ".le_strings", ".vf3_pc")):
            files.append(p)
print("散文件 %d 个" % len(files), flush=True)
for p in files:
    try:
        d = open(p, "rb").read()
    except Exception:
        continue
    check(d, os.path.relpath(p, G), out)

# ---------- 2) VPP 条目 ----------
for vn in ["patch", "common", "pegs", "city_load", "hmaps", "cutscenes", "anims"]:
    fp = G + vn + ".vpp_pc"
    if not os.path.exists(fp):
        continue
    print("== VPP %s" % vn, flush=True)
    try:
        vp = S.Vpp(fp)
    except Exception as e:
        print("   打开失败", e)
        continue
    for e in vp.entries():
        sz = e.get("size") or 0
        if sz > 120 * 1024 * 1024:
            continue
        try:
            d = bytes(vp.read(e))
        except Exception:
            continue
        if len(d) < 2000:
            continue
        check(d, "%s:%s.%s" % (vn, e.get("name"), e.get("ext")), out)
    del vp

print()
print("总命中 %d 处，耗时 %.1fs" % (len(out), time.time() - t0))
for o in out:
    print("   ", o)
