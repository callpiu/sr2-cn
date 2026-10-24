# 黑道圣徒 2 简体中文 —— 工作区索引

> **状态：已停止开发。** 游戏处于可正常游玩的干净状态。
> 未完成的核心问题见 **[交接_字形定位问题.md](交接_字形定位问题.md)**（另有更详细的 [交接文档.md](交接文档.md)）。

---

## 一、当前游戏状态（**干净、可玩**）

| 项目 | 值 |
|---|---|
| `patch.vpp_pc` | 48,857,216 字节，SHA256 `60E196F0...CCFBD` —— **与官方完全一致** |
| `textures.vpp_pc` | 1,261,819,104 字节 —— **原始** |
| `Mods\static_CH.le_strings` | **稳定版**：746 条转简体，无缺字、无乱码 |
| 字体 / 字符表 | **未做任何改动** |

**一键还原**：`还原官方繁中.bat` 或 `restore_official_TC.bat`

---

## 二、成果总结

### 已完成（有硬证据）

| 环节 | 结论 | 证据 |
|---|---|---|
| VPP 容器 | 附录式替换可行，只需改目标条目 | 全部构建基于此 |
| `.le_strings` | `u32 CRC` + UTF-16**BE**，`00 00` 结尾 | 7670 条转换正确 |
| 文本转换 | **完全正确，离线验证通过** | `1吗？听好，这里需要一台救护车。...` |
| 引擎字符表来源 | **`patch.vpp_pc` 的 `charlist_CH.txt`** | 换 3610 项后 `num_cchars = 3610` |
| 槽位公式 | **`slot = charlist行号 + 32`** | `车→2870, 来→2871, 会→2872` 完美连续 |
| `compress_char` | 已反汇编，与 Juiced 源码吻合 | `0x7F4F60` 真实机器码 |
| 调试能力 | **已具备**（`DebugActiveProcess` 可附加） | `sr2_dbgprobe` 实测 True |
| 硬件断点 | **已跑通**（62 线程，Dr0/Dr7） | `sr2_hwbp` |

### 未完成（**唯一阻塞点**）

**字形图集的「槽位 → 单元格」映射公式未知。**

已证伪的六个假设：

| 假设 | 验证结果 |
|---|---|
| `cell = slot - 32` | ❌ 得到 貨 |
| `cell = slot` | ❌ |
| `cell = slot - 94` | ❌ 得到 話 |
| 图集按 Unicode 排序 | ❌ 得到 迅/噢/悉/繼 |
| 模板匹配 | ❌ 最高相关 0.51 |
| 从字符表反推 | ❌ 图集 2697 格 vs 字符表 2838 项，非 1:1 |

**因为无法确定布局，新增的 772 个字形曾被写到错误位置、覆盖了原有字形**（导致「衣」「房」「存」消失）。现已全部撤回。

---

## 三、目录说明

### 📄 文档

| 文件 | 内容 |
|---|---|
| `交接_字形定位问题.md` | **本轮交接文档**：未解问题、排除过的假设、下一步正确方向 |
| `交接文档.md` | 早期主文档：格式规范、引擎映射机制、踩坑记录 |

### 🔧 调试工具（**本轮新增，均可复用**）

| 文件 | 用途 |
|---|---|
| `sr2_memread.exe` | 读引擎字符表（`cc_list` / `num_cchars` / 逐字槽位） |
| `sr2_dbgprobe.exe` | 测试调试附加 + 读任意地址机器码 |
| `sr2_hwbp.exe` | **硬件断点工具**（Dr0/Dr7）。改 `ADDR_TARGET` 常量即可断在任意地址 ★ |
| `sr2_slot_trace.exe` | 软件断点 + 调用栈追踪 |
| `sr2_hwbp_v2.cs` 等 | 上述工具的源码（`csc /platform:x86` 编译） |

### 🔧 格式库

| 文件 | 用途 |
|---|---|
| `tools\sr2lib.py` | **格式库**：VPP 读写、字符表、VFNT、DXT3 编解码 |
| `tools\sr2patch.py` | `.le_strings` 读写与单元解码 |
| `build_stable.py` | 生成稳定版（只转有字形的字） |
| `build_final.py` | 生成完整版（含 772 新字形，**图集定位仍错**） |

### 📦 交付包

| 目录 | 说明 |
|---|---|
| `SR2_简体中文补丁_稳定版\` | **当前已装**。`install.bat` / `uninstall.bat`，零风险 |
| `SR2_简体中文补丁_安全版\` | 与稳定版等价 |
| `SR2_简体中文补丁_完整版\` | 全量版（未完成，图集定位有误） |

### 💾 原始数据（**重要，勿删**）

| 目录 | 说明 |
|---|---|
| `pristine\` | **原始快照**：`patch.vpp_pc`、`static_CH.le_strings`、`juiced_CH.le_strings` |
| `vpp_backup\` | 原始 `patch.vpp_pc` 与 `textures.vpp_pc` 完整备份 |
| `mlpack\patch.vpp_pc` | 官方多语言补丁原件（与 pristine 同哈希） |
| `jptools\` | SR2 JP Strings Tools 源码（编码规则权威来源） |
| `pylibs\` | OpenCC 等依赖 |

---

## 四、关键校验值

```
原始 patch.vpp_pc
  大小   : 48,857,216
  SHA256 : 60E196F08F96A25686959FDD40BA3EBB3662527828BBCFC07951177D923CCFBD

原始 textures.vpp_pc
  大小   : 1,261,819,104
```

任何时候不确定游戏是否干净，用这些值比对。

---

## 五、环境

| 项目 | 路径 |
|---|---|
| 游戏 | `G:\SteamLibrary\steamapps\common\Saints Row 2` |
| Python | `C:\Users\ezplayer\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe` |
| Steam 启动选项 | `forcelang_ch`（启用官方繁中） |
| x32dbg 快照 | `D:\下载\Compressed\snapshot_2026-05-27_12-11\release\x32\` |

### 关键地址（SR2_pc.exe **无 ASLR**，绝对地址）

| 地址 | 含义 |
|---|---|
| `0x7F4F60` | `compress_char`（Unicode → 槽位） |
| `0x7F4430` | `loadcharlist`（被 Juiced 挂钩，首字节 `E9`） |
| `0x02528B2C` | `cc_list` 指针（`{u16 unicode; u16 compressed}[]`） |
| `0x02528B30` | `num_cchars` |

---

## 六、给接手者的一句话

**不要在文本处理流程里找字形布局，要去字形渲染流程里找。**

`compress_char` 是**加载期**调用（已用硬件断点证实：100 秒 0 触发），不是渲染期。
建议从 `IDirect3DDevice9::CreateTexture` / `D3DXCreateTextureFromFileInMemory` 或 `DrawText` 类函数入手，
找到**接收槽位并输出 UV 矩形**的那个函数。
