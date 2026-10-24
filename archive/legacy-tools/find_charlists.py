# -*- coding: utf-8 -*-
"""穷举所有 VPP/DLC 中的 charlist 类文件，弄清 2838 与 2795 两套字表的关系。"""
import os, sys, struct, glob, re
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
import sr2lib as S

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

class VppLite:
    def __init__(self, path):
        self.path = path
        with open(path, 'rb') as f:
            head = f.read(5 + 0x14F + 20)
            o = 5 + 0x14F
            (self.num, self.cs, self.lo, self.lf, self.le) = struct.unpack_from('<iiiii', head, o)
            self.names_at = ((0x800 + self.lo) & 0xFFFFF800) + 0x800
            self.ext_at = ((self.names_at + self.lf) & 0xFFFFF800) + 0x800
            self.data_start = ((self.ext_at + self.le) & 0xFFFFF800) + 0x800
            f.seek(0x800); et = f.read(self.num * 28)
            f.seek(self.names_at); names = f.read(self.lf)
            f.seek(self.ext_at); exts = f.read(self.le)
        self.ents = []
        for i in range(self.num):
            a, b, c, d, ln, m1, z = struct.unpack_from('<IIiiiii', et, i * 28)
            nm = names[a:names.find(b'\x00', a)].decode('ascii','replace') if a < len(names) else ''
            ex = exts[b:exts.find(b'\x00', b)].decode('ascii','replace') if b else ''
            self.ents.append(dict(idx=i, name=nm, ext=ex, body=d, size=ln))
    def read(self, ent):
        with open(self.path, 'rb') as f:
            f.seek(self.data_start + ent['body']); return f.read(ent['size'])

roots = [G] + [os.path.join(G, d) for d in os.listdir(G) if os.path.isdir(os.path.join(G, d))]
vpps = []
for r in roots:
    for f in glob.glob(os.path.join(r, "*.vpp_pc")):
        vpps.append(f)
vpps += glob.glob(os.path.join(G, "**", "*.vpp_pc"), recursive=True)
vpps = sorted(set(vpps))
print("找到 %d 个 vpp_pc" % len(vpps))

hits = []
for p in vpps:
    try:
        vl = VppLite(p)
    except Exception as ex:
        print("  !! %s 解析失败 %s" % (p, ex)); continue
    for e in vl.ents:
        n = (e['name'] or '').lower()
        if 'char' in n or 'font' in n or n.startswith('fnt'):
            hits.append((p, e))
print("\n=== charlist/font 类条目 %d 个 ===" % len(hits))
for p, e in hits:
    print("  %-58s %-14s ext=%-10s size=%d" % (os.path.basename(os.path.dirname(p)) + "/" + os.path.basename(p),
                                               e['name'], e['ext'], e['size']))

print("\n=== 逐个解析 charlist* 的条目数与顺序特征 ===")
for p, e in hits:
    if 'char' not in (e['name'] or '').lower(): continue
    try:
        d = vl = None
        vl = VppLite(p); d = vl.read(e)
    except Exception as ex:
        print("  %s 读取失败 %s" % (e['name'], ex)); continue
    txt = d.decode('latin1', 'replace')
    nums = [int(x) for x in re.findall(rb'\d+', d)]
    if not nums:
        print("  %-16s (%s) 非十进制文本, 前32字节=%s" % (e['name'], os.path.basename(p), d[:32].hex()))
        continue
    asc = sum(1 for i in range(len(nums)-1) if nums[i] < nums[i+1]) / max(1, len(nums)-1)
    print("  %-16s (%s) %d 项 唯一%d 升序%.3f 首=%d 末=%d"
          % (e['name'], os.path.basename(p), len(nums), len(set(nums)), asc, nums[0], nums[-1]))
