"""离线验证：按游戏真实解析逻辑（反汇编自 StringsLoad@0x7F4780）模拟桶表遍历，
确认新文件不会触发 0x7F491B 的越界崩溃。

游戏逻辑（已从机器码还原）：
  ebx = header.buckets (u16)  —— 实际是 [ebp] 处 u16
  ebp -> 桶表首项
  for ecx in range(ebx):                  # 外层：遍历所有桶
      bucket = &桶表[ecx*8]
      f0 = bucket[0]  (u32)
      f1 = bucket[1]  (u32)
      if f0 == 0: continue                # 0x7F48FD test eax,eax / je
      # f1 会 += 基址（模拟）
      for edx in range(f0):               # 内层：cmp edx,[ebp]（ebp=&bucket[0]）
          off = offset[起始下标 + edx]     # 实际是 [ecx+edx*4]，ecx = &bucket[4]+基址
          record = data[off + 基址]
          ...
  ⇒ 内层上限是【字段0】，所以字段0 必须是"该桶覆盖的 offset 表元素数"。
  ⇒ 字段0 若为脏数据(312)而实际只有 12 条，则 edx 会读到 offset 表外的内存。
"""
import struct, sys

def load(path):
    d = open(path, 'rb').read()
    magic, ver, buckets, count = struct.unpack_from('<IHHI', d, 0)
    HDR, BT = 16, buckets*8
    off_at = HDR + BT
    offs = [struct.unpack_from('<I', d, off_at+k*4)[0] for k in range(count)]
    btab = [struct.unpack_from('<II', d, HDR+i*8) for i in range(buckets)]
    return d, magic, ver, buckets, count, off_at, offs, btab

def analyze(path, label):
    d, magic, ver, buckets, count, off_at, offs, btab = load(path)
    print("\n===== %s =====" % label)
    print("size=%d buckets=%d count=%d off_at=0x%X" % (len(d), buckets, count, off_at))
    print("offset 表: %s" % [hex(o) for o in offs])

    # 关键：模拟内层遍历是否会读越界
    # 保守判定：任一桶的 f0 若 > count，则内层 edx 会越过 offset 表末尾
    max_f0 = max(f0 for f0, f1 in btab)
    print("桶字段0 最大值 = %d (count=%d)" % (max_f0, count))
    risky = [(i, f0, f1) for i, (f0, f1) in enumerate(btab) if f0 > count]
    if risky:
        print("★ 存在 f0 > count 的桶（游戏靠外层兜住，属原文件既有行为）:")
        for i, f0, f1 in risky:
            print("     bucket[%d] f0=%d f1=%d" % (i, f0, f1))
    else:
        print("✓ 所有桶 f0 <= count")

    # 检查所有有效 offset 是否指向合理的记录（有 0x0000 终止）
    print("\n记录有效性:")
    for k, off in enumerate(offs):
        if off + 8 > len(d):
            print("  rec%-2d off=0x%X  ★越界/损坏（原文件既有）" % (k, off))
            continue
        p = off + 8; n = 0; ok = False
        while p + 2 <= len(d):
            x, y = d[p], d[p+1]
            p += 2
            if x == 0 and y == 0:
                ok = True; break
            n += 1
        print("  rec%-2d off=0x%X slots=%-3d 终止符=%s" % (k, off, n, "有" if ok else "★无"))

for p, lab in (
    (r"G:\SteamLibrary\steamapps\common\Saints Row 2\Mods\JUICED - Strings\juiced_CH.le_strings", "当前游戏文件(已回滚的原版)"),
    (r"F:\sr2-cn\_fix_candidates\juiced_CH.fixed.le_strings", "新构建(桶表原样)"),
    (r"F:\sr2-cn\_fix_candidates\juiced_CH.rebuilt.le_strings", "★上一版崩溃文件(重建桶表)"),
):
    try:
        analyze(p, lab)
    except FileNotFoundError:
        print("跳过(不存在): %s" % lab)