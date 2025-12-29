# GitHub Stats (gh-stats)

一个强大且美观的命令行工具，用于统计 GitHub 贡献数据。支持个人仓库及组织仓库，直接通过 GitHub API 获取数据，无需本地克隆代码。

## 🌟 特性

- **精准统计**：基于 GitHub Commits API，准确统计指定时间范围内的提交数及代码行数变化。
- **美观输出**：内置彩色表格展示，实时进度条反馈。
- **零代码克隆**：直接调用 `gh` CLI，无需将仓库克隆到本地。
- **智能过滤**：
    - 支持按个人/组织维度过滤。
    - 自动按最近活跃时间（Pushed at）排序，优先扫描最近工作的项目。
    - 可分别设置个人和组织的扫描仓库上限（Limit），在大规模组织中也能快速得到结果。
- **灵活的时间范围**：支持 `today`, `week`, `month`, `quarter`, `year` 简写，或自定义 `--since`/`--until` 日期。

## 🛠️ 环境要求

1. **Python 3.9+**
2. **GitHub CLI (`gh`)**: 必须安装并登录。
    - 安装：`brew install gh`
    - 登录：`gh auth login`
    - *建议对组织仓库进行 SSO 授权*：`gh auth refresh -s read:org`

## 🚀 快速开始

### 安装

本项目使用 [Poetry](https://python-poetry.org/) 进行管理。

```bash
# 安装依赖并创建环境
poetry install

# 使用 poetry 运行
poetry run gh-stats --range week
```

### 常用命令示例

```bash
# 查看本周统计（包含个人项目和默认组织限制）
gh-stats --range week

# 查看本月某个组织的统计，最近活跃的 30 个仓库
gh-stats --range month --orgs SH-SE --org-limit 30

# 只看个人项目，最近活跃的 10 个仓库
gh-stats --range today --no-personal --personal-limit 10

# 自定义日期范围
gh-stats --since 2023-12-01 --until 2023-12-31
```

## ⚙️ 参数说明

| 参数 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `--personal` / `--no-personal` | 是否包含个人仓库 | `True` |
| `--orgs` | 需要统计的组织名称（逗号分隔） | `""` |
| `--since` | 开始日期 (YYYY-MM-DD) | 今天 |
| `--until` | 结束日期 (YYYY-MM-DD) | 今天 |
| `--range` | 时间范围简写 (`today`, `week`, `month`, `quarter`, `year`) | - |
| `--personal-limit` | 个人仓库扫描上限（按活跃排序） | `20` |
| `--org-limit` | 每个组织仓库扫描上限（按活跃排序） | `50` |

## 📁 项目结构

```text
viewgithub/
├── src/
│   └── gh_stats/       # 核心逻辑
│       ├── main.py     # 主程序
│       └── __init__.py
├── scripts/
│   └── gh-stats.sh     # Shell 脚本版本 (内部使用 Events API)
├── pyproject.toml      # Poetry 配置
├── README.md           # 项目文档
└── .gitignore          # Git 忽略配置
```

## 📝 注意事项

- **API 限制**：频繁运行可能会触及 GitHub API 的速率限制。
- **SAML SSO**：如果统计组织仓库显示为 0 或 403 错误，请确保已通过 `gh auth refresh -s read:org` 并完成了 SSO 授权。
