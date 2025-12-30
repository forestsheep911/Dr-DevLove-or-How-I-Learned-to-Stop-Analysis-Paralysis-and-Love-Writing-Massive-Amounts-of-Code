# Dr. DevLove (開発の愛)
### *あるいは：私が如何にして分析麻痺を止めて大量のコードを書くことを愛するようになったか*

[![GitHub license](https://img.shields.io/github/license/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code)](https://github.com/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code/blob/main/LICENSE)

> "諸君、ここで喧嘩は駄目だ！ここは作戦室だぞ！" — *ドクター・ストレンジラブ*
>
> "開発者諸君、ここで考えすぎては駄目だ！ここはIDEだぞ！" — *ドクター・デブラブ*

点滅するカーソルを見つめるのに疲れていませんか？慢性的な*分析麻痺*に苦しんでいませんか？コードを書く時間よりも、コードを計画する時間の方が長くなっていませんか？

**Dr. DevLove** (別名 `gh-stats`) が処方箋です。これは、あなたが*働いている*ことを証明するCLIツールです。ローカルクローンを必要とせず（ディスク容量の無駄ですからね）、GitHub宇宙全体での毎日のコード貢献を追跡することで、あなたの存在を証明します。

---

[English](./README.md) | [🇨🇳 简体中文](./README.zh-CN.md) | [🇹🇼 繁體中文](./README.zh-TW.md) | [🇯🇵 日本語](./README.ja.md) | [🇰🇷 한국어](./README.ko.md) | [🇪🇸 Español](./README.es.md) | [🇫🇷 Français](./README.fr.md) | [🇸🇦 العربية](./README.ar.md) | [🇮🇳 हिन्दी](./README.hi.md)

---

## 💊 処方箋 (機能)

*   **遠隔診断**: API経由でGitHubのアクティビティを直接スキャンします。ローカルリポジトリは不要です。
*   **バイタルサイン**: 詐欺師症候群（インポスター・シンドローム）よりも速く回転するプログレスバーを備えた、美しいカラーターミナル出力。
*   **スケーラブルな治療**: 個人プロジェクトから大規模な組織まで対応します。
*   **タイムトラベル**: `today` (今日)、`yesterday` (昨日)、`thisweek` (今週)、`lastweek` (先週) など、柔軟な期間設定が可能です。
*   **証拠収集**: 全てのコミットメッセージをMarkdownファイルにエクスポート。AIによる分析や週報の作成に最適です。
*   **トリアージモード**: 最終プッシュ日時でリポジトリを自動ソートし、最新の「救済」プロジェクトを優先的に表示します。

## 📥 服用方法 (インストール)

Dr. DevLoveにはPython 3.9以上とGitHub CLI (`gh`)が必要です。

### 1. 依存関係のインストール

```bash
# GitHub CLIのインストール
brew install gh
gh auth login
gh auth refresh -s read:org  # 組織リポジトリのスキャンに必須
```

### 2. Poetryのインストール

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 3. 服用

```bash
git clone https://github.com/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code.git
cd Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code
poetry install
```

## 📋 用法・用量 (使用法)

```bash
# 今日何かしたことを確認する
poetry run gh-stats --range today

# 今月働いたことを上司に証明する
poetry run gh-stats --range thismonth --orgs YOUR_COMPANY_ORG

# AI要約用エクスポート - 先週の全コミットメッセージを出力
poetry run gh-stats --range lastweek --export-commits
```

### パラメータ

| フラグ | 効果 | デフォルト |
| :--- | :--- | :--- |
| `--range` | 日付の短縮形 (`today`, `yesterday`, `lastweek`, `3days` など) | なし |
| `--no-personal` | 個人のリポジトリを除外する | - |
| `--export-commits` | コミットメッセージをMarkdownに出力 | False |
| `--all-branches` | 全アクティブブランチをスキャン | False |

## 📄 ライセンス

MIT. 好きに使ってください、ただコードを書きましょう。
