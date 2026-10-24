# -*- coding: utf-8 -*-
# 决定性验证：引擎输出的「索引序列」是否与记录内容无关（固定序列）
import os, re, struct

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
MAGIC_VPP = bytes([0xCE, 0x0A, 0x89, 0x51, 0x04])


class Vpp:
    def __init__(self, path):
        self.d = open(path, "rb").read()
        o = 5 + 0x14F
        self.num = struct.unpack_from("<i", self.d, o)[0]
        self.len_offsets = struct.unpack_from("<i", self.d, o + 8)[0]
        self.len_filenames = struct.unpack_from("<i", self.d, o + 12)[0]
        self.len_extensions = struct.unpack_from("<i", self.d, o + 16)[0]
        self.names_at = ((0x800 + self.len_offsets) & 0xFFFFF800) + 0x800
        self.ext_at = ((self.names_at + self.len_filenames) & 0xFFFFF800) + 0x800
        self.data_start = ((self.ext_at + self.len_extensions) & 0xFFFFF800) + 0x800

    def _strz(self, base, pos):
        e = self.d.find(b"\x00", base + pos)
        return self.d[base + pos:e].decode("ascii", "replace")

    def entries(self):
        out = []
        for i in range(self.num):
            e = 0x800 + i * 28
            a, b, c, d, ln = struct.unpack_from("<IIiii", self.d, e)
            out.append(dict(name=self._strz(self.names_at, a),
                            ext=self._strz(self.ext_at, b) if b else "",
                            body=d, size=ln))
        return out

    def read(self, ent):
        p = self.data_start + ent["body"]
        return self.d[p:p + ent["size"]]

    def find(self, name, ext=None):
        for e in self.entries():
            if e["name"].lower() == name.lower() and (ext is None or e["ext"].lower() == ext.lower()):
                return e
        return None


def load_cl(v):
    b = v.read(v.find("charlist_CH", "txt"))
    m = re.search(rb"count\s*=\s*(\d+)", b)
    body = b[m.end():] if m else b
    end = body.find(b"//ENDOFFILE")
    return [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]


# 官方（当前游戏）
v_off = Vpp(os.path.join(G, "patch.vpp_pc"))
CL_OFFICIAL = load_cl(v_off)
print("官方 charlist =", len(CL_OFFICIAL), "项")

# 汉化（从备份里取）
CL_CN = None
for bak in [r"F:/sr2-cn/_backup_B/patch.vpp_pc.before_safeB",
            r"F:/sr2-cn/_backup_LUA/patch.vpp_pc.before_luafont2"]:
    if os.path.exists(bak):
        try:
            vv = Vpp(bak)
            cl = load_cl(vv)
            print("汉化 charlist (%s) = %d 项" % (os.path.basename(bak), len(cl)))
            if len(cl) != len(CL_OFFICIAL):
                CL_CN = cl
                break
        except Exception as ex:
            print("  读取失败:", ex)

# 我这边 9 组对照的 j（显示字在汉化 charlist 中的序号）
J = [336, 1784, 410, 967, 362, 2656, 2268, 336, 1784, 354, 2342]
# 我这边实际看到的显示字
MY_DISP = "任璨偶巧位雄衡任璨伪该"
# 对方文档里实际看到的显示字（官方）
THEIR_DISP = "使發光彈借歷復使發俱誘"


def dec(idx_seq, CL):
    return "".join(chr(CL[i]) if 0 <= i < len(CL) else "?" for i in idx_seq)


print("\n=== 用同一串索引 [%s] 分别解码 ===" % ", ".join(str(x) for x in J))
print("  汉化 charlist 解码 :", dec(J, CL_CN) if CL_CN else "(无汉化表)")
print("  我实际看到的显示字 :", MY_DISP)
print("  官方 charlist 解码 :", dec(J, CL_OFFICIAL))
print("  对方实际看到的显示字:", THEIR_DISP)

if CL_CN:
    ok1 = dec(J, CL_CN) == MY_DISP
    print("\n  汉化表是否吻合 =", ok1)
else:
    ok1 = None
ok2 = dec(J, CL_OFFICIAL) == THEIR_DISP
print("  官方表是否吻合 =", ok2)

print("\n=== 对照表 ===")
for k, i in enumerate(J):
    a = chr(CL_CN[i]) if CL_CN and i < len(CL_CN) else "?"
    b = chr(CL_OFFICIAL[i]) if i < len(CL_OFFICIAL) else "?"
    mine = MY_DISP[k] if k < len(MY_DISP) else " "
    theirs = THEIR_DISP[k] if k < len(THEIR_DISP) else " "
    print("  位置%-3d 索引%-6d 汉化表=%s (实际%s)   官方表=%s (实际%s) %s" %
          (k + 1, i, a, mine, b, theirs,
           "OK" if (a == mine and b == theirs) else "<<<"))
