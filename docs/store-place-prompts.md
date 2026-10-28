# 地名与商店名提示补译：v551 修复

2026-10-26 的截图显示“指定辩护律师”中两句提示仍含 `Sloppy Seconds` 和 `TeeNay`。它们属于 `static_CH` 内完整的任务提示字符串，单独翻译商店标题不会替换其中嵌入的英文。

本次以原始字符串 ID 添加 61 条 CXT 覆盖，覆盖任务目的地、相关离店确认、折扣通知和地点菜单文本。商店优先沿用已有中文名；`Sloppy Seconds` 为“捡破鞋”，`TeeNay` 与 `Tee'N'Ay` 统一为“蒂妮酒吧”。音像店、希腊卷饼公司标题与上一版已汉化的杀手档案译名统一。所有译名及原文见 `localization/text/store-places.json`。

Juiced 的 `MStrings::get_localization_from_hash` 优先查询自定义 CXT 哈希表，未命中再调用原生查找。使用原始 ID 可以覆盖整句 HUD 提示，并保留其中的颜色、输入图标和格式占位符。冻结的字符串表、Lua 脚本、可执行文件和存档均不需要修改。

重建与校验：

```powershell
python tools/build_store_places.py
python tools/verify_project.py
```

先前列表/提示重建器如需重跑，执行顺序为 `build_list_tips.py`、`build_store_places.py`。后者检查完整 v550 CXT 前缀的哈希，以防覆盖先前翻译。重复重建结果一致。

自动验证覆盖原始 ID/索引/文本、原表哈希、UTF-8 无 BOM、CRLF、全部控制符和段落、2795 字位覆盖，以及先前 345 条 CXT 文本未改动。`verify_achievement_progress.py` 的 Lua 5.1 回归验证也通过。

2026-10-26，用户完整重启并安装后实机确认“指定辩护律师”中的
“在捡破鞋买几件新衣服”和“前往蒂妮酒吧”两句提示显示正常，颜色、
缺字和换行无异常。本修复纳入 v551。
