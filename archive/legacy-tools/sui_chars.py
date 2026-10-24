import sys, os
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
CPS = set(int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit())
print("第三方 charlist %d 项" % len(CPS))
print()
CAND = {
 "SUI_OPTIONS_TITLE": "音效选项",
 "SUI_OPTIONS_WEAPON_SWITCH_SOUND": "武器切换音效",
 "SUI_OPTIONS_FAST_WEAPON_SWITCH": "快速切换武器",
 "SUI_OPTIONS_HUD_MESSAGES": "HUD 讯息",
 "SUI_OPTIONS_HUD_LAYOUT": "HUD 布局",
 "SUI_OPTIONS_HUD_AUTOHIDE": "HUD 自动隐藏",
 "SUI_OPTIONS_HUD_ZOMBIE": "僵尸模式 HUD",
 "SUI_OPTIONS_SCREEN_EDGE_SHADOW": "屏幕边缘阴影",
 "SUI_MINIMUM": "最小",
 "SUI_DEATH_1": "你死了",
 "SUI_MULTIPLAYER_NAKED_WARNING": "多人游戏中出现裸露内容警告",
}
for k, val in CAND.items():
    miss = [c for c in val if ord(c)>0x100 and ord(c) not in CPS]
    print("  %-34s %-22s %s" % (k, val, "OK" if not miss else "缺: "+"".join(miss)))
print()
LOADS = ["正在载入游戏...","正在读取存档...","正在准备城市...","正在载入资源...",
         "正在初始化...","正在载入地图...","正在准备车辆...","正在载入音效...","请稍候..."]
print("=== 加载提示候选 ===")
for s in LOADS:
    miss = [c for c in s if ord(c)>0x100 and ord(c) not in CPS]
    print("  %-18s %s" % (s, "OK" if not miss else "缺: "+"".join(miss)))
