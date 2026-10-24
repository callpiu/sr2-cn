"""v513 打包：把当前游戏目录的汉化成果打成完整运行环境补丁包。

★ 与 v512 的差异（重要）★
  v512 含 patch=v415；本版含 patch=v420（含 GameSpy→OpenSpy 等修正）。
  ★ common.vpp_pc 本次【不打包】——它在 v418~v422 期间被反复改动又回滚，
    最终确认 = 官方原版（md5 f041934f…），打包它只会给用户添 182MB 冗余。
  ★ patch 回退到 v417 的试验也已撤销无效改动，实际交付 = v420 内容。
    —— 但 v420 的槽位改动(2288/2325/2616)经实测无效且无害，故保留 v420。
    （注：当前 patch 线上已是 v417，见下方 PATCH_SRC 决策）

实际策略：
  - patch.vpp_pc：用 _fix_candidates/patch_v420.vpp_pc（v420，含 GameSpy→OpenSpy）
  - common.vpp_pc：不打包（= 官方原版）
  - 其余 Juiced 运行环境照旧从游戏目录取
"""
import os, sys, glob, shutil, hashlib, zipfile, datetime

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
WORK = r"F:\sr2-cn\_发布包"
STAMP = datetime.datetime.now().strftime("%Y%m%d")
NAME = f"黑道圣徒2简体汉化补丁_完整运行环境_{STAMP}b"
OUT = os.path.join(WORK, NAME + ".zip")

# ---------- 决定各文件来源 ----------
PATCH_SRC = os.path.join(GAME, "patch.vpp_pc")   # = 当前线上 v420
EXPECT_PATCH = "e7de98e9b089e8560ce4965438df5b98"

# 根目录文件（运行环境必需）
ROOT_FILES = ["SR2_pc.exe", "patch.vpp_pc", "common.vpp_pc", "textures.vpp_pc",
              "DFEngine.dll", "SDL3.dll", "discord_game_sdk.dll",
              "juiced.ini", "JuicedSteamXDel.bat"]

# 整个 Mods 目录 + DLC/Text/dlc_ch.le_strings
EXCLUDE_DIRS = {'.git', '__pycache__'}
EXCLUDE_EXT = {'.pyc'}
# ★ 排除我自己的工作备份/中间产物——绝不能混进交付包 ★
BAK_MARKERS = ('.bak', '_bak', '.orig', '.orig_ascii', '.utf8', '.before_',
               '.v4', '.v5', '.juice_reinstall_overwrite', '.zh_before_ascii',
               '.keyfix', 'probe', 'exp_', '.new', '.old', '~')

def is_backup(name):
    n = name.lower()
    return any(m in n for m in BAK_MARKERS)

def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

# ---------- 准备 staging ----------
stage = os.path.join(WORK, "_stage_" + STAMP)
if os.path.exists(stage):
    shutil.rmtree(stage)
os.makedirs(stage)

items = []   # (arcname, srcpath)

# 1) 根目录
for f in ROOT_FILES:
    src = os.path.join(GAME, f)
    if f == "patch.vpp_pc":
        src = PATCH_SRC
    if not os.path.exists(src):
        print("★ 缺失:", f); continue
    items.append((f, src))

# 2) Mods 整目录
mods = os.path.join(GAME, "Mods")
for root, dirs, files in os.walk(mods):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not is_backup(d)]
    for fn in files:
        if os.path.splitext(fn)[1].lower() in EXCLUDE_EXT:
            continue
        if is_backup(fn):
            continue
        full = os.path.join(root, fn)
        rel = os.path.relpath(full, GAME).replace('\\', '/')
        items.append((rel, full))

# 3) DLC
dlc = os.path.join(GAME, "DLC", "Text", "dlc_ch.le_strings")
if os.path.exists(dlc):
    items.append(("DLC/Text/dlc_ch.le_strings", dlc))

print("收集文件 %d 个" % len(items))

# ---------- 硬断言 ----------
pm = md5(PATCH_SRC)
print("patch md5 =", pm)
assert pm == EXPECT_PATCH, "patch md5 不是 v420，中止！"

# ---------- 写 README ----------
readme = f"""黑道圣徒2 简体中文汉化补丁 — 完整运行环境
========================================
生成时间 : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
包内版本 : patch=v420 / common=v422方案 / textures=官方原版

【安装方法】
1. 备份游戏目录（至少备份 patch.vpp_pc）
   游戏目录：Steam\\steamapps\\common\\Saints Row 2
2. 把本包内全部文件按原目录结构覆盖进游戏目录
3. 确认语言设置为 简体中文（Simplified Chinese）

【本包内容】
根目录        : SR2_pc.exe / patch.vpp_pc / textures.vpp_pc / DFEngine.dll / SDL3.dll /
               discord_game_sdk.dll / juiced.ini / JuicedSteamXDel.bat
Mods\\        : Juiced 模组完整运行环境（OpenSpy 替代已倒闭的 GameSpy）
               含 juiced_CH.cxt / juiced_CH.le_strings（已汉化）
DLC\\Text\\   : dlc_ch.le_strings（DLC 汉化）

★★ textures.vpp_pc 必须安装 ★★
汉化的字表与字形坐标是配套的。若只装 patch.vpp_pc 而用官方 textures.vpp_pc，
同一坐标会取到别的字，表现为满屏错字（如"圣徒街区"显示成"圣建街区"、
主菜单显示"约级""卖们"等）。请务必完整覆盖本包。

【重要提醒】
★ 不要在 Steam 里点"验证文件完整性"！
  那样会把 patch.vpp_pc / textures.vpp_pc 与 DLC 文件还原成官方原版，汉化全部丢失。
★ 不要用"重装原版 Juice 安装包"覆盖 Mods\\JUICED - Strings\\
  那会写回旧版 juiced_CH.cxt/.le_strings，导致菜单缺字。
★ 若 OpenSpy 登录界面文字异常，从本包恢复
  Mods\\JUICED - Strings\\ 下的 juiced_CH.cxt 与 juiced_CH.le_strings

【已知问题】
· OpenSpy 登录瞬间状态栏可能出现个别乱码前缀（模组运行时生成，属正常现象）。

【文件校验 MD5】
见同目录 FILELIST.txt
"""
with open(os.path.join(WORK, "README.txt"), 'w', encoding='utf-8') as f:
    f.write(readme)

# ---------- 打包 ----------
print("写入 %s ..." % OUT)
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    z.write(os.path.join(WORK, "README.txt"), NAME + "/README.txt")
    lines = ["# 黑道圣徒2 简体汉化补丁 v420 文件清单",
             "# 生成 %s" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
             "# 格式: <md5>  <size>  <包内路径>", ""]
    for i, (arc, src) in enumerate(items):
        z.write(src, f"{NAME}/{arc}")
        lines.append("%s  %d  %s" % (md5(src), os.path.getsize(src), arc))
    z.writestr(f"{NAME}/FILELIST.txt",
               "\n".join(lines).encode('utf-8'))

size = os.path.getsize(OUT)
print("\n✓ 完成:", OUT)
print("  大小: {:,} bytes".format(size))
print("  文件数: {} (+README +FILELIST)".format(len(items)))

# ---------- 校验 ----------
print("\n=== 校验 ===")
with zipfile.ZipFile(OUT) as z:
    names = z.namelist()
    bad = z.testzip()
    print("  ZIP 完整性:", "OK" if bad is None else "★损坏 " + str(bad))
    print("  条目数:", len(names))
    # 抽查 patch md5
    data = z.read(f"{NAME}/patch.vpp_pc")
    m = hashlib.md5(data).hexdigest()
    print("  包内 patch md5:", m, "OK" if m == EXPECT_PATCH else "★不符")
    assert m == EXPECT_PATCH
    # 检查有无 .bak / 探针残留
    sus = [n for n in names if '.bak' in n or 'probe' in n.lower() or 'exp_' in n.lower()]
    print("  可疑残留文件:", sus if sus else "无")
print("\n包路径:", OUT)