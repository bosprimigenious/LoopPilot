# arXiv Paper Workspace

本目录为 **LoopPolit 项目内的本地 arXiv 论文草稿区**，已加入 `.gitignore`，不会进入版本库。

This folder is a **local arXiv LaTeX workspace** for LoopPolit-related papers. It is git-ignored and not tracked.

## 文件说明 / Files

| 文件 | 用途 |
|------|------|
| `main.tex` | 主文档：摘要、引言、相关工作、方法、实验、结论 |
| `references.bib` | BibTeX 参考文献（配合 `natbib` + `plainnat`） |
| `Makefile` | 一键编译 PDF |

## 编译 / Build

### 方式一：Make（推荐）

```bash
cd arxiv-paper
make
```

输出：`main.pdf`

### 方式二：手动 pdflatex + bibtex

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

### 中文正文 / Chinese text

若需在正文使用中文：

1. 在 `main.tex` 中取消 `xeCJK` 相关注释并设置字体；
2. 使用 `make xelatex` 或 `xelatex` + `bibtex` 流程编译。

## arXiv 投稿提示 / Submission notes

- 默认使用 `article` + 常见宏包，与 arXiv 兼容性较好。
- 投稿前可运行 `make clean`，仅打包 `.tex`、`.bib`、图片等源文件。
- 避免依赖本地-only 的自定义 `.sty`；必要时将宏包内联或一并上传。
