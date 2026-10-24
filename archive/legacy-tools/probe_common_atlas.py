# -*- coding: utf-8 -*-
"""查 common 图集真实尺寸 + vf3 头字段 + U/V 行结构细节。"""
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
import sr2lib as S

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def load_vf3(path_vpp, name="fnt_chinese", ext="vf3_pc"):
    v = S.Vpp(os.path.join(G, path_vpp))
    e = v.find(name, ext)
    buf = bytes(v.read(e))
    N = struct.unpack_from("<I", buf, 8)[0]
    U = list(struct.unpack_from("<%dI" % N, buf, 0xBC + 16 * N))
    V = list(struct.unpack_from("<%dI" % N, buf, 0xBC + 16 * N + 4 * N))
    return buf, N, U, V

cbuf, cN, cU, cV = load_vf3("common.vpp_pc")
pbuf, pN, pU, pV = load_vf3("patch.vpp_pc")

print("=== common vf3 头部 0xBC 字节 ===")
print(cbuf[:0xBC].hex(" "))
print("作为 u32 x47:")
h32 = struct.unpack_from("<47I", cbuf, 0)
for i in range(0, 47, 8):
    print("  +%3d: %s" % (i * 4, h32[i:i + 8]))

print("\n=== patch vf3 头部前 64 字节（对照）===")
print(pbuf[:64].hex(" "))

print("\n=== common U/V 行结构 ===")
resets = [i for i in range(1, cN) if cU[i] < cU[i - 1]]
print("全部 %d 个重置点: %s" % (len(resets), resets))
for r in resets[:6]:
    print("  行首 idx=%-5d U=%-5d V=%-5d  下一行U差=%s" % (r, cU[r], cV[r], cU[r + 1] - cU[r] if r + 1 < cN else "-"))
print("  U[115:135]=%s" % cU[115:135])
print("  V[115:135]=%s" % cV[115:135])
print("  U[0:8]=%s  V[0:8]=%s" % (cU[:8], cV[:8]))
# 行距
print("  行y值: %s" % [cV[r] for r in resets[:8]])
print("  最后一行: idx=%d U=%d V=%d, 该行字数=%d" % (resets[-1], cU[resets[-1]], cV[resets[-1]], cN - resets[-1]))

print("\n=== patch 行结构（对照）===")
presets = [i for i in range(1, pN) if pU[i] < pU[i - 1]]
print("重置点: %s ... 共%d" % (presets[:6], len(presets)))
print("行y值: %s" % [pV[r] for r in presets[:6]])

# ---------------------------------------------------------- GEKV 描述符搜索
print("\n=== GEKV 描述符搜索 ===")
def scan_gekv(path, label):
    try:
        data = open(path, "rb").read()
    except Exception as ex:
        print("  %s 读取失败: %s" % (label, ex))
        return
    pos = 0
    n = 0
    while True:
        i = data.find(b"GEKV", pos)
        if i < 0:
            break
        pos = i + 1
        n += 1
        if n > 400:
            print("  %s: GEKV 超过400个，停止" % label)
            break
        # 尝试解析: magic(4) size(4) dataSize(4) ... w/h/fmt ... name
        try:
            sz = struct.unpack_from("<I", data, i + 4)[0]
            if not (20 <= sz <= 200):
                continue
            fields = struct.unpack_from("<%dI" % ((sz - 4) // 4), data, i + 4)
            # 找 2048/4096/1024 样的宽高对
            w = h = fmt = None
            for k in range(len(fields) - 2):
                if fields[k] in (256, 512, 1024, 2048, 4096) and fields[k + 1] in (256, 512, 1024, 2048, 4096):
                    w, h = fields[k], fields[k + 1]
                    fmt = fields[k + 2] if k + 2 < len(fields) else None
                    break
            nm = data[i + sz:i + sz + 48].split(b"\x00")[0].decode("ascii", "replace")
            if w and ("chinese" in nm.lower() or "fnt" in nm.lower()):
                print("  %s @0x%X size=%d w=%d h=%d fmt=%s name=%r" % (label, i, sz, w, h, fmt, nm))
        except Exception:
            pass
    print("  %s: GEKV 共 %d 处" % (label, n))

for p, lb in ((os.path.join(G, "pegs.vpp_pc"), "pegs.vpp_pc"),
              (os.path.join(G, "common.vpp_pc"), "common.vpp_pc")):
    if os.path.exists(p):
        scan_gekv(p, lb)

# textures.vpp_pc 太大，只搜前 32MB（描述符通常在头部元数据区）
print("\n=== textures.vpp_pc GEKV（只搜前 64MB）===")
with open(os.path.join(G, "textures.vpp_pc"), "rb") as f:
    head = f.read(64 * 1024 * 1024)
pos, n = 0, 0
while True:
    i = head.find(b"GEKV", pos)
    if i < 0:
        break
    pos = i + 1
    n += 1
    try:
        sz = struct.unpack_from("<I", head, i + 4)[0]
        if not (20 <= sz <= 200):
            continue
        fields = struct.unpack_from("<%dI" % ((sz - 4) // 4), head, i + 4)
        w = h = fmt = None
        for k in range(len(fields) - 2):
            if fields[k] in (256, 512, 1024, 2048, 4096) and fields[k + 1] in (256, 512, 1024, 2048, 4096):
                w, h = fields[k], fields[k + 1]
                fmt = fields[k + 2] if k + 2 < len(fields) else None
                break
        nm = head[i + sz:i + sz + 48].split(b"\x00")[0].decode("ascii", "replace")
        if w:
            print("  textures @0x%X size=%d w=%d h=%d fmt=%s name=%r" % (i, sz, w, h, fmt, nm))
    except Exception:
        pass
print("  textures 前64MB 内 GEKV 共 %d 处" % n)
