# -*- coding: utf-8 -*-
# 找「好触发」的验证句：字幕路径 + 高频简体专属字 + 日常任务必见
# 排除菜单/UI 项（走默认字体，不会乱码），只留对白与提示
import sys, struct, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp

VANILLA = r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017"
CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"


def parse_charlist(raw):
    B = []
    for L in raw.split(b"\r\n"):
        s = L.strip()
        if not s or s.startswith(b"//") or s.startswith(b"count="):
            continue
        for tok in s.split():
            if tok.isdigit():
                B.append(chr(int(tok)))
    return B


vv, cn = Vpp(VANILLA), Vpp(CN)
T = parse_charlist(vv.read(vv.find("charlist_CH", "txt")))
f = Font(CN)
B = [chr(c) for c in f.charlist]
BT = set(ord(c) for c in T)
missing = set(c for c in B if ord(c) not in BT and 0x4E00 <= ord(c) <= 0x9FFF)

# 高频缺字权重（来自全字幕频次统计）
FREQ = {"这": 1501, "们": 1441, "车": 1082, "个": 964, "么": 903, "会": 798, "来": 792,
        "点": 671, "说": 619, "开": 612, "尔": 609, "时": 535, "帮": 529, "儿": 490,
        "吗": 488, "现": 479, "过": 473, "没": 472, "还": 468, "杀": 463, "着": 414,
        "为": 396, "对": 362, "击": 350, "干": 327, "机": 325, "让": 308, "圣": 302,
        "数": 300, "别": 299}

# 明显是菜单/UI 的特征（这些走默认字体，不会乱码）
UI_PAT = re.compile(r"^[\s]*(%|\[|\{|\$|\+|-|\d|⟨|选项|菜单|标签|统计|键|灵敏度|音量|分辨率|画质|关闭|开启|返回|确定|取消|应用|保存|载入|删除|排序|筛选|搜索|地图|电台|歌曲|播放|暂停|音量|亮度|对比度|控制|鼠标|键盘|手柄|网络|服务器|玩家|房间|密码|名称|创建|加入|邀请|好友|排行|成就|奖杯|解锁|装备|武器|弹药|服装|商店|购买|出售|价格|现金|声望|等级|经验|进度|存档|读取|退出|暂停|继续|重新开始|新游戏|读取|教程|帮助|设置|显示|音频|视频|语言|字幕|画质|分辨率|刷新率|垂直同步|阴影|抗锯齿|纹理|特效|体积光|景深|动态模糊|屏幕|窗口|全屏|无边框|自适应|画质预设|最低|低|中|高|最高|超|自定义|默认|重置|恢复)")


def load(name):
    d = cn.read(cn.find(name, "le_strings"))
    buckets, = struct.unpack_from("<H", d, 6)
    count, = struct.unpack_from("<I", d, 8)
    ptrs = struct.unpack_from("<%dI" % count, d, 12 + buckets * 8)
    return d, count, ptrs


def rec(d, p):
    id1, id2 = struct.unpack_from("<HH", d, p)
    q = p + 4
    out = []
    while True:
        s, = struct.unpack_from(">H", d, q)
        q += 2
        if s == 0:
            break
        k = s - 32
        out.append(B[k] if 0 <= k < len(B) else "{%d}" % s)
    return id1, id2, "".join(out)


cands = []
for name in ("voice_script_CH", "static_CH"):
    d, count, ptrs = load(name)
    for i in range(count):
        p = ptrs[i]
        if p + 6 > len(d):
            continue
        try:
            a, b_, t = rec(d, p)
        except Exception:
            continue
        # 只要纯中文对白：汉字为主、长度适中、无格式标记/占位符
        han = [c for c in t if 0x4E00 <= ord(c) <= 0x9FFF]
        if len(han) < 5 or len(han) < len(t) * 0.6:
            continue
        if any(x in t for x in ("%", "{", "[", "$", "img", "format", "color")):
            continue
        if UI_PAT.match(t):
            continue
        bad = [c for c in han if c in missing]
        if len(bad) < 3:
            continue
        score = sum(FREQ.get(c, 1) for c in bad)
        hi = sorted(set(bad), key=lambda c: -FREQ.get(c, 0))
        cands.append((score, len(bad), len(han), name, a, b_, t, "".join(hi)))

cands.sort(reverse=True)
print("候选句数 =", len(cands))
print("\n=== Top 20 好触发验证句（按高频缺字权重排序）===")
for s, nb, tot, name, a, b_, t, hi in cands[:20]:
    print("\n  [%04X.%04X] %s  缺字%d/%d  权重%d" % (a, b_, name, nb, tot, s))
    print("     「%s」" % t[:60])
    print("     缺字: %s" % hi)

# 单独看「劫辆车赶紧离开」系列（任务撤离提示，最好触发）
print("\n\n=== 「赶紧离开」系列（任务收尾必现）===")
for s, nb, tot, name, a, b_, t, hi in cands:
    if "赶紧离开" in t or "离开这儿" in t:
        print("  [%04X.%04X] 「%s」  缺字%d/%d" % (a, b_, t[:50], nb, tot))
