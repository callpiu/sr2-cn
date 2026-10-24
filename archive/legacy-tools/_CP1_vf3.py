import struct, sys
import numpy as np
sys.path.insert(0, r"F:\sr2-cn")
from _vpp import Vpp

def load(path, name, ext):
    v = Vpp(path)
    e = v.find(name, ext)
    return v.read(e) if e else None

D = r"F:\sr2-cn\_fontdump"
files = {
    "游戏内 common": load(r"G:\SteamLibrary\steamapps\common\Saints Row 2\common.vpp_pc", "fnt_chinese", "vf3_pc"),
    "游戏内 patch ": load(r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc", "fnt_chinese", "vf3_pc"),
    "官方  patch  ": open(D + r"\vf3_offi.bin", "rb").read() if __import__("os").path.exists(D + r"\vf3_offi.bin") else None,
    "作者原始     ": open(D + r"\vf3_auth.bin", "rb").read() if __import__("os").path.exists(D + r"\vf3_auth.bin") else None,
}

for tag, b in files.items():
    if b is None:
        print(tag, "无文件"); continue
    N = struct.unpack_from("<I", b, 8)[0]
    exp = 0xBC + N * 24
    print("\n===== %s  size=%d  N=%d  预期=%d %s" % (tag, len(b), N, exp, "OK" if exp == len(b) else "!!"))
    if exp != len(b):
        continue
    offU = 0xBC + N * 16
    U = np.frombuffer(b, dtype="<u4", count=N, offset=offU)
    V = np.frombuffer(b, dtype="<u4", count=N, offset=offU + N * 4)
    uu = np.unique(U); vv = np.unique(V)
    print("  U 唯一=%d  min=%d max=%d 前8=%s" % (len(uu), uu.min(), uu.max(), list(uu[:8])))
    print("  V 唯一=%d  min=%d max=%d 前8=%s" % (len(vv), vv.min(), vv.max(), list(vv[:8])))
    # 检验公式
    idx = np.arange(N)
    for tagc, fu, fv in (
        ("row-major U=1+31*(i%65)", 1 + 31 * (idx % 65), 1 + 31 * (idx // 65)),
        ("col-major U=1+31*(i//43)", 1 + 31 * (idx // 43), 1 + 31 * (idx % 43)),
    ):
        mu = int((U == fu).sum()); mv = int((V == fv).sum())
        print("   %-26s U命中=%d/%d (%.1f%%)  V命中=%d/%d (%.1f%%)" % (tagc, mu, N, 100.0*mu/N, mv, N, 100.0*mv/N))
    print("  U[0:12]=%s" % list(U[:12]))
    print("  V[0:12]=%s" % list(V[:12]))
