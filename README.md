# 黑道圣徒 2 简体中文汉化 · sr2-cn

《Saints Row 2》简体中文汉化、Juiced Patch 适配、DLC 汉化与原版遗留乱码修正。

当前发布：**v551 · Juiced Patch 9.3.1 · DLC 1.0.1 · SuperUI 2.9**。2026-10-26 补充地名与商店名提示、奖励载具移除警告，并修订两句法庭过场字幕；保留 v550 的名单、提示、统计、成就及竞速修正。

## 下载与安装

进入 [Releases](https://github.com/callpiu/sr2-cn/releases/tag/v551-20261026)，下载：

- **完整整合包**：`sr2-cn-v551-juiced-9.3.1-dlc-1.0.1-superui-2.9.zip`，包含汉化、Juiced、DLC、完整 SuperUI 配套文件与字幕修复安装器。
- **单独字幕修复**：`sr2-cn-helicopter-fix-v1.0.0.zip`，适合已经安装匹配简中资源和 Juiced 的玩家。
- **上游 CXT 修正条目**：`juiced_CH.hardcoded-fixes.cxt`，供 Juiced 作者合并六条中文硬编码文本；需要上游配套移除硬编码分支。

整合包需要已有可运行的游戏，不包含 `SR2_pc.exe`。GitHub 的自动生成 Source code ZIP 是项目源码；玩家安装请下载上述整合包。

1. 正常退出游戏，备份原文件及自定义 `juiced.ini`、`Mods`。
2. 解压完整整合包，将包内全部文件、文件夹复制到含 `SR2_pc.exe` 的游戏根目录，覆盖同名文件。
3. 双击游戏目录里的 **一键安装修复.cmd**，也可使用 **启动中文补丁管理器.cmd**。确认安装成功后重启游戏。
4. 保留原有中文启动设置；需要强制中文时，在 Steam 启动选项填写 `forcelang_ch`。

字幕修复会校验主程序与文本包的 SHA-256，不匹配时停止。Windows 自带 PowerShell 即可运行，玩家不需要 Python。

管理器的安装、检查、卸载只管理新增的字幕修复；整个整合包仍采用覆盖复制，回滚整包需要玩家自己的备份。验证游戏文件可能恢复被替换的资源；重新安装其他版本的 Juiced 也可能覆盖汉化文件。

旧 v546/v547 整合包只带了两个 SuperUI 定制脚本，漏带公共库和配套组件，在全新游戏目录可能卡在退出确认框、设置退出提示等位置。请使用 v551；已安装旧包也可覆盖升级。[根因与验证](docs/superui-dependency-fix.md)。

## 包含内容

| 模块 | 内容 |
| --- | --- |
| 本体简体汉化 | 简体文本、字体及字符表资源，地名、商店、菜单、任务等修正；v551 补全地名与商店提示及法庭字幕 |
| Juiced Patch 适配 | 9.3.1 菜单漏译、错译和缺字修正；OpenSpy 联机界面 12 条重译、等待玩家 SUI 标签修复 |
| 帮助菜单 | 四个入口完整中文；补齐 Sandbox++ 14 页标题与说明，保留 493 条指令编号 |
| SuperUI 配套 | 2.9 公共库、菜单/HUD 脚本及表资源；补回旧包遗漏的 64 个文件 |
| 清单与载入提示 | 30 个杀手目标、40 辆拆车厂目标的名称和说明；45 条不同载入提示（46 次引用） |
| 统计与成就 | 补齐 16 条统计标签、6 个成就名称及 37 项说明；兼容原生带空格的进度格式，竞速总数改为 PC 版实际的 27 场 |
| DLC 汉化 | DLC 1.0.1 配套的 982 条 slot 编码中文文本 |
| 直升机护卫乱码修复 | 将两个中文硬编码返回分支转回正常查表路径，只改变支持版本主程序的 16 字节 |
| 奖励载具与过场字幕 | 补全奖励载具移除确认框，修订“指定辩护律师”两句法庭字幕 |
| 上游协作资料 | 六条 CXT 条目、反汇编、补丁规则、构建与验证记录 |

## 验证与兼容范围

2026-10-26，用户重启后确认“指定辩护律师”中的“捡破鞋”和“蒂妮酒吧”提示、奖励载具移除确认框，以及两句修订后的法庭字幕均显示正常。[地名与商店提示](docs/store-place-prompts.md)、[车库警告与法庭字幕](docs/court-garage-text.md)。

同日，用户还确认名单左栏及详情、统计第 14/22 页和 22/22 页、成就名称及说明正常；随后确认原先显示 -1 的栏目恢复，最后单独确认“快速暴怒”的进度与 27 场说明正常。载入提示为代表性实测，未逐条查看全部 45 条；真实存档达到 27/27 的完成标记尚未实测，已用实际 Lua 回调覆盖完成边界。[汉化补全](docs/info-pages-second-revision-20261026.md)、[进度修复](docs/achievement-progress-20261026.md)。

2026-10-25，用户实机确认帮助菜单四个中文入口正常打开，Sandbox++ 列表及抽查说明正常，Juiced 的帧率、视野、鼠标轮盘和瞄准协助等选项显示完整。指令编号、顺序、网址与按键图标已静态核对；并未逐一执行全部 493 条指令。[菜单修正与验证](docs/menu-localization.md)。

2026-10-25，用户先确认只补公共库后退出和 Esc 恢复正常；补齐完整 SuperUI 组件并重启后，再次确认主菜单显示、Esc 返回、退出游戏全部正常。

用户已确认修复后、游戏重启后字幕正常，并于 2026-10-24 补充确认已逐级实机验证。直升机护卫 **2～6 级验证通过**；1 级原本正常。

原有自动验证包括 126 组语言/标签分支模拟、栈与寄存器保持检查、15 项安装/回退/恢复检查，以及 9 项管理器与命令入口检查。[详细记录](docs/helicopter-fix.md)与[机器可读验证报告](docs/evidence/installer-validation.json)区分了自动检查和用户实机反馈。

字幕修复验证环境：Steam App 9480 / Build 1076239、简中 v546 文本资源、Juiced 9.3.1。v547～v551 沿用该文本包。不同主程序、GOG 或其他汉化包未据此认定兼容。

| 文件状态 | SHA-256 |
| --- | --- |
| 支持的原始 `SR2_pc.exe` | `7d119931c7356a534f7a1b903dd6f920e417249d128438e939edb35b0dc2f244` |
| 修复后 `SR2_pc.exe` | `8bfc0c2a3606861837d8d831c5cdc1535db7d45813c809c04251018b5d4eecf7` |
| 配套 `patch.vpp_pc` | `e125d83628f8552035efc47e07778054ca593a718ba87570df03caa7a524d76b` |

已覆盖当前 SuperUI 脚本引用的全部载入提示；拆车厂杂志封面的英文属于贴图，仍保持原样。已有个别坏字位采用同义改写绕行，不能据此宣称所有游戏界面都无问题。[当前技术说明](docs/DEVELOPMENT.md)列出了资源读取路径和维护注意事项。

## 项目结构

```text
localization/payload/        已验证的本体文本包、DLC、Juiced 中文及完整 SuperUI 适配
localization/text/           按 ID 导出的 17,631 条文本记录及 2,795 项字符表
installer/                   可移植的 PowerShell 安装器、图形管理器与补丁规则
src/helicopter-fix/          16 字节补丁的 Python 构建与模拟验证源码
src/dlc/                     DLC 译文补充表及原始重建脚本
upstream/                    提供给 Juiced 作者的六条 CXT 修正
tools/                       可移植的项目校验、发行包重建工具
packaging/                   冻结的整合覆盖层、发行资产清单
docs/                        当前说明、验证证据
archive/                     历史构建/排障工具与交接文档，仅供追溯
third_party/                 原包许可及第三方声明
```

导出的 17,631 条是资源记录数，不代表本项目新增翻译数。`localization/payload` 是可部署的已验证基线；JSON 是便于审阅的严格回读导出，修改 JSON 不会自动改变二进制资源。

## 开发与重建

项目校验只需要 Python 3.12 标准库：

```powershell
python tools/verify_project.py
```

名单、提示和信息页的规范源为 `localization/text/list-tips.json`、`info-pages.json`；运行 `python tools/build_list_tips.py` 重建 CXT 和受管理的 Lua 修改。成就进度回归另需 `lupa==2.8`：`python tools/verify_achievement_progress.py`，CI 同样执行，覆盖 164 个有上限统计案例和 4 个竞速完成标记案例。

重建单独修复包（输出目录必须不存在）：

```powershell
python tools/build_release.py --output dist
```

重建整合包需要本地原始 `2026-10-21` v546 整合 ZIP，工具会核对其完整 SHA-256。该输入作为 [sr2-cn-v546-base-20261021.zip](https://github.com/callpiu/sr2-cn/releases/download/v547-20261024/sr2-cn-v546-base-20261021.zip) 保存在 v547 历史 Release，便于复现：

```powershell
python tools/build_release.py --base "sr2-cn-v546-base-20261021.zip" --output build/v551
```

脚本使用仓库内冻结的汉化载荷和覆盖层，生成后核对发布资产的 SHA-256；不读取或修改当前游戏安装。原始整合构建脚本保存在 `archive/legacy-tools`，包含本机绝对路径，不应直接批量运行。

发布文件校验值见 [SHA256SUMS.txt](SHA256SUMS.txt)。源码提交对应的 GitHub 自动 Source code 下载与 Release 安装包分别提供。

## 致谢与权利说明

Juiced Patch 由 **Kobraworks Modding Group 及贡献者**开发；本项目提供中文适配与相关修正，不代表 Juiced 官方发布。

- SuperUI for SR2 2.9：nclok1405；本次从用户提供的正常运行备份恢复配套文件，保留既有中文定制。
- [Juiced Patch 上游源码与发布](https://github.com/kobraworksmodding/Saints-Row-2-Juiced-Patch)
- [随原整合包保留的 Juiced GPL 许可、附加许可与第三方声明](third_party/juiced/)
- [本项目的第三方与资源说明](THIRD_PARTY.md)

游戏、DLC、原有译文和资源归各自权利人所有。仓库保留现有许可说明，未替不同来源的游戏资源或译文统一授予新的许可证。
