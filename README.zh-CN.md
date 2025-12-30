# Dr. DevLove (开发之爱)
### *或者是：我如何学会停止分析瘫痪并爱上疯狂写代码*

[![GitHub license](https://img.shields.io/github/license/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code)](https://github.com/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code)](https://github.com/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code/stargazers)

> "先生们，这里不能打架！这是作战室！" — *奇爱博士*
>
> "开发者们，这里不能过度思考！这是 IDE！" — *开发之爱博士*

你是否厌倦了盯着闪烁的光标发呆？你是否患有慢性*分析瘫痪*？你花在计划代码上的时间是否比实际写代码的时间还长？

**Dr. DevLove** (即 `gh-stats`) 就是你的处方药。它证明了你*确实*在干活。它通过追踪你在 GitHub 宇宙中的每日代码贡献来验证你的存在，而且不需要本地克隆仓库——毕竟谁有那么多硬盘空间呢？

---

[English](./README.md) | [🇨🇳 简体中文](./README.zh-CN.md) | [🇹🇼 繁體中文](./README.zh-TW.md) | [🇯🇵 日本語](./README.ja.md) | [🇰🇷 한국어](./README.ko.md) | [🇪🇸 Español](./README.es.md) | [🇫🇷 Français](./README.fr.md) | [🇸🇦 العربية](./README.ar.md) | [🇮🇳 हिन्दी](./README.hi.md)

---

## 💊 处方 (特性)

*   **远程诊断**: 直接通过 API 扫描你的 GitHub 活动。无需本地仓库。
*   **生命体征**: 美观的彩色终端输出和进度条，旋转速度比你的冒充者综合症发作还快。
*   **可扩展治疗**: 无论是个人项目还是庞大的组织项目均可使用。
*   **时间旅行**: 查看 `today` (今天)、`yesterday` (昨天)、`thisweek` (本周)、`lastweek` (上周)、`thismonth` (本月)、`lastmonth` (上月)、`thisyear` (本年)、`lastyear` (去年) 的统计数据。
*   **分诊模式**: 自动按最后推送日期排序，让你优先看到最近“抢救”回来的项目。

## 📥 服用方法 (安装)

Dr. DevLove 需要 Python 3.9+ 和 GitHub CLI (`gh`)。

### 1. 安装依赖
```bash
brew install gh
gh auth login
# 组织访问权限（正确诊断所必需）：
gh auth refresh -s read:org
```

### 2. 服药
克隆这个名字巨长的仓库并使用 Poetry 安装：

```bash
git clone https://github.com/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code.git
cd Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code
poetry install
```

## 📋 剂量 (使用)

运行工具查看统计。副作用可能包括突如其来的成就感。

```bash
# 证明你今天干活了
poetry run gh-stats --range today

# 查看昨天的工作
poetry run gh-stats --range yesterday

# 向老板证明你这个月都在工作
poetry run gh-stats --range thismonth --orgs YOUR_COMPANY_ORG

# 查看上周的统计
poetry run gh-stats --range lastweek

# "我是 10 倍工程师" 视图 (仅个人仓库，前 10 个)
poetry run gh-stats --range thisyear --no-personal --personal-limit 10
```

### 参数

| 标志 | 效果 | 默认值 |
| :--- | :--- | :--- |
| `--range` | 日期简写 (如 `today`, `yesterday`, `thisweek`, `lastweek`, `thismonth`, `lastmonth`, `thisyear`, `lastyear`, `3days`) | 无 |
| `--date-after` / `--date-before` | 自定义起止时间 (YYYYMMDD, now-1week) | - |
| `--since` / `--until` | 同上 (为了兼容性保留) | - |
| `--orgs` | 逗号分隔的组织名称 | 无 |
| `--personal-limit` | 扫描的个人仓库上限 | 自动 (根据range) |
| `--org-limit` | 每个组织扫描的仓库上限 | 自动 (根据range) |
| `--all-branches` | 启用全分支扫描 (默认只扫主线) | False |

### 📅 高级用法

**1. 常用时间范围表达**
支持更符合实际语言习惯的时间范围参数：
- **当前时间范围**：
  - `--range today` (今天)
  - `--range thisweek` (本周，从周一到今天)
  - `--range thismonth` (本月，从1号到今天)
  - `--range thisyear` (本年，从1月1日到今天)
- **历史时间范围**：
  - `--range yesterday` (昨天)
  - `--range lastweek` (上周，完整的一周)
  - `--range lastmonth` (上月，完整的一个月)
  - `--range lastyear` (去年，完整的一年)

**2. 灵活的相对日期 (yt-dlp 风格)**
支持自然语言和缩写，例如：
- `--range 3days` (过去3天)
- `--date-after 20240101` (YYYYMMDD 格式)
- `--date-before now-2weeks` (相对时间)

**注意**：为保持向后兼容，原有的 `week`、`month`、`year` 参数仍然可用，分别等同于 `thisweek`、`thismonth`、`thisyear`。

**3. 🌿 多分支扫描**
默认情况下，工具只统计默认分支（因为这通常代表了最终贡献）。
如果您在多个 Feature 分支上并行工作且尚未合并，使用 `--all-branches` 来捕获这些活跃分支上的所有提交。
此功能通过智能分析 GitHub Events 来定位您最近活动过的分支。

```bash
gh-stats --range 3days --all-branches
```

## 🧪 临床试验

已在那些认为自己整天“什么都没写”的开发者身上进行测试，结果发现他们其实推送了 300 行配置更改。

## 📄 许可证

MIT. 想怎么用就怎么用，只要写代码就行。
