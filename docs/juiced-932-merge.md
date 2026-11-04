# Juiced Patch 9.3.2 合并说明

日期：2026-11-04

## 输入

上游包：

```text
SR2_JUICED_3.zip
SHA-256 d5b3436122cf7fd602be7719ddc79bcd24655a0e4f0e2ad630b196b31d1bc7f
```

本版以已经实机验证的 v551 完整整合包为基线：

```text
SHA-256 b969f09b2c863967a403bc321697c0bbec893162461450c3a8a72a1fffa97ecd
```

## 文件处理

相对 v551，9.3.2 有 5 个实际变化的可发布文件，另有 323 个相同文件。处理方式如下：

| 文件 | 处理 |
| --- | --- |
| `DFEngine.dll` | 采用 9.3.2 原始字节 |
| `Mods/JUICED - Lua Libraries/mouse_ui.lua` | 采用 9.3.2 原始字节 |
| `juiced.ini` | 采用 9.3.2 默认配置 |
| `Mods/JUICED - Strings/juiced_CH.cxt` | 保留 406 条项目译文并合入 6 条新增修正，共 412 条 |
| `Mods/JUICED - Strings/juiced_CH.le_strings` | 保留已经验证的 12 条 OpenSpy 简中表 |
| `DFEngine.pdb` | 调试符号，不发布 |

9.3.2 自带的 `juiced_CH.cxt` 只有 58 条。若直接覆盖，会丢失 354 条项目新增的菜单、帮助、Sandbox++、地名、名单和其他汉化。因此只从上游新增条目中提取下列 6 条：

- 统计资料损坏标题与正文
- 直升机护卫活动开始与移动交易提示
- 死亡标记与猫抓老鼠联机恢复提示

新增文本使用字面运行时 ID，保留了 `[format]`、`[/format]`、`{ATTACK_SECONDARY_IMG}` 与 `{ATTACK_PRIMARY_IMG}`。合并后文件为 UTF-8 无 BOM、CRLF，共 412 条。

9.3.2 的 `juiced_CH.le_strings` 仍使用相同的 12 个 OpenSpy ID，但文本为英文重建。项目保留现有简中表，避免服务器浏览器、排行榜和玩家信息界面退回英文。

## 上游功能

Juiced 9.3.2 发布说明还包含：

- 禁用原版硬编码中文字符串，并加入本项目提交的 6 条修正。
- 修复超宽屏下联机活动提示 HUD。
- 为服务器浏览器、排行榜和玩家信息界面增加鼠标 UI。
- 修复人物/玩家动画淡出后残留和切换异常。

## 验证状态

静态验证已覆盖：

- 412 条 CXT 可解析，6 个新增运行时 ID 与文本完全匹配。
- 两个统计条目各保留两行文本。
- 两个格式标签和两个输入图标占位符完整。
- UTF-8 无 BOM、全部换行均为 CRLF。
- `DFEngine.pdb` 未进入载荷。
- 12 条 OpenSpy 中文 `.le_strings` 回读一致。
- 全部 17,631 条文本表、SuperUI、菜单、地名、名单、法庭与车库检查继续通过。

实机验证尚待完成。建议至少检查主菜单、Esc、Juiced 设置菜单、OpenSpy 联机界面、超宽屏提示 HUD、2 级直升机护卫字幕和一场普通游戏内动画。
