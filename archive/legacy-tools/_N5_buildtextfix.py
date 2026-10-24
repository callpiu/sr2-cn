# -*- coding: utf-8 -*-
"""生成「改文本」修复包 —— 零副作用方案。

原理
    已知映射 c -> d（c 是想要的字，d 是引擎会显示 c 的字形时用的输入字）
    把 le_strings 记录里的 c 的槽位换成 d 的槽位
    => 引擎显示正确字形，且【不碰图集】，其他文字不受影响

已知映射来源: pairs_cn.json（简体版实测，用户读数 100% 可靠）

用法
    python _N5_buildtextfix.py <vpp输入> <vpp输出> [--extra 出=某,意=某]
"""
import os
import re
import sys
import struct
import hashlib

sys.path.insert(0, r"F:\sr2-cn")
sys.path.insert(0, r"F:\sr2-cn\pylibs")
from sr2font import Vpp
from sr2lib import Vpp as VppLib
from sr2patch import file_offsets, read_units

OFFSET = 5

# 简体版实测映射（来自 pairs_cn.json）
MAP = {
    "你": "任", "的": "璨", "弟": "偶", "兄": "巧", "们": "位",
    "需": "雄", "要": "衡", "保": "伪", "护": "该",
    "去": "勾", "他": "亡", "击": "拮", "谈": "远", "几": "藐",
    "笔": "乱", "生": "携", "免": "匪", "遭": "冰", "袭": "挺",
    "出": None,      # 待补
    "意": None,      # 待补
}

TARGETS = (0x84F287ED, 0x10AF1E62)


def load_charlist(vpp_path):
    v = Vpp(vpp_path)
    raw = v.read(v.find("charlist_CH", "txt"))
    m = re.search(rb"count\s*=\s*(\d+)", raw)
    body = raw[m.end():] if m else raw
    end = body.find(b"//ENDOFFILE")
    return [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]


def main():
    src = sys.argv[1]
    dst = sys.argv[2]
    extra = {}
    for a in sys.argv[3:]:
        if a.startswith("--extra"):
            continue
        if "=" in a:
            k, v = a.split("=", 1)
            extra[k] = v

    mp = dict(MAP)
    mp.update(extra)
    missing = [k for k, v in mp.items() if v is None]

    cl = load_charlist(src)
    IDX = {cp: i for i, cp in enumerate(cl)}
    print("charlist: %d 项" % len(cl))
    print("已知映射: %d 条" % sum(1 for v in mp.values() if v))
    if missing:
        print("★ 缺映射: %s（这些字将保持不变）" % "".join(missing))
    print()

    # 读取 static_CH
    v2 = VppLib(src)
    ent = v2.find("static_CH", "le_strings")
    body = bytes(v2.read(ent))
    raw = bytearray(open(src, "rb").read())
    pos = raw.find(body)
    if pos < 0:
        raise SystemExit("无法定位 static_CH")
    d = bytearray(body)
    b, c, oa, offs = file_offsets(bytes(d))

    changed = 0
    for off in [o for o in dict.fromkeys(offs) if 0 < o <= len(d) - 10]:
        id1, id2 = struct.unpack_from("<HH", d, off)
        h = (id1 << 16) | id2
        if h not in TARGETS:
            continue
        u, _ = read_units(bytes(d), off + 8)
        vals = [x for x, _ in u]
        # 解码成字符
        chars = []
        for s in vals:
            cp = cl[s - 0x20] if 0 <= s - 0x20 < len(cl) else None
            chars.append(chr(cp) if cp else "?")
        old_txt = "".join(chars)
        # 替换
        new_chars = [mp.get(ch, ch) if mp.get(ch) else ch for ch in chars]
        new_txt = "".join(c if c else "?" for c in new_chars)
        print("  0x%08X" % h)
        print("    原: %s" % old_txt)
        print("    新: %s" % new_txt)
        # 写回
        for j, ch in enumerate(new_chars):
            if ch is None or ch == "?":
                continue
            cp = ord(ch)
            if cp not in IDX:
                print("    ★ %s 不在 charlist，跳过该位" % ch)
                continue
            s = IDX[cp] + 0x20
            bp = off + 8 + j * 2
            old_s, = struct.unpack_from(">H", d, bp)
            if old_s != s:
                d[bp] = (s >> 8) & 0xFF
                d[bp + 1] = s & 0xFF
        changed += 1

    raw[pos:pos + len(d)] = d
    open(dst, "wb").write(bytes(raw))
    md5 = hashlib.md5(open(dst, "rb").read()).hexdigest()
    print()
    print("已输出 %s" % dst)
    print("  修改 %d 条记录, md5 = %s" % (changed, md5))
    print()
    print("部署:")
    print('  cp "%s" "G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"' % dst)


if __name__ == "__main__":
    main()
