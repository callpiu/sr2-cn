import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
vp = Vpp(os.path.join(G,"patch.vpp_pc"))
t = vp.read(vp.find("charlist_CH","txt")).decode('utf-8','replace')
nums=[int(s) for s in t.replace('\r','').split('\n') if s.strip().isdigit()]
print("当前 charlist 条目:", len(nums))
vc = Vpp(os.path.join(G,"common.vpp_pc"))
ec = vc.find("fnt_chinese","vf3_pc"); o = vc.data_start + ec['body']
N = struct.unpack_from('<I', vc.data, o+8)[0]
uo = 0xBC + N*16
U=[struct.unpack_from('<I',vc.data,o+uo+i*4)[0] for i in range(N)]
V=[struct.unpack_from('<I',vc.data,o+uo+N*4+i*4)[0] for i in range(N)]
print("vf3 N =", N, " 需要的字形数 =", len(nums)+32)

TEXT = "你的弟兄们需要你的保护"
print("\n句子:", TEXT)
print("%-4s %-6s %-8s %-8s" % ("字","正确idx","引擎用=idx+32","该格实际字"))
for ch in TEXT:
    i = nums.index(ord(ch))
    g = i + 32
    # 我方 vf3 字形 g 对应该 charlist[g]（因为我方字形号==charlist位置）
    actual = chr(nums[g]) if g < len(nums) else '(越界)'
    print("%-4s %-8d %-12d %-8s  U=%d V=%d" % (ch, i, g, actual, U[g] if g<N else -1, V[g] if g<N else -1))
print("\n★ 引擎实际会显示:", "".join(chr(nums[nums.index(ord(c))+32]) for c in TEXT if nums.index(ord(c))+32 < len(nums)))

# 官方原版 charlist 条目数
try:
    vo = Vpp(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig")
    e = None
    for x in vo.entries():
        if x['name']=='charlist_CH' and x.get('ext')=='txt': e=x; break
    if e:
        t2 = vo.read(e).decode('utf-8','replace')
        n2=[int(s) for s in t2.replace('\r','').split('\n') if s.strip().isdigit()]
        print("\n官方原版 charlist_CH.txt: %d 字节, %d 条 -> +32 = %d (官方 vf3 N=2838)" % (len(vo.read(e)), len(n2), len(n2)+32))
        print("  官方前6:", n2[:6], " 有 count= 行:", 'count=' in t2)
except Exception as ex:
    print("官方 charlist 读取失败:", ex)
