import os, re
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
M = os.path.join(G,"Mods")
p = os.path.join(M,"city_load.lua")
b = open(p,"rb").read()
try:
    txt = b.decode("gbk")
except UnicodeDecodeError as e:
    print("GBK 解码失败: %s" % e); raise SystemExit(1)
# 把中文字面量还原成原始 key
n = 0
def repl(m):
    global n
    n += 1
    return '"SUI_TIPS_%s"' % m.group(1)
# 匹配 "任意中文..."（GBK 解出来是中文）
txt2 = re.sub(r'"([\u4e00-\u9fff][^"]*)"', repl, txt)
out = txt2.encode("ascii", "strict")
open(p,"wb").write(out)
print("还原 %d 处中文字面量 -> 原始 SUI_TIPS_N key" % n)
print("  文件 %d -> %d 字节" % (len(b), len(out)))
# 复验
b2 = open(p,"rb").read()
try:
    b2.decode("ascii"); print("  复验: 纯 ASCII OK")
except UnicodeDecodeError: print("  复验: 仍有非 ASCII")
print()
print("=== 全部 5 个文件复验 ===")
for fn in ("pause_menu.lua","main_menu.lua","sui_main_menu.lua","hud.lua","city_load.lua"):
    bb = open(os.path.join(M,fn),"rb").read()
    na = sum(1 for x in bb if x > 0x7F)
    print("  %-24s %8d 字节  非ASCII %d %s" % (fn, len(bb), na, "OK" if na==0 else "★"))
