# 车库奖励载具警告与法庭字幕修订

2026-10-26，本修复已通过实机复核，纳入 v551。

## 车库警告

`Mods/garage.lua` 的 `garage_remove_reward_vehicle` 请求
`SUI_DELETE_REWARD_VEHICLE_WARNING`（`0xBC2C80DF`）。该标签存在于
SuperUI 的 `Mods/static_US.le_strings`，中文原表和已有 CXT 覆盖中均缺失。
普通载具走 `GARAGE_REMOVE_PROMPT`，奖励载具才走这个分支。

补齐完整提示，保留原文四个换行及中间空行：

> 你即将删除一辆奖励载具。  
> 奖励载具不占用车库的 64 辆载具名额。  
> 删除后将无法再次获得这辆载具。
>
> 确定要从车库中移除这辆载具吗？

## 指定辩护律师过场

英文取自 `patch.vpp_pc/voice_script_US.le_strings`，其 SHA-256 为
`90e7481a53721a0edfbf12aaa8fa01f1b5fe3d19f25e5f2a5711662c308cf479`。

- `LEE_TSSP02_CUT02_1` / `0x0E93DFF8`：
  `My client would like that stricken from the record... ` →
  `我当事人请求……刚才那段就别记进笔录了。`
- `LEE_TSSP02_CUT02_2` / `0x979A8E42`：
  `Anyone hit and need a lawyer?` → `有人中枪吗？需不需要律师？`

第二句发生在法庭枪战后，hit 指中枪；原译“被抓”误解了情境。
律师躲完枪战就揽客的喜感保留在措辞与情境中。

## 构建与验证

规范源为 `localization/text/court-garage.json`。
执行 `python -X utf8 tools/court_garage_strings.py --build` 生成两个独立 CXT：

- `Mods/JUICED - Strings/sr2cn_garage_CH.cxt`
- `Mods/JUICED - Strings/sr2cn_court_vcCH.cxt`

Juiced MStrings 的 `StartParsing` 读取 CH.cxt；`StartParsingVoice`
读取 `_vcCH.cxt`，过场查询优先查对应 voice map。现有 DFEngine.dll
含 voice CXT 后缀，SHA-256 为
`263ec33e6dad4f3a46ed8f24726f10e5fbba44206d95e17f6aa3019eb696d7c8`。
未修改 DLL、EXE、Lua、原生中文表及存档。

`python -X utf8 tools/verify_project.py` 验证原文与 ID、UTF-8 无 BOM、
CRLF、换行与字库覆盖，并检查 garage.lua 中所有 SUI 文本标签都有中文来源。
现有 406 条 CXT 保持原字节。

用户完整重启游戏后确认奖励载具的移除确认框显示完整中文（选择“否”，
未实际删除载具），并重播法庭过场确认两句新字幕均正常。本修复纳入 v551。
