# -*- coding: utf-8 -*-
"""把 common.vpp_pc 里 fnt_body_n / fnt_body_s 的 vf3 换成 fnt_chinese 的表
（字幕走 thin_overlay -> fnt_body_n，N=224 只有 ASCII，装不下汉字 -> 乱码）
"""
import sys, struct, hashlib, shutil, os
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
CN = os.path.join(G, "common.vpp_pc")
BAK = r"F:/sr2-cn/_backup_CN/common.vpp_pc.before_bodyfont"

v = Vpp(CN, load_all=True)
data = bytearray(v.data)

# 1) 先看现状
print("=== 现状 ===")
for nm in ("fnt_chinese", "fnt_body_n", "fnt_body_s", "fnt_head_n", "fnt_bodyital_n"):
    e = v.find(nm, "vf3_pc")
    if not e:
        print("  %-16s 不存在" % nm)
        continue
    b = v.read(e)
    N = struct.unpack_from("<I", b, 8)[0]
    UOFF = 0xD0 + N * 16
    U = [struct.unpack_from("<i", b, UOFF + k * 4)[0] for k in range(min(N, 200))]
    gaps = sorted(set(sorted(set(U))[i + 1] - sorted(set(U))[i] for i in range(len(set(U)) - 1)))
    print("  %-16s size=%-7d N=%-6d md5=%s  U间隔=%s" % (nm, len(b), N, hashlib.md5(b).hexdigest()[:12], gaps[:5]))

src = v.find("fnt_chinese", "vf3_pc")
payload = v.read(src)
print("\n用 fnt_chinese.vf3_pc 作为替换源: size=%d md5=%s" % (len(payload), hashlib.md5(payload).hexdigest()))

# 2) 备份
if not os.path.exists(BAK):
    shutil.copy2(CN, BAK)
    print("已备份 -> %s" % BAK)

# 3) append + repoint
def replace_appended(ent, pl):
    d = data
    pad = (-len(d)) % 0x800
    d += b"\x00" * pad
    new_body = len(d) - v.ds
    d += pl
    struct.pack_into("<i", d, ent["entry_off"] + 12, new_body)
    struct.pack_into("<i", d, ent["entry_off"] + 16, len(pl))
    struct.pack_into("<i", d, 5 + 0x14F + 4, len(d))
    return len(d)

for nm in ("fnt_body_n", "fnt_body_s", "fnt_head_n", "fnt_head_s", "fnt_bodyital_n", "fnt_bodyital_s"):
    e = v.find(nm, "vf3_pc")
    if not e:
        print("  %-16s 跳过（不存在）" % nm)
        continue
    old = v.read(e)
    sz = replace_appended(e, payload)
    print("  %-16s %d -> %d 字节  (文件 %d)" % (nm, len(old), len(payload), sz))

out = r"F:/sr2-cn/_FIX/common_bodyfont.vpp_pc"
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "wb").write(bytes(data))
print("\n输出: %s  md5=%s" % (out, hashlib.md5(bytes(data)).hexdigest()))

# 4) 部署
try:
    import subprocess
    tl = subprocess.run(["tasklist"], capture_output=True, text=True, errors="ignore").stdout.lower()
except Exception:
    tl = ""
if "sr2_pc.exe" in tl:
    print("!! 游戏正在运行，未部署")
else:
    shutil.copy2(out, CN)
    print("已部署 ✓  md5=%s" % hashlib.md5(open(CN, "rb").read()).hexdigest())
print("\n回退: cp \"%s\" \"%s\"" % (BAK.replace("\\", "/"), CN.replace("\\", "/")))
