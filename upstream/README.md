# Juiced 作者协作资料

`juiced_CH.hardcoded-fixes.cxt` 包含作者要求的六条繁中修正条目，UTF-8 无 BOM、CRLF 换行；格式标签、绿色标记与按键图标占位符保持完整，两条统计损坏提示各包含一个换行。

| 标签名 | CXT 字面 ID |
| --- | --- |
| STATS_CORRUPT_BODY | 0xFF6299D9 |
| STATS_CORRUPT_TITLE | 0x2370E5A4 |
| ACT_HELI_PROTECTION_START_MOVING_MESSAGE | 0xAF10621E |
| ACT_HELI_PROTECTION_START_MESSAGE | 0xF284ED87 |
| DIVERSION_COOP_DEATH_TAG_START_MESSAGE | 0xAB55CE3B |
| DIVERSION_COOP_CAT_AND_MOUSE_START_MESSAGE | 0x42363FC7 |

上述六个名称通过游戏本身的大小写不敏感哈希表计算，均对应这些值；无需为 STATS 两项假定特殊哈希。

作者需要配套移除旧的 CH 硬编码分支，让查询能到达 Juiced 的自定义字符串钩子，然后将条目合并至 `juiced_CH.cxt`。这些繁中协作条目未追加到当前已验证的简中载荷中。

可给作者的英文说明：

> Here are the six corrected Traditional Chinese entries in CXT format. The file is UTF-8 without BOM, uses CRLF, and preserves the formatting tags and input-icon placeholders. The two STATS entries use two physical lines to preserve their embedded newline. The literal hash headers match the game's lookup IDs. Please merge these entries into juiced_CH.cxt when removing the corresponding hardcoded Chinese branches. The helicopter protection fix has now also been tested in-game level by level (levels 2–6), and the text remains correct after restarting the game.
