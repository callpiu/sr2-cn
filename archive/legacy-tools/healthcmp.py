# -*- coding: utf-8 -*-
"""对比当前表与干净基线 v532 的健康指标，判断差异是原生的还是重建造成的"""
import sys, struct, re, hashlib
sys.path.insert(0, "F:/sr2-cn")
import sr2lib as S
game = "G:/SteamLibrary/steamapps/common/Saints Row 2/"

def check(path, label):
    vp = S.Vpp(path)
    buf = vp.read(vp.find("charlist_CH", "txt"))
    end = buf.find(b"//ENDOFFILE")
    cl = [int(x) for x in re.findall(rb"\d+", buf[:end if end > 0 else len(buf)])]
    ent = vp.find("static_CH", "le_strings")
    d = bytes(vp.read(ent))
    magic, ver, buckets, count = struct.unpack_from("<IHHI", d, 0)
    offs = [struct.unpack_from("<I", d, 12 + buckets * 8 + k * 4)[0] for k in range(count)]
    bad_term = []; empty = []
    texts = {}
    for i, off in enumerate(offs):
        if off + 4 > len(d):
            bad_term.append((i, "OOR")); continue
        id1, id2 = struct.unpack_from("<HH", d, off)
        h = (id1 << 16) | id2
        p = off + 4; n = 0; ok = False
        while p + 1 < len(d):
            s = struct.unpack_from(">H", d, p)[0]
            if s == 0: ok = True; break
            p += 2; n += 1
            if n > 400: break
        if not ok: bad_term.append((i, hex(h)))
        if n == 0: empty.append((i, hex(h)))
        texts[h] = n
    print(f"\n===== {label} =====")
    print(f"  md5={hashlib.md5(open(path,'rb').read()).hexdigest()[:12]} buckets={buckets} count={count} size={len(d)}")
    print(f"  缺终止符 {len(bad_term)} 条: {bad_term[:10]}")
    print(f"  空记录   {len(empty)} 条: {empty[:10]}")
    del vp
    return dict(texts), buckets, count

cur, b1, c1 = check(game + "patch.vpp_pc", "当前（ASCII探针）")
base, b2, c2 = check(game + "patch.vpp_pc.v532_before_exp.bak", "干净基线 v532")

diff = [h for h in base if h not in cur or cur.get(h) != base[h]]
print("\n===== 与 v532 的差异（按记录长度统计） =====")
print(f"  记录数: {len(cur)} vs {len(base)}")
print(f"  长度不同的记录: {len(diff)} 条")
for h in diff[:20]:
    print(f"    {h:#010x}  v532={base.get(h)} 槽位   当前={cur.get(h)} 槽位")
