import zipfile, hashlib, os

def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
EXPECT = {
    'patch.vpp_pc': 'e71c1d338e6bb6da7b2b603903c312d7',
    'Mods/dialog_box.lua': 'f89645e132f3e65bf9284e68ce7de2cc',
    'Mods/dialog_box.lua.sui.bak': '4dc698b8eb797eeafec1c6c80a3c1ac1',
    'DLC/Text/dlc_ch.le_strings': 'eedbc779ffbef51c4200aafa73892039',
    'Mods/JUICED - Strings/juiced_CH.cxt': 'f0c1d9b291d371e1faefb5d44ccecdbe',
    'Mods/JUICED - Strings/juiced_CH.le_strings': '21dde0bc7638c595505d9b1cd339a0ec',
}
ROLLBACK_MD5 = 'b430930fd03a2106e7fa810722ab2f29'
rollback = 'F:/sr2-cn/_发布包/patch_修复前_v407.vpp_pc'
assert md5(rollback) == ROLLBACK_MD5, md5(rollback)

for rel, exp in EXPECT.items():
    got = md5(G + rel)
    assert got == exp, '%s 期望 %s 实际 %s' % (rel, exp, got)
    print('OK  %-46s %s' % (rel, got))

NAME = '黑道圣徒2简体汉化_整合修复包_18项_20261018.zip'
OUT = 'F:/sr2-cn/_发布包/' + NAME

files = [
    ('patch.vpp_pc', G + 'patch.vpp_pc'),
    ('DLC/Text/dlc_ch.le_strings', G + 'DLC/Text/dlc_ch.le_strings'),
    ('Mods/JUICED - Strings/juiced_CH.cxt', G + 'Mods/JUICED - Strings/juiced_CH.cxt'),
    ('Mods/JUICED - Strings/juiced_CH.le_strings', G + 'Mods/JUICED - Strings/juiced_CH.le_strings'),
    ('Mods/dialog_box.lua', G + 'Mods/dialog_box.lua'),
    ('_回滚用/patch_修复前_v407.vpp_pc', rollback),
]

README = """黑道圣徒2 简体汉化 整合修复包 18项 (2026-10-18)
================================================
用法：解压，把文件按原目录结构覆盖到
  G:\\SteamLibrary\\steamapps\\common\\Saints Row 2\\

★★ 重要警告
  1) 千万不要在 Steam 里点「验证文件完整性 / 修复文件」，
     那会把 patch.vpp_pc 还原成官方英文原版，汉化与崩溃修复全部丢失。
  2) 不要重装原版 Juice 插件安装包，它会覆盖 Mods 下的文件，
     导致修复失效。本包内已含修复版，直接覆盖即可。
  3) 地图地名的「区」字由引擎自动补在 district 名之后。
     本包已把该 district 名从「城 」改为「市郊」，地图上显示「市郊区」。

★ 本包新增（第18 项）
  联机「等待玩家」对话框不再漏出英文 tag SUI_LAN_COOP_SP。
  原因：Juice mod 自己造了一个官方不存在的 tag 当正文，引擎查不到译文
        只能把tag 原文打在屏幕上。
  修法：Mods/dialog_box.lua 里改用官方真实 tag MENU_TITLE_NOTICE（显示「注意」），
        第二选项由误用的 LEADERBOARDS_SP（=单人游戏）改回官方的 CONTROL_CANCEL（=取消）。
  原始文件备份在 Mods/dialog_box.lua.sui.bak，需要回滚直接覆盖回去。

★ 其余 17 项
  - Father 误译「神父」→「父亲」（省吾台词）
  - 地图 Suburbs 区域名 -> 「市郊区」
  - 城郊 -> 市郊（32 处）
  - 散筒枪 -> 霰弹枪 / 火料 -> 弹药 / 填料 -> 弹药
  - 指定辩护律师（修复截断）
  - 兄弟会 / 三王 / 三街圣徒 等折中译名回滚
  - v532 哈希桶镜像重建（修复 !!unrecognized hash value）
  - charlist count= 修复（坏字位与活动字幕乱码的总根因）
  - 拆车厂崩溃修复

回滚：_回滚用/patch_修复前_v407.vpp_pc 为修复前的原始文件。
"""

flist = '\n'.join('%s  md5=%s  size=%d' % (n, md5(p), os.path.getsize(p)) for n, p in files)
flist += '\nMods/dialog_box.lua.sui.bak  md5=%s  size=%d (备份，未打入包)' % (
    EXPECT['Mods/dialog_box.lua.sui.bak'], os.path.getsize(G + 'Mods/dialog_box.lua.sui.bak'))

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    for n, p in files:
        z.write(p, n)
    z.writestr('README.txt', README.encode('utf-8'))
    z.writestr('FILELIST.txt', flist.encode('utf-8'))

print()
print('built', OUT, os.path.getsize(OUT), 'md5', md5(OUT))
with zipfile.ZipFile(OUT) as z:
    assert z.testzip() is None
    nl = z.namelist()
    print(len(nl), 'entries')
    assert not any(x.endswith(('.new', '.orig')) for x in nl), nl
    assert z.read('patch.vpp_pc') and md5  # noop
    import io
    h = hashlib.md5(z.read('patch.vpp_pc')).hexdigest()
    assert h == EXPECT['patch.vpp_pc'], h
    h2 = hashlib.md5(z.read('Mods/dialog_box.lua')).hexdigest()
    assert h2 == EXPECT['Mods/dialog_box.lua'], h2
    print('in-zip md5 verified: patch + dialog_box')
    for x in nl:
        print('  ', x)