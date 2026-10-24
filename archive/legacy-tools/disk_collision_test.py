# -*- coding: utf-8 -*-
"""磁盘决定性测试：
1) 乱码显示串「任璨偶巧位雄衡任璨伪该」是否作为某条记录的文本存在（哈希碰撞假说）
2) 锚点转换表 T（u16 数组）在全盘所有 VPP 中搜索（含 DLC/Juiced/Mods）
3) 其他「charlist 样式」十进制文本文件中是否有 T
"""
import sys, os, struct, re
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
import sr2lib as S

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# ---- charlist ----
vp = S.Vpp(os.path.join(G, "patch.vpp_pc"))
clbuf = vp.read(vp.find("charlist_CH", "txt"))
CL = [int(x) for x in re.findall(rb"\d+", clbuf)]
CP2I = {cp: i for i, cp in enumerate(CL)}
print("charlist %d 项, CL[0]=%d" % (len(CL), CL[0]))

def slots_be(text):
    out = b""
    for ch in text:
        o = ord(ch)
        out += struct.pack(">H", o if 0x20 <= o <= 0x7E else CP2I[o] + 0x20)
    return out

# 假想碰撞记录 R 的 slot 流：任璨[format][color:green]位雄衡[/format]任璨伪该
R1 = slots_be("任璨") + "[format][color:green]".encode("utf-16-be") + slots_be("位雄衡") + "[/format]".encode("utf-16-be") + slots_be("任璨伪该")
# 仅可见乱码字串（连续 5 字，防标签结构不同的情况）
R2 = slots_be("任璨偶巧位")
R3 = slots_be("位雄衡")
# 正确串 REC1 完整 slot 流（应在 static_CH 里命中，作为搜索器自检！）
R4 = slots_be("你的") + "[format][color:green]".encode("utf-16-be") + slots_be("弟兄们") + "[/format]".encode("utf-16-be") + slots_be("需要你的保护")
print("乱码碰撞串 R1 = %s" % R1.hex(" "))
print("自检串 R4     = %s" % R4[:40].hex(" "))

ANCH = [(332, 0x4F4D), (371, 0x4EFB), (391, 0x4F2A), (422, 0x5DE7),
        (1035, 0x5076), (1190, 0x8BE5), (1836, 0x74A8), (2296, 0x8861), (2667, 0x96C4)]

def scan_bin(buf, anchors, stride, endian):
    fmt = ("<" if endian == "LE" else ">") + ("H" if stride == 2 else "I")
    exp = [(a[0] * stride, struct.pack(fmt, a[1])) for a in anchors]
    f_off, f_b = exp[0]
    res, start = [], 0
    while True:
        p = buf.find(f_b, start)
        if p < 0:
            break
        start = p + 1
        if all(buf[p + off:p + off + len(b)] == b for off, b in exp[1:]):
            res.append(p)
            if len(res) >= 10:
                break
    return res

# 收集所有要搜的文件
files = []
for root, dirs, fs in os.walk(G):
    dirs[:] = [d for d in dirs if d.lower() not in ("directx", "microsoft.vc80.crt")]
    for f in fs:
        p = os.path.join(root, f)
        try:
            sz = os.path.getsize(p)
        except OSError:
            continue
        if sz < 1024:
            continue
        files.append((p, sz))
files.sort(key=lambda x: -x[1])
print("\n共 %d 个文件待搜，最大的5个: %s" % (len(files), [(os.path.basename(p), s // 1048576) for p, s in files[:5]]))

hits = {"R1": [], "R2": [], "R3": [], "R4_selfcheck": [], "T_array": []}
CH = 48 * 1024 * 1024
OV = 1 << 16
for p, sz in files:
    lb = os.path.relpath(p, G)
    big = sz > 150 * 1024 * 1024
    try:
        if big:
            with open(p, "rb") as f:
                base = 0
                prev = b""
                while True:
                    blk = f.read(CH)
                    if not blk:
                        break
                    buf = prev + blk
                    b0 = base - len(prev)
                    for key, pat in (("R1", R1), ("R2", R2), ("R3", R3), ("R4_selfcheck", R4)):
                        st = 0
                        while True:
                            i = buf.find(pat, st)
                            if i < 0:
                                break
                            hits[key].append((lb, b0 + i))
                            st = i + 1
                    for stride in (2, 4):
                        for en in ("LE", "BE"):
                            for q in scan_bin(buf, ANCH, stride, en):
                                hits["T_array"].append((lb, q, stride, en))
                    prev = buf[-OV:]
                    base += len(blk)
        else:
            buf = open(p, "rb").read()
            for key, pat in (("R1", R1), ("R2", R2), ("R3", R3), ("R4_selfcheck", R4)):
                st = 0
                while True:
                    i = buf.find(pat, st)
                    if i < 0:
                        break
                    hits[key].append((lb, i))
                    st = i + 1
            for stride in (2, 4):
                for en in ("LE", "BE"):
                    for q in scan_bin(buf, ANCH, stride, en):
                        hits["T_array"].append((lb, q, stride, en))
            # 十进制码点文本表
            try:
                t = buf.decode("utf-8", "replace")
                vals = [int(x) for x in re.findall(r"(?m)^\s*(\d+)\s*$", t)]
                if len(vals) > 2700:
                    for nm, anch in (("idx", ANCH),):
                        if all(vals[i] == c for i, c in anch):
                            hits["T_array"].append((lb, "TXT lines=%d" % len(vals), 0, ""))
            except Exception:
                pass
    except Exception as ex:
        print("  %s 读取失败: %s" % (lb, ex))

print("\n=== 结果 ===")
for k in ("R4_selfcheck", "R1", "R2", "R3", "T_array"):
    v = hits[k]
    print("【%s】%d 处" % (k, len(v)))
    for x in v[:10]:
        print("    ", x)
