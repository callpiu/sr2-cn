# 当前维护说明

本说明更新于 2026-10-26。历史文档的早期猜测不覆盖当前实验证据。

## 资源路径

游戏中文资源从 `patch.vpp_pc` 中的 `charlist_CH`、`static_CH`、`voice_script_CH` 和 `platform_pc_CH` 读取；Juiced 的松散资源可能优先于 VPP 内同名条目。适配还涉及 `Mods/dialog_box.lua`、`Mods/JUICED - Strings/juiced_CH.cxt` 与 `juiced_CH.le_strings`。DLC 中文位于 `DLC/Text/dlc_ch.le_strings`。

本项目以冻结的 v546 汉化资源为载荷基线，v547 加入可回退的直升机护卫字幕修复，v548 补齐 SuperUI 2.9 依赖，v549 以 CXT 覆盖修正帮助、Juiced 菜单与 Sandbox++ 帮助，v550 增补名单、提示与信息页，并修复成就进度格式与竞速总数。仓库中的本体文本包与 Release 使用相同字节；不会从维护者当前运行的游戏目录自动采集配置。

## le_strings

经当前工具验证的布局为 12 字节头（magic、version、bucket count、record count），随后为每桶 8 字节的桶表、LE u32 指针数组，以及 `[4-byte ID][BE u16 slot...][0000]` 记录。文本 slot 大于等于 32 时，以 `charlist[slot - 32]` 解码；小于 32 的控制值原样保留。

导出 JSON 的 ID 按记录原始四字节的大端数值表示，与本次 EXE 比较常量一致。历史脚本存在交换 16 位字后的不同表示法，维护时必须比较原始四字节，不能仅凭旧文档的数字推断同一标签。

不要采用历史 `sr2strings.py` 的 16 字节头假设。`tools/verify_project.py` 会逐条核对 JSON ID、索引、文本与冻结二进制资源，验证所有五张表的 17,631 条记录。导出 JSON 仅供审阅；修改文本需要重建 slot 编码资源、保留桶与指针关系、复查格式标签并重新实机验证。

## 直升机护卫根因

`SR2_pc.exe!0x007F4BC0` 在 CH 语言下对六个特殊哈希返回 `.rdata` 里的旧硬编码数据，绕过正常查表；这两句活动提示的数据包含过时的字符索引，导致官方繁中和简体汉化均可出现乱码。

已验证的临时与永久修复只将两个命中分支跳转回 `0x007F4BE8`。总计 16 字节变更，其他四个分支保持原行为。可移植安装器先校验 EXE 和文本包，再备份、暂存并替换；卸载恢复经校验的原程序。

`upstream/juiced_CH.hardcoded-fixes.cxt` 额外提供六条繁中原文，供上游在移除全部六个硬编码分支后使用。它是上游集成资料，不是当前独立安装器的替代品。六个普通标签名通过引擎大小写不敏感哈希计算均与 EXE 常量一致；使用字面哈希标题只是明确指定查询 ID，两条 `STATS_*` 无需另造特殊哈希。

## 证据边界

2026-10-23 的记录证明了 2 级两句提示修复、重启后正常，以及安装回退和模拟检查。2026-10-24 用户补充“我已实机逐级验证过了”，据此将 2～6 级逐级实测状态更新为通过；来源为用户反馈，无新增截图。

原自动报告中的时间和历史路径保留用于追溯，不把旧机器路径作为可移植构建依赖。历史工具的依赖可能包含 numpy、Pillow、pefile、unicorn、OpenCC 等；现行项目静态校验使用标准库，成就 Lua 回归另需 `lupa==2.8`。

## SuperUI 依赖

`Mods/dialog_box.lua`、`Mods/city_load.lua` 是 SuperUI 版本，必须与同版 `Mods/vint_lib.lua` 和配套组件共同发布。`localization/superui-manifest.json` 固定 66 个文件；其中 64 个在 v548 补回。源数据来自正常运行备份，并与原始 SuperUI_vanilla.7z 清单对齐。原包的 loose static_CH 表未出现在正常备份中，不能覆盖本项目已验证的简中 slot 表。

`tools/verify_superui.py --directory <目录>` 校验配套文件哈希，并检查 SuperUI Lua 调用有相应定义；此检查也加入项目 CI。v547 发布目录应检查失败，v548 应通过。详细证据见 [SuperUI 缺项修复](superui-dependency-fix.md)。

菜单 CXT 的结构、字符覆盖与帮助指令编号验证由 `tools/verify_menu_strings.py` 完成，并纳入项目 CI。`localization/text/superui-help.json` 保留 SuperUI 英文来源与中文译文；CXT 才是实际加载的文本。更新译文需同步两者。
