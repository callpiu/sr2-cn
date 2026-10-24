import zipfile, hashlib, os

def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
PATCH_MD5_EXPECT = 'e71c1d338e6bb6da7b2b603903c312d7'
ROLLBACK_MD5_EXPECT = 'b430930fd03a2106e7fa810722ab2f29'
patch = G + 'patch.vpp_pc'
rollback = 'F:/sr2-cn/_发布包/patch_修复前_v407.vpp_pc'
if not os.path.exists(rollback):
    rollback = G + 'patch.vpp_pc.v407.rollback.bak'
assert md5(patch) == PATCH_MD5_EXPECT, md5(patch)
assert md5(rollback) == ROLLBACK_MD5_EXPECT, md5(rollback)

NAME = '黑道圣徒2简体汉化_整合修复包_17项_20261018.zip'
OUT = 'F:/sr2-cn/_发布包/' + NAME
files = [
    ('patch.vpp_pc', patch),
    ('DLC/Text/dlc_ch.le_strings', G + 'DLC/Text/dlc_ch.le_strings'),
    ('Mods/JUICED - Strings/juiced_CH.cxt', G + 'Mods/JUICED - Strings/juiced_CH.cxt'),
    ('Mods/JUICED - Strings/juiced_CH.le_strings', G + 'Mods/JUICED - Strings/juiced_CH.le_strings'),
    ('_回滚用/patch_修复前_v407.vpp_pc', rollback),
]

README = """黑道圣徒2 简体汉化 整合修复包 17项 (2026-10-18)
================================================
用法：解压，把文件按原目录结构覆盖到
  G:\\SteamLibrary\\steamapps\\common\\Saints Row 2\\

★★ 重要警告
  1) 千万不要在 Steam 里点「验证文件完整性 / 修复文件」，
     那会把 patch.vpp_pc 还原成官方英文原版，汉化与崩溃修复全部丢失。
  2) 不要重装原版 Juice 插件安装包，它会覆盖 Mods 下的两个 juiced 文件，
     导致 Juice 菜单缺字。本包内已含修复版，直接覆盖即可。
  3) 地图地名的「区」字由引擎自动补在 district 名之后。
     本包已把该 district 名从「城 」改为「市郊」，地图上现在显示「市郊区」。

★ 覆盖效果
  - Father误译「神父」→「父亲」（省吾台词，2 条 × 2 副本）
  - 地图 Suburbs 区域名 -> 「市郊区」（修复前显示「城区」）
  - 城郊 -> 市郊（32 处）
  - 散筒枪 -> 霰弹枪 / 火料 -> 弹药 / 填料 -> 弹药
  - 指定辩护律师（修复截断）
  - 兄弟会 / 三王 / 三街圣徒 等折中译名回滚
  - v532 哈希桶镜像重建（修复 !!unrecognized hash value）
  - 拆车厂崩溃修复

回滚：_回滚用/patch_修复前_v407.vpp_pc 为修复前的原始文件。
"""

flist = '\n'.join('%s  md5=%s  size=%d' % (n, md5(p), os.path.getsize(p)) for n, p in files)
flist += '\npatch.vpp_pc  md5=%s' % PATCH_MD5_EXPECT

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    for n, p in files:
        z.write(p, n)
    z.writestr('README.txt', README.encode('utf-8'))
    z.writestr('FILELIST.txt', flist.encode('utf-8'))

print('built', OUT, os.path.getsize(OUT), 'md5', md5(OUT))
with zipfile.ZipFile(OUT) as z:
    assert z.testzip() is None
    nl = z.namelist()
    print(len(nl), 'entries')
    assert not any(x.endswith(('.bak', '.new', '.orig')) for x in nl), nl
    h = hashlib.md5(z.read('patch.vpp_pc')).hexdigest()
    assert h == PATCH_MD5_EXPECT, h
    print('in-zip patch md5 OK', h)
    for x in nl:
        print('  ', x)