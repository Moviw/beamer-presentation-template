---
name: beamer-presentation-template
description: Create, modify, compile, and export classic academic LaTeX Beamer presentations using built-in themes such as Madrid, Berlin, Warsaw, and Copenhagen. Use this skill for paper-reading presentations, research progress reports, academic talks, thesis defenses, and requests for traditional Beamer-style PDF, PPTX, or Keynote slides.
---

# Beamer 经典演示文稿模板技能

制作、修改、导出 **经典学术风格** 的 LaTeX Beamer 演示文稿：顶部章节导航条、Madrid 蓝色主题、规整的标题页和页脚状态条。适用于读论文、研究进展汇报、开题 / 答辩、组会、会议报告。

## 文件

| 路径 | 用途 |
| --- | --- |
| `assets/template/presentation.tex` | 模板：Madrid + 默认配色，带常用宏、两列 Outline、示例页（要点 + Takeaway、长文字表、结果表、图文两栏、时间线、总结） |
| `assets/template/components.tex` | 组件库（约 20 页）：block / 定理 / tcolorbox、逐步显示、公式、并排子图、整页大图、宽表与高亮行、pgfplots 曲线、TikZ 流程图、代码、文献引用（`refs.bib`）、链接与二维码、讲稿、参考文献页、致谢页、不计页码的备用页、每节自动目录、logo |
| `assets/template/.latexmkrc` | `latexmk` 配置：中间文件放 `build/`，成功后把 PDF 拷回本目录 |
| `scripts/contact_sheet.py` | 把 PDF 渲染成缩略图拼图，并列出日志里的溢出警告 |
| `scripts/pdf2pptx.py` | 从最终 PDF 导出 `.pptx`；macOS 上加 `--key` 再转成 `.key` |
| `scripts/mcp_server.py` | MCP server：`new_deck` / `compile_deck` / `contact_sheet` / `render_page` / `export_pptx`，拼图和单页以图片返回 |

## 硬性规则

- **一律从附带模板开始**：把 `assets/template/` 整个复制到目标目录再改。只用 Beamer 内置主题（默认 Madrid；用户点名 Berlin / Warsaw / Copenhagen 等时只换 `\usetheme{}`），不下载任何第三方模板，不用 metropolis 等现代主题，不装字体，不换 lualatex。
- **用户给了自己的 .tex 模板时用用户的**，保留其主题、配色、标题页、页脚、导航符号和板块样式，只改内容。
- **幻灯片内容一律用英文**，除非用户明确要求其他语言。

## 工作流

1. **复制模板**，改标题区：`\title[短标题]{全标题}`、`\subtitle{}` 只放论文或报告的副标题，汇报性质（如 Progress Report）和日期一起写在 `\date{}` 里。
2. **定篇幅**：3 分钟分享 3–4 页；组会读论文 8–12 页；进展汇报 8–15 页；开题 10–18 页；会议报告 12–20 页。信息不明确且影响目标时才问用户。
3. **定结构**：
   - 读论文：标题 → 背景 → 动机 → 核心思路 → 方法总览 → 关键技术点 → 实验设置 → 主要结果 → 消融 → 总结 → 讨论。
   - 进展汇报：标题 → 贡献与证据 → 设置（模型 / 数据 / 指标）→ 各项结果 → 剩余工作与时间线 → 总结。
4. **写内容**（见下方排版规则），每个 frame 前放一个 `\subsection{}`，让 Outline 列出每页。需要图表、公式、流程图、代码、引用、二维码、备用页等元素时，从 `components.tex` 复制对应 frame 和它用到的宏包，不要从头写。
5. **编译与检查**：`latexmk`，再跑 `contact_sheet.py` 看所有页，有溢出就修（见下）。
6. **导出**：用户要 PPT / Keynote 时用 `pdf2pptx.py`。

## 内容与排版

- **标题**：用陈述句或像论文小节一样的名称（如 "Main Results on X"、"Ablation Study"），不要每页都用问句。
- **每页一件事**：3–5 条要点，或「图 / 表 + 几条说明」的两栏。术语第一次出现时用一句大白话解释。
- **Takeaway 只放关键页**（全篇 4–6 个左右），用模板里的 `takeaway` 环境，一句话写出数字结论。
- **表格**：用 `booktabs`；大表只留最有说服力的几行，其余口头讲。长文字列用模板里的 `L{宽度}` 左对齐定宽列，避免两端对齐把字距拉开。未出的结果用 `\tbd`，标准差用 `\sd{}`，表注写清指标、±含义和题数。
- **Outline**：模板是两列（`\tableofcontents[sections={1-5}]` / `{6-10}`），章节多时调分界；条目太挤时减小 `\vspace`。
- **时间线**：一行写清一个时间段做什么，不要事无巨细；带具体时刻时写明时区（如 JST），截止时间按 AoE 换算。
- **一致性**：改了数字或模型数量后，全文搜一遍（Takeaway、Summary、Outline 小节名、表注），例如 five → six；已解决的事项（如待批准的决定）及时删掉。
- **图**：优先用论文原图或矢量 PDF，放 `fig/`；不拉伸、裁掉留白、配一句说明。

## 编译、自动刷新与检查

```bash
latexmk                                    # 编译一次（读 .latexmkrc）
latexmk -pvc -interaction=nonstopmode      # 持续模式：保存即重新编译，阅读器打开 presentation.pdf 会自动刷新
python3 scripts/contact_sheet.py presentation.pdf   # 生成 presentation_contact.png，并列出 Overfull 警告
pdftoppm -png -r 90 -f N -l N presentation.pdf page # 单页放大看细节
```

- **不要在 `latexmk -pvc` 运行时再手动编译同一目录**：两个进程同时写 `build/presentation.pdf` 会把 PDF 写坏（pdftoppm 报 "Kid object is wrong type"）。要么停掉 `-pvc`，要么只改 .tex 让它自己编译。
- **每次改完都看图**，不能只看编译日志：确认没有溢出、没有缺图、表格没超宽、字号能读。`Overfull \hbox` / `\vbox` 都要修：精简文字、缩表宽（`\setlength{\tabcolsep}`、`\resizebox`）或缩小图，不要放任裁切。
- Mac 的「预览」不会自动刷新；用 Skim（打开「检查文件变化」）、VS Code 的 PDF 预览或 evince。

## 导出 .pptx / .key

PDF 是权威版本，`.pptx` 和 `.key` 都从最终 PDF 转换，每页一张高清图铺满 16:9 幻灯片，视觉与 PDF 完全一致，不用 python-pptx 重新排版文字。

```bash
python3 scripts/pdf2pptx.py presentation.pdf             # → presentation.pptx（默认 200 dpi）
python3 scripts/pdf2pptx.py presentation.pdf --key       # macOS：再用 Keynote 另存为 presentation.key
```

需要 `pdftoppm`（poppler）和 `python-pptx`（`pip install python-pptx`）。`.key` 只能在装了 Keynote 的 macOS 上生成；在 Linux 上只交付 `.pptx` 并说明原因。导出的幻灯片里文字不能逐个编辑，用户明确要求可编辑时要先说明这一点。

## MCP（可选）

`scripts/mcp_server.py` 把上面的流程包装成 MCP 工具，依赖由 `uv` 按脚本里的内联声明自动安装：

```bash
claude mcp add beamer -- uv run --script <skill 目录>/scripts/mcp_server.py
```

| 工具 | 作用 |
| --- | --- |
| `new_deck(dest)` | 复制模板到新目录 |
| `compile_deck(directory, tex)` | `latexmk` 编译，返回页数和错误 / 溢出 |
| `contact_sheet(pdf)` | 所有页的缩略图拼图（图片） |
| `render_page(pdf, page)` | 单页放大（图片） |
| `export_pptx(pdf, keynote)` | 导出 `.pptx`，macOS 上可再转 `.key` |

有 MCP 时优先用工具编译和看图；没有时用上面的命令行。

## 交付前检查

- [ ] 从附带模板开始，经典风格保持：导航条、标题页、页脚、Madrid 默认配色
- [ ] 内容是英文；页数符合用途
- [ ] 标题不是一串问句；Takeaway 只在关键页
- [ ] `contact_sheet.py` 看过所有页，0 处 Overfull
- [ ] 数字和计数全文一致
- [ ] 交付 .tex 和 PDF；要求 PPT / Keynote 时附从 PDF 转出的文件
