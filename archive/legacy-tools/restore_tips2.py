import os
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
M = os.path.join(G,"Mods")
p = os.path.join(M,"city_load.lua")
TIPS = [
 '善用掩体可以减少受伤','按 R 可以捡起地上的物品','完成任务可以提升帮派声望',
 '在地图上标记目标可以指引方向','驾驶时按 Shift 可以加速','购买房产可以获得额外收入',
 '升级武器可以提升威力','召唤小弟可以协助战斗','完成任务时注意保存进度',
 '击倒敌人后可以抢夺他们的武器','车辆可以开到车库进行改装','按 Tab 可以查看地图',
 '遇到警察时注意通缉等级','使用手雷可以对付聚集的敌人','不同的服装可以获得不同效果',
 '在商店可以购买武器和补给','帮派地盘可以通过完成任务扩张','多利用环境可以更轻松取胜',
 '骑摩托车时注意保持平衡','被通缉时可以躲进建筑物','完成小游戏可以获得额外奖励',
 '和朋友一起玩可以完成更多挑战','注意屏幕上的提示信息','保存游戏可以避免进度丢失',
 '升级角色能力可以让战斗更轻松','在车库里可以保存你喜欢的车辆','多尝试不同的武器找到适合自己的',
 '完成任务后记得领取奖励','注意敌人的攻击前摇及时闪避','可以随时调整难度设置',
 '利用高处可以获得视野优势','金钱可以用来购买装备和房产','把车停在安全的地方再下车',
 '注意任务提示中的时间限制','不同的帮派有不同的战斗风格','在城市中探索可以发现隐藏内容',
 '完成任务可以获得新的武器解锁','保持移动可以避免被敌人包围','使用望远镜可以标记远处的目标',
 '受伤后可以寻找医疗包恢复','多利用车辆快速移动','注意天气对驾驶的影响',
 '把重要的车辆存进车库','完成任务链可以解锁新的剧情','随时可以打开选项调整设置',
]
b = open(p,"rb").read()
txt = b.decode("gbk")
n = 0
for i, tip in enumerate(TIPS, 1):
    pat = '"%s"' % tip
    if pat in txt:
        n += txt.count(pat)
        txt = txt.replace(pat, '"SUI_TIPS_%d"' % i)
out = txt.encode("ascii")
open(p,"wb").write(out)
print("还原 %d 处, %d -> %d 字节" % (n, len(b), len(out)))
print()
print("=== 全部文件复验 ===")
ok = True
for fn in ("pause_menu.lua","main_menu.lua","sui_main_menu.lua","hud.lua","city_load.lua"):
    bb = open(os.path.join(M,fn),"rb").read()
    na = sum(1 for x in bb if x > 0x7F)
    st = "OK" if na == 0 else "★ 仍有 %d" % na
    if na: ok = False
    print("  %-24s %8d 字节  非ASCII %-4d %s" % (fn, len(bb), na, st))
print()
print("全部干净" if ok else "★ 还有残留")
