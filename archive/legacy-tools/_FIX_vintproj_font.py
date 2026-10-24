# -*- coding: utf-8 -*-
"""第十五轮修复：把 sr2.vint_proj 的全部 UI 字体别名指向 fnt_chinese。

根因：
  * 汉化补丁只替换了 fnt_chinese（vf3 N=2795 + 图集 2048x2048）。
  * sr2.vint_proj 未被修改，UI 字体 alias 仍指向
      thin / thin_overlay  -> fnt_body_n / fnt_body_s   (vf3 N=224)
      header_n 等          -> fnt_head_n / fnt_head_s   (vf3 N=224)
      bodyital_overlay     -> fnt_bodyital_n/_s         (vf3 N=224)
  * charlist 有 2795 项，任何索引 >= 225 的中文字符在 224 字形的
    字体里越界，取到 vf3 数组之外的垃圾 U/V -> 渲染出错误的汉字。
  * HUD 文字走引擎默认字体（fnt_chinese）所以正常；底部字幕由
    hud_msg.lua 显式指定 "thin_overlay" -> fnt_body_n/s -> 乱码。

修复：把 6 个 font_info 的 <filename> 全部改成 fnt_chinese，
      3 个 <filename_overlay> 也改成 fnt_chinese（否则描边层仍用 224 字体）。
"""
import os, sys, hashlib, subprocess, shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
COMMON = os.path.join(G, "common.vpp_pc")
BAK_DIR = r"F:\sr2-cn\_backup_J"
BAK = os.path.join(BAK_DIR, "common.before_vintproj_font_20261014.vpp_pc")

# ---------------------------------------------------------- 1. 安全检查
def fail(msg):
    print("[ABORT]", msg)
    sys.exit(1)

out = subprocess.run(["tasklist"], capture_output=True).stdout
if b"sr2_pc.exe" in out.lower():
    fail("游戏仍在运行（PID 存在），请先退出游戏再执行写入。")

if not os.path.isfile(COMMON):
    fail("找不到 common.vpp_pc: " + COMMON)

before_md5 = hashlib.md5(open(COMMON, "rb").read()).hexdigest()
print("当前 common.vpp_pc md5 :", before_md5)
print("大小                   :", os.path.getsize(COMMON))

if not os.path.isfile(BAK):
    os.makedirs(BAK_DIR, exist_ok=True)
    shutil.copy2(COMMON, BAK)
    print("已备份 ->", BAK)
else:
    print("备份已存在，跳过 :", BAK)

# ---------------------------------------------------------- 2. 读 sr2.vint_proj
v = Vpp(COMMON)
ent = v.find("sr2", "vint_proj")
if ent is None:
    fail("sr2.vint_proj 条目未找到")

orig = v.read(ent)
orig_md5 = hashlib.md5(orig).hexdigest()
print("sr2.vint_proj 原 md5 :", orig_md5, "大小", len(orig))

# ---------------------------------------------------------- 3. 构造新 XML
# 只改 <filename> 与 <filename_overlay> 的值，不动 alias。
import re

def set_fields(block, path, newval):
    path = path.encode()
    """替换 <path>...</path> 的内容。"""
    pat = re.compile(rb"(<%s>)(.*?)(</%s>)" % (path, path), re.S)
    return pat.sub(lambda m: m.group(1) + newval + m.group(3), block, count=1)

text = orig

# font_info 块列表
blocks = re.findall(rb"<font_info>.*?</font_info>", text, re.S)
assert len(blocks) == 6, "font_info 块数异常: %d" % len(blocks)

new_blocks = []
changed = []
for blk in blocks:
    mf = re.search(rb"<filename>(.*?)</filename>", blk, re.S)
    ma = re.search(rb"<alias>(.*?)</alias>", blk, re.S)
    mo = re.search(rb"<filename_overlay>(.*?)</filename_overlay>", blk, re.S)
    fn = mf.group(1).strip()
    al = ma.group(1).strip()
    ov = mo.group(1).strip() if mo else b""
    nb = blk
    if fn != b"fnt_chinese":
        nb = set_fields(nb, "filename", b"fnt_chinese")
    if mo is not None and ov != b"fnt_chinese" and ov != b"":
        nb = set_fields(nb, "filename_overlay", b"fnt_chinese")
    if nb != blk:
        changed.append((al.decode(), fn.decode(), ov.decode()))
    new_blocks.append(nb)

assert len(changed) > 0, "没有任何改动？"
print("--- 将要修改的字体 ---")
for al, fn, ov in changed:
    print("  alias %-20s  %s (+overlay %s)" % (al, fn, ov or "-"))

new_text = orig
for old_blk, new_blk in zip(blocks, new_blocks):
    if old_blk != new_blk:
        assert new_text.count(old_blk) == 1, "块不唯一，中止"
        new_text = new_text.replace(old_blk, new_blk, 1)

# 尺寸校验：新的 XML 应能解析且长度合理
assert new_text.count(b"<font_info>") == 6
assert new_text.count(b"fnt_chinese") >= 6, "fnt_chinese 出现次数不足，中止"
print("新 sr2.vint_proj 大小 :", len(new_text), "(原 %d)" % len(orig))

# ---------------------------------------------------------- 4. 写回 vpp
v.replace_body_appended(ent, new_text, align=0x800)
v.save(COMMON)

# ---------------------------------------------------------- 5. 校验
new_md5 = hashlib.md5(open(COMMON, "rb").read()).hexdigest()
print("写入后 common.vpp_pc md5:", new_md5)

v2 = Vpp(COMMON)
chk = v2.read(v2.find("sr2", "vint_proj"))
assert chk == new_text, "回读校验失败！"
print("回读校验 : OK, md5", hashlib.md5(chk).hexdigest())
print()
print("=== 完成 ===")
