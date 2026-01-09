# Dr. DevLove (開發之愛)
### *或者是：我如何學會停止分析癱瘓並愛上瘋狂寫程式*

[![GitHub license](https://img.shields.io/github/license/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code)](https://github.com/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code)](https://github.com/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code/stargazers)

> "先生們，這裡不能打架！這是作戰室！" — *奇愛博士*
>
> "開發者們，這裡不能過度思考！這是 IDE！" — *開發之愛博士*

你是否厭倦了盯著閃爍的游標發呆？你是否患有慢性*分析癱瘓*？你花在計畫程式碼上的時間是否比實際寫程式的時間還長？

**Dr. DevLove** (即 `gh-stats`) 就是你的處方藥。它證明了你*確實*在工作中。它透過追蹤你在 GitHub 宇宙中的每日程式碼貢獻來驗證你的存在，而且不需要本地複製倉庫——畢竟誰有那麼多硬碟空間呢？

---

[English](./README.md) | [🇼 繁體中文](./README.zh-TW.md)

---

## 💊 處方 (特性)

*   **遠端診斷**: 直接透過 API 掃描你的 GitHub 活動。無需本地倉庫。
*   **生命徵象**: 美觀的彩色終端輸出和進度條，旋轉速度比你的冒名頂替症候群發作還快。
*   **可擴展治療**: 無論是個人專案還是龐大的組織專案均可使用。
*   **時光旅行**: 查看 `today` (今天)、`yesterday` (昨天) 等多種預設或自定義的時間範圍。
*   **證據採集**: 將所有 Commit Message 導出為 Markdown 文件，方便 AI 分析或撰寫週報。
*   **分診模式**: 自動按最後推送日期排序，讓你優先看到最近“搶救”回來的專案。

## 📥 服用方法 (安裝)

Dr. DevLove 需要 Python 3.9+ 和 GitHub CLI (`gh`)。

### 1. 安裝依賴

#### macOS / Linux

```bash
# 安裝 GitHub CLI
brew install gh

# 認證 GitHub
gh auth login

# 組織存取權限（正確診斷所必需）
gh auth refresh -s read:org
```

#### Windows

```powershell
# 安裝 GitHub CLI（使用 winget，Windows 10 1709+ 自帶）
winget install --id GitHub.cli

# 認證 GitHub
gh auth login

# 組織存取權限（正確診斷所必需）
gh auth refresh -s read:org
```

### 2. 安裝 Poetry

```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# macOS / Linux
curl -sSL https://install.python-poetry.org | python3 -
```

### 3. 服藥

複製這個名字超長的倉庫並使用 Poetry 安裝：

```bash
git clone https://github.com/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code.git
cd Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code
poetry install
```

## 📋 劑量 (使用)

執行工具查看統計。副作用可能包括突如其來的成就感。

```bash
# 證明你今天工作了
poetry run gh-stats --range today

# 查看昨天的工作
poetry run gh-stats --range yesterday

# 向老闆證明你這個月都在工作
poetry run gh-stats --range thismonth --orgs YOUR_COMPANY_ORG

# AI 總結神器 - 導出上週所有 commit message
poetry run gh-stats --range lastweek --export-commits

# 導出完整版 commit message（包含正文）到指定檔案
poetry run gh-stats --range lastweek --export-commits --full-message --output weekly_report

# 圍觀大佬 - 查看其他用戶的公開倉庫活動
poetry run gh-stats --user torvalds --range thismonth

# 查看同事在組織內的貢獲
poetry run gh-stats --user colleague_name --orgs YOUR_COMPANY_ORG --range lastweek
```

### 參數

| 標誌 | 效果 | 預設值 |
| :--- | :--- | :--- |
| `--user` | 目標 GitHub 用戶名（可查看他人公開倉庫統計，或組合 --orgs 查看同事） | 當前認證用戶 |
| `--range` | 日期簡寫 (如 `today`, `yesterday`, `thisweek`, `lastweek`, `lastmonth`, `3days`) | 無 |
| `--date-after` / `--date-before` | 自定義起止時間 (YYYYMMDD, now-1week) | - |
| `--since` / `--until` | 同上 | - |
| `--orgs` | 逗號分隔的組織名稱 | 無 |
| `--no-personal` | 排除個人倉庫 | - |
| `--personal-limit` | 掃描的個人倉庫上限 | 自動 |
| `--org-limit` | 每個組織掃描的倉庫上限 | 自動 |
| `--all-branches` | 啟用全分支掃描 | False |
| `--export-commits` | 導出 Commit Message 到 Markdown 檔案 | False |
| `--full-message` | 導出時包含完整的 Commit 正文（預設只導出標題） | False |
| `--output` / `-o` | 指定導出檔案名（預設儲存到 `reports/` 目錄） | 自動產生 |
| `--org-users` | 團隊模式：比較指定組織內所有貢獻者的統計 | False |
| `--highlights` | 顯示洞察資訊（最長連續提交、最高產日期等） | False |
| `--group-by` | 導出分組方式：`user`（按用戶）或 `repo`（按倉庫），用於 `--org-users` | `user` |

### 📅 高級用法

**1. 靈活的相對日期 (yt-dlp 風格)**
- `--range 3days` (過去3天)
- `--date-after 20240101` (YYYYMMDD 格式)
- `--date-before now-2weeks` (相對時間)

**2. 🌿 多分支掃描**
使用 `--all-branches` 來捕獲活躍分支上的所有提交。

```bash
gh-stats --range 3days --all-branches
```

**3. 📝 AI 分析導出 (AI-Ready)**
使用 `--export-commits` 生成 Markdown 文件，非常適合直接投餵給大模型（LLM）來生成專業的工作總結。

```bash
gh-stats --range lastweek --export-commits
```

**4. 👥 查看同事貢獲**
使用 `--user` 配合 `--orgs` 查看同一組織內同事的工作貢獲。程式會掃描您有權限存取的組織倉庫，篩選出目標用戶的提交。

```bash
# 查看同事 alice 在 YOUR_COMPANY_ORG 組織內的貢獲
poetry run gh-stats --user alice --orgs YOUR_COMPANY_ORG --range lastweek --export-commits
```

**注意**: 當組織倉庫超過 64 個時，程式會詢問您是否全部掃描，或輸入一個數量限制（倉庫按最近更新時間排序）。

**5. 📁 導出檔案管理**
- 所有導出檔案預設儲存到 `reports/` 目錄
- 使用 `--output` 可指定自定義檔案名
- 檔案名衝突時會自動追加序號，不會覆蓋舊檔案

```bash
# 指定檔案名導出
poetry run gh-stats --range lastweek --export-commits --output my_weekly_report
# 輸出: reports/my_weekly_report.md
```

**6. 🏆 個人亮點**
使用 `--highlights` 查看您的編碼模式洞察，包括最長連續提交天數、最高產的一天、最愛的工作日等。

```bash
poetry run gh-stats --range month --highlights
```

**7. 👥 團隊模式（組織對比）**
使用 `--org-users` 比較組織內所有貢獻者的統計數據。此模式會掃描組織內所有倉庫，並按貢獻者彙總統計。

```bash
# 查看 YOUR_COMPANY_ORG 本月所有貢獻者的對比
poetry run gh-stats --orgs YOUR_COMPANY_ORG --org-users --range thismonth

# 導出團隊統計，按倉庫分組（而非按用戶）
poetry run gh-stats --orgs YOUR_COMPANY_ORG --org-users --range lastweek --output team_report --group-by repo
```

## 📄 授權條款

MIT. 想怎麼用就怎麼用，只要寫程式就行。
