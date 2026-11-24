# 0.2 配色来源与纠偏

日期：2026-11-16。

## 用户要求与修正

用户截图要求的是实际 Claude CLI 的**粉蓝／红蓝**效果，同时保留 Quiet Light 的淡紫界面主强调。0.1 把删除色改成橙色、代码改成自设计蓝橙色，偏离了要求。0.2 删除这项自作主张，直接采用本机原色。

## 直接读取当前本机，不再使用旧 npm 版本推测

提取工具读取 Claude Code **2.1.322** 的原生可执行文件。运行时请提供实际二进制文件路径。

该 ELF 文件内含可读 JavaScript。提取工具只读取 mmap 字节，不执行提取出的代码，也不修改 CLI 本身。

```sh
python3 -I tools/extract_cli_palette.py \
  /path/to/claude-native \
  /path/to/capture.ansi
```

输出：`sources/claude-code-2.1.322-palette.json`，记录二进制 SHA-256、表／选择器的文件字节偏移、全部颜色和已有原生终端输出的 SHA-256。偏移从 0 开始。工具固定核查 2.1.322，不把旧布局套到未来版本。

## 两层配色必须区分

### 1. 界面状态表

主题模块起点 byte **288943791**，选择器 `c4(r)` 明确将 `light-daltonized` 映射至 `W`，`dark-daltonized` 映射至 `P`。如 success 为浅色 `#006699`／深色 `#3399FF`，error 为 `#CC0000`／`#FF6666`。

此表的 `background` 不是整个终端底色。`diffAdded` / `diffRemoved` 也不能直接代表截图中代码 Diff 的最终背景。

### 2. 代码与代码 Diff 渲染器

byte **317289482** 附近的 `ge(e)` 选择主题名称：含 dark → **Monokai Extended**，其他非 ANSI → **GitHub**。

- 深色语法表 `G`，约 byte **317289594**。
- 浅色语法表 `P`，约 byte **317290274**。
- 渲染选择器 `V(e,n)`，约 byte **317291284**。
- `daltonized` 改变 Diff 新增色，**不另换语法 scopes 表**。
- storage 词集合包含 const、let、var、function、class、type、interface、enum 等；`ye` 将这些 keyword 映射为 `_storage`，故深色声明词是青色而其他 keyword 是粉色。

| 原 scope | GitHub 浅色 | Monokai Extended 深色 |
| --- | --- | --- |
| keyword / operator | `#A71D5D` | `#F92672` |
| _storage | `#A71D5D` | `#66D9EF` |
| built_in / type | `#0086B3` | `#A6E22E` |
| title.function | `#795DA3` | `#A6E22E` |
| title.class | `#000000` | `#A6E22E` |
| number / literal / symbol | `#0086B3` | `#BE84FF` |
| string / regexp | `#183691` | `#E6DB74` |
| params | `#0086B3` | `#FD971F` |
| comment / meta | `#969896` | `#75715E` |
| attr / attribute | `#0086B3` | `#A6E22E` |
| variable / property | `#0086B3` | `#FFFFFF` |
| punctuation / subst / 默认 | `#333333` | `#F8F8F2` |

`V` 在 truecolor daltonized 模式下的代码 Diff：

| 用途 | 浅色 | 深色 |
| --- | --- | --- |
| 新增行 | `#DBEDFF` | `#001B29` |
| 新增词 | `#B3D9FF` | `#003047` |
| 新增符号 | `#24578A` | `#51A0C8` |
| 删除行 | `#FFDCDC` | `#3D0100` |
| 删除词 | `#FFC7C7` | `#5C0200` |
| 删除符号 | `#CF222E` | `#DC5A5A` |

这些值也与本机既有真实终端 ANSI 记录中的输出吻合。原生非 truecolor 终端会使用 256 色量化，此处采用源 RGB 原色。

## VS Code 映射

原始 scope 值映射到 TextMate 与语义高亮类别；不再把函数名改成界面紫色，也不人为给代码添加粗体／斜体。不同解析器个别分类可能不同，不能承诺逐字一致。

Diff 行背景直接使用渲染器原值；词背景采用可透出的 RGBA，经与行背景合成后精确得到原版 word 值。这样既保持截图效果，也不使用不透明词背景遮蔽编辑器装饰。

仅工作台保留 Quiet Light 紫色：浅色标题栏 `#C4B7D7`、按钮／状态栏 `#705697`、焦点 `#9769DC`；深色为相应紫色。编辑区使用接近用户截图的中性浅／深底色。

## 验证与限制

`tools/check.py` 对照提取记录，严格验证代码原色、状态色、Diff 行背景、合成后的词背景、语义高亮与主题包。工作台常用文字检查 4.5:1。

原版语法 palette 的若干颜色本来达不到 4.5:1；保持用户要求的原色，并在报告 `nativeBelowAAOnEditor` 中逐项列出，而非修改原色后继续声称“忠实”。未做医学保证或完整 WCAG 认证。

`dist/` 仅保留 v0.2.0 安装包、对比度报告 `contrast-report.json`、VS Code 渲染报告 `vscode-render-report-v0.2.0.json` 和 `preview-v0.2.0-*` 截图。

## 现成主题检索记录

前轮未找到明确同时移植 CLI 色盲模式、又保留 Quiet Light 紫色的现成主题。[GitHub Theme](https://marketplace.visualstudio.com/items?itemName=GitHub.github-vscode-theme) 确有亮暗色盲主题，但不是本次完整组合。[Claude Theme for VS Code by SK](https://marketplace.visualstudio.com/items?itemName=sathishsk-me.claude-theme-for-vscode)、[Claude Mode](https://marketplace.visualstudio.com/items?itemName=TheWebDev.claude-mode) 有类似风格，未见对应来源声明。检索未找到不等于断言全网不存在。
