# Quiet Violet 0.2

**Claude CLI 的粉蓝／红蓝原色 + Quiet Light 的淡紫界面。**

Quiet Violet v0.2.0 为 VS Code、kitty 和 Windows Terminal 提供浅色与深色配色。代码与 Diff 配色来自 Claude Code **2.1.322**，独立终端配置沿用主题内置终端的 16 个 ANSI 色槽。

## 使用

扩展包含两个主题：

- **Quiet Violet Light**：GitHub 代码配色，粉色关键词、深蓝字符串，浅蓝新增／浅粉删除。
- **Quiet Violet Dark**：Monokai Extended 代码配色，粉色关键词、青色声明词、淡黄字符串，深蓝新增／暗红删除。

按 **Ctrl+K，再按 Ctrl+T**，搜索 `Quiet Violet`。可分别设为首选浅色／深色颜色主题，并启用 VS Code 的自动检测配色方案。

下载 [v0.2.0 安装包](dist/quiet-violet-0.2.0.vsix)，在扩展页 `…` → **从 VSIX 安装…** 中选择该文件。VS Code 集成终端会跟随当前主题。

## 独立终端

**kitty**：下载 [浅色配置](terminal/kitty-light.conf) 或 [深色配置](terminal/kitty-dark.conf)，放在 `kitty.conf` 同一目录。在 `kitty.conf` 末尾加入 `include kitty-dark.conf`（浅色用 `include kitty-light.conf`），重新打开 kitty 即可。

**Windows Terminal**：打开设置，选择「打开 JSON 文件」。把[配色文件](terminal/windows-terminal.json)数组内的两个对象追加到设置的 `schemes` 数组中，保留已有方案。保存后，在所用配置文件的「外观 → 配色方案」选择 `Quiet Violet Light` 或 `Quiet Violet Dark`。

浅色终端的 16 个 ANSI 色槽各有独立色值。红色采用柔和的玫瑰红，绿色和青色各自独立，品红槽使用紫色。六种彩色及其亮色按感知明度均衡调整，平均 OKLCH L 约为 0.55，与终端底色的对比度均达到 4.5∶1。深色终端在 `#1E1E1E` 背景上使用珊瑚红、草绿、琥珀黄、蓝、淡紫和青绿，普通彩色的 OKLCH L 约为 0.73，亮彩色约为 0.80。kitty、Windows Terminal 与 VS Code 集成终端使用相同的映射。可用下列命令在兼容 POSIX 的 shell 中查看全部 16 色：

```sh
for code in 30 31 32 33 34 35 36 37 90 91 92 93 94 95 96 97; do
  printf '\033[%sm %s \033[0m' "$code" "$code"
done
printf '\n'
```

## 主要原色

| 用途 | 浅色 | 深色 |
| --- | --- | --- |
| 关键词 | `#A71D5D` | `#F92672` |
| const / let / function 等声明词 | `#A71D5D` | `#66D9EF` |
| 字符串 | `#183691` | `#E6DB74` |
| 函数名 | `#795DA3` | `#A6E22E` |
| 数字 / 字面量 | `#0086B3` | `#BE84FF` |
| 注释 | `#969896` | `#75715E` |
| Diff 新增行 | `#DBEDFF` | `#001B29` |
| Diff 删除行 | `#FFDCDC` | `#3D0100` |

**界面紫色独立保留**：浅色标题栏 `#C4B7D7`、按钮和状态栏 `#705697`、焦点 `#9769DC`；深色使用对应紫色。紫色不再替代代码本身的原色。

## 忠实度与可读性边界

- 语法表原色、状态表原色、代码 Diff 渲染色分别记录；没有把 `diffAdded` 等界面 token 误当成代码渲染的最终背景。
- CLI 使用 highlight.js；VS Code 使用 TextMate／语言服务。已按语法类别映射同一套原色，但不同解析器的个别 token 分类可能不同，不承诺逐字像素一致。
- 原版灰色注释、部分青色／粉色语法颜色并非都达到 4.5:1。为符合这次“按实际 CLI 原色”的要求，**不擅自加深、提亮或换成橙色**。对比度报告如实列出不足，不宣称全部文字通过 WCAG。
- 工作台常用正文、按钮、选中项和状态提示另做对比度检查；源码选中时使用可读前景。Diff 保留 `+ / −`、错误保留图标和波浪线。
- 终端真彩色由应用决定；VS Code ANSI 槽只能影响 ANSI 输出，不能覆盖应用自己的 24 位颜色。

## 来源与构建

完整来源、二进制偏移、两层 palette 的区别见 [设计说明](DESIGN.md)。可机器读取的提取结果位于 `sources/claude-code-2.1.322-palette.json`。本主题非 Anthropic 或 Microsoft 官方产品。

无需第三方依赖：

```sh
python3 -I tools/build.py
python3 -I tools/check.py
```

可安装文件：`dist/quiet-violet-0.2.0.vsix`。扩展只含主题数据，不执行代码、不联网、不遥测。
