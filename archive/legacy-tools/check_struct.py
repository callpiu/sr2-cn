"""结构完整性检查：le_strings 表的 桶表/偏移表/记录终止符。

若某新增表的偏移表指向非法位置、或记录缺 0x0000 终止符（read_units 越界），
游戏哈希查找会得到野指针 → strlen16(0x1) 崩溃。
以 dlc_ch（已知良好）为参照。
"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units, MAGIC

LOCAL = r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc"
BASE  = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def check(path, label):
    d = open(path,'rb').read()
    if struct.unpack_from('<I',d,0)[0] != MAGIC:
        print("[跳过] %s 非 le_strings" % label); return
    buckets, cnt, off_at, offs = file_offsets(d)
    n=len(d)
    # 实际能成功解析的记录 + 越界记录
    good=badterm=0
    bad_offs=[]
    for off in dict.fromkeys(offs):
        # off 必须是合法记录起点：位于 [off_at+cnt*4, n-10]
        if not (off_at + cnt*4 <= off <= n-10):
            bad_offs.append(off); continue
        units,end = read_units(d, off+8)
        if units is None:
            badterm+=1; bad_offs.append(off)
        else:
            good+=1
    print("== %s ==" % label)
    print("   pairCount=%d  实际解析 good=%d 越界/缺终止=%d" % (cnt, good, badterm))
    if bad_offs:
        print("   非法/越界偏移样例: %s" % [hex(x) for x in bad_offs[:8]])
    # 偏移是否覆盖全部记录区？检查最后一条记录是否越出 data
    if offs:
        last=max(offs)
        u,end=read_units(d,last+8)
        if end is not None and end>n:
            print("   ★ 最后记录越出数据区 end=0x%X > n=0x%X" % (end,n))
    print()

# 已知良好参照
check(os.path.join(BASE,"DLC/Text/dlc_ch.le_strings"), "DLC/Text/dlc_ch (参照)")
check(os.path.join(BASE,"Mods/JUICED - Strings/patch_ch.le_strings"), "Mods/patch_ch (参照)")

# patch 内所有 le_strings
v=Vpp(LOCAL)
for e in v.entries():
    if e['ext']=='le_strings':
        d=v.read(e)
        # 临时写盘以便复用 check
        tmp=r"F:\sr2-cn\_fix_candidates\_tmp_%s.%s"%(e['name'],e['ext'])
        open(tmp,'wb').write(d)
        check(tmp, "patch::%s"%e['name'])
        os.remove(tmp)
