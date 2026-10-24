import os, shutil, hashlib, re

SRC = 'D:/下载/Compressed/SR2_JUICED_2/'
OUT = 'F:/sr2-cn/_发布包/黑道圣徒2_Juiced9.3.1_简体汉化整合_20261018/'

if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT, exist_ok=True)

def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

# 1) 复制 Juice 9.3.1 全部内容
n = 0
for root, dirs, files in os.walk(SRC):
    rel = os.path.relpath(root, SRC)
    tgt = OUT if rel == '.' else os.path.join(OUT, rel)
    os.makedirs(tgt, exist_ok=True)
    for fn in files:
        if fn.lower().endswith('.pdb'):
            continue          # 调试符号，跳过（可选，省 20MB）
        shutil.copy2(os.path.join(root, fn), os.path.join(tgt, fn))
        n += 1
print('Juice 文件已复制:', n)

# 2) 覆盖汉化文件（★顺序关键：汉化必须在 Juice 之后覆盖）
G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
BAK = G + '_汉化备份_装Juice前/'

# 2.1 dialog_box.lua —— 我的 SUI_LAN_COOP_SP 修复
shutil.copy2(BAK + 'dialog_box.lua', OUT + 'Mods/dialog_box.lua')
print('已恢复 Mods/dialog_box.lua (SUI 修复)')

# 2.2 DLC 汉化
os.makedirs(OUT + 'DLC/Text', exist_ok=True)
shutil.copy2(BAK + 'dlc_ch.le_strings', OUT + 'DLC/Text/dlc_ch.le_strings')
print('已恢复 DLC/Text/dlc_ch.le_strings')

# 2.3 patch.vpp_pc —— 汉化主体（Juice 包里本来就没有，但保险）
shutil.copy2(BAK + 'patch.vpp_pc', OUT + 'patch.vpp_pc')
print('已放入 patch.vpp_pc (v543)')

# 2.4 juiced_CH.le_strings —— 用新版的（44 字节差异是官方的修正）
#     当前游戏目录那份是我早期修的，官方新版更权威 => 保留新版不动
print('juiced_CH.le_strings: 保留 Juice 官方新版')
print('juiced_CH.cxt:       保留 Juice 官方新版（官方自带完整汉化，50 项）')

# 3) 生成说明
README = """黑道圣徒2  Juice 9.3.1 + 简体中文汉化 整合版 (2026-10-18)
==============================================================
本包 = Juice 9.3.1 官方包（含官方自带中文菜单）
     + SR2 简体汉化补丁 v543（21 项修复）
     + Juice dialog_box.lua 的 SUI 标签修复

安装：把本包全部内容拖到
  G:\\SteamLibrary\\steamapps\\common\\Saints Row 2\\
  （直接覆盖，不要先装旧的 Juice）

★★★ 装完后务必注意 ★★★
  1) 【禁止】点 Steam「验证文件完整性 / 修复文件」
     → 会把 patch.vpp_pc 还原成官方英文原版，汉化全部丢失！
  2) 【禁止】之后不要再单独安装旧版 Juice 安装包
     → 会覆盖 Mods/ 下的文件，汉化修复失效。
     → 需要重装 Juice 时，请重新用本整合包。
  3) 不要删除 Mods/dialog_box.lua —— 这是等待玩家界面漏英文标签的修复。

★ 汉化内容（共 21 项，详见包内 README）
  地名 / 商店 / 街区 / 餐厅名、地图区域「市郊区」、指定辩护律师、
  兄弟会 / 三王 / 三街圣徒、霰弹枪 / 弹药、Father→「父亲」、
  charlist 坏字位总修复、v532 哈希桶镜像重建（!!unrecognized）、
  拆车厂崩溃修复、等待玩家界面 SUI 标签修复。

★ 关于 Juice 菜单中文
  本包内 Mods/JUICED - Strings/juiced_CH.cxt 采用 Juice 官方自带的
  完整汉化版（51 个选项全部中文），优于此前手工补的版本。
"""
with open(OUT + '_先读我.txt', 'w', encoding='utf-8') as f:
    f.write(README)

# 4) 校验
print()
print('=== 校验关键文件 ===')
must = {
    'patch.vpp_pc': 'c91a4ff4e2fab9a3522d4724922791d7',
    'Mods/dialog_box.lua': 'f89645e132f3e65bf9284e68ce7de2cc',
    'DFEngine.dll': None,
    'Mods/JUICED - Strings/juiced_CH.cxt': None,
    'DLC/Text/dlc_ch.le_strings': None,
}
for rel, exp in must.items():
    p = OUT + rel
    assert os.path.exists(p), '缺失 ' + rel
    h = md5(p)
    ok = 'OK' if (exp is None or h == exp) else '★不符 期望 ' + exp
    print('   %-42s %s  %s' % (rel, h, ok))

# 确认没有 .bak/.orig 混进去会干扰
bad = []
for root, dirs, files in os.walk(OUT):
    for fn in files:
        if fn.endswith(('.bak', '.orig', '.orig_ascii')):
            bad.append(os.path.join(root, fn))
print()
print('注意：整合包内含 Juice 自带的 .bak/.orig 文件（如有）：')
for b in bad[:10]:
    print('   ', os.path.relpath(b, OUT))
print('   共', len(bad), '个（Juice 原包自带，不影响汉化）')