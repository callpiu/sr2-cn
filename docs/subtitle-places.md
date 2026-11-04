# 过场字幕地名与店名补译

截图中的「Rounds Square 购物中心」来自原生对白表 `voice_script_CH` 的 `0x2C9F3F0B`，与地图或任务提示使用的条目不同。沿用已经核对过的「朗兹广场购物中心」，保留原文末尾的换行和 `11000` 时长。

用同一对白表核对了蒂妮酒吧的两种英文拼法、法律边缘夜总会、关东和阿尔塔蒙特，共补译 11 条对白。另外补译了两条含「Rounds Square 购物中心」的新闻文本。

修正为两个独立 CXT：`sr2cn_subtitle_places_vcCH.cxt` 走 Juiced 的过场对白覆盖；`sr2cn_subtitle_places_CH.cxt` 走普通文本覆盖。与之前确认正常的法庭字幕使用同一种过场加载方式。两条带时长的对白保留原始数字，未替换本体文本包、游戏主程序或存档。

两个 CXT 已纳入 v552 完整整合包的载荷清单，并随一键覆盖安装部署。撤回时移除上述两个新增 CXT 即可，不会影响原有汉化、Juiced 或存档。

规范源为 `localization/text/subtitle-places.json`。运行 `python tools/build_subtitle_places.py --build` 重建到 `localization/payload`，并同步 `localization/manifest.json`；追加 `--archive <新 ZIP 路径>` 可生成只含两个 CXT 的小补丁。构建会核对原表哈希、记录 ID、已有覆盖是否重号、控制符与时长、字表覆盖及 CXT 回读。用户当前游戏目录已安装与规范源一致的两个文件；截图对应过场的完整重启回放确认仍待记录。
