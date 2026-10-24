"""清理游戏目录里的备份/临时文件。

用户选择：保留 3 个 .official_bak（patch/common/textures 官方原版），
其余中间版本备份与 Mods 下的临时文件全部删除。
"""
import os, glob, hashlib

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# ★ 保留：官方原版备份（彻底重置时要用）
KEEP = {
    "patch.vpp_pc.official_bak",
    "common.vpp_pc.official_bak",
    "textures.vpp_pc.official_bak",
}

def is_junk(name):
    n = name.lower()
    return any(k in n for k in (
        '.bak', '_bak', '.orig', '.new', '.old', '~', '.tmp',
        '.before_', '.utf8', 'probe', 'exp_',
    ))

targets = []

# 根目录
for f in glob.glob(os.path.join(GAME, "*")):
    if not os.path.isfile(f):
        continue
    n = os.path.basename(f)
    if n in KEEP:
        continue
    if is_junk(n):
        targets.append(f)

# Mods 递归
for f in glob.glob(os.path.join(GAME, "Mods", "**", "*"), recursive=True):
    if not os.path.isfile(f):
        continue
    n = os.path.basename(f)
    if n in KEEP:
        continue
    if is_junk(n):
        targets.append(f)

total = sum(os.path.getsize(t) for t in targets)
print("=== 待删除 %d 个文件，共 %.2f GB ===" % (len(targets), total / (1024**3)))
for t in sorted(targets):
    print("  %10d  %s" % (os.path.getsize(t), os.path.relpath(t, GAME)))

print("\n=== 保留 ===")
for k in sorted(KEEP):
    p = os.path.join(GAME, k)
    if os.path.exists(p):
        print("  %10d  %s  %s" % (os.path.getsize(p), k,
                                   hashlib.md5(open(p, 'rb').read()).hexdigest()[:16]))

print("\n=== 执行删除 ===")
ok = 0
for t in targets:
    try:
        os.remove(t); ok += 1
    except Exception as e:
        print("  ★失败:", os.path.relpath(t, GAME), e)
print("已删除 %d / %d 个" % (ok, len(targets)))

# 删除后复核
print("\n=== 删除后复核 ===")
left = []
for f in glob.glob(os.path.join(GAME, "*")):
    if os.path.isfile(f) and is_junk(os.path.basename(f)):
        left.append(os.path.basename(f))
for f in glob.glob(os.path.join(GAME, "Mods", "**", "*"), recursive=True):
    if os.path.isfile(f) and is_junk(os.path.basename(f)):
        left.append(os.path.relpath(f, GAME))
print("残留可疑文件:", left if left else "无")

print("\n=== 当前游戏目录关键文件 ===")
for f in ["patch.vpp_pc", "common.vpp_pc", "textures.vpp_pc", "SR2_pc.exe", "DFEngine.dll"]:
    p = os.path.join(GAME, f)
    if os.path.exists(p):
        print("  %-18s %12d  %s" % (f, os.path.getsize(p),
                                     hashlib.md5(open(p, 'rb').read()).hexdigest()))