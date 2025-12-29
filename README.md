# Dr. DevLove 
### *or: How I Learned to Stop Analysis Paralysis and Love Writing Massive Amounts of Code*

[![GitHub license](https://img.shields.io/github/license/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code)](https://github.com/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code)](https://github.com/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code/stargazers)

> "Gentlemen, you can't fight in here! This is the War Room!" — *Dr. Strangelove*
>
> "Developers, you can't overthink in here! This is the IDE!" — *Dr. DevLove*

Are you tired of staring at a blank cursor? Do you suffer from chronic *Analysis Paralysis*? Do you spend more time planning your code than actually writing it?

**Dr. DevLove** (alias `gh-stats`) is your prescription. It's a CLI tool that proves you *are* getting work done. It validates your existence by tracking your daily code contributions across the GitHub universe, bypassing the need for local clones because who has disk space for that?

---

[English](./README.md) | [🇨🇳 简体中文](./README.zh-CN.md) | [🇹🇼 繁體中文](./README.zh-TW.md) | [🇯🇵 日本語](./README.ja.md) | [🇰🇷 한국어](./README.ko.md) | [🇪🇸 Español](./README.es.md) | [🇫🇷 Français](./README.fr.md) | [🇸🇦 العربية](./README.ar.md) | [🇮🇳 हिन्दी](./README.hi.md)

---

## 💊 The Prescription (Features)

*   **Remote Diagnostics**: Scans your GitHub activity directly via API. No local repositories required.
*   **Vital Signs**: Beautiful, colored terminal output with progress bars that spin faster than your imposter syndrome.
*   **Scalable Treatment**: Works for personal projects and massive organizations alike.
*   **Time Travel**: Check your stats for `today`, `this week`, `this month`, or `this year`.
*   **Triage Mode**: Automatically sorts repositories by last push date, so you see your most recent "saves" first.

## 📥 Intake (Installation)

Dr. DevLove requires Python 3.9+ and the GitHub CLI (`gh`).

### 1. Install Dependencies
```bash
brew install gh
gh auth login
# For organizational access (REQUIRED for proper diagnosis):
gh auth refresh -s read:org
```

### 2. Take the Medicine
Clone this massive repository and install with Poetry:

```bash
git clone https://github.com/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code.git
cd Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code
poetry install
```

## 📋 Dosage (Usage)

Run the tool to see your stats. Side effects may include a sudden sense of accomplishment.

```bash
# Verify you did something today
poetry run gh-stats --range today

# Prove to your boss you worked this month
poetry run gh-stats --range month --orgs YOUR_COMPANY_ORG

# The "I'm a 10x Engineer" view (Personal repos only, top 10)
poetry run gh-stats --range year --no-personal --personal-limit 10
```

### Parameters

| Flag | Effect | Default |
| :--- | :--- | :--- |
| `--range` | Date shorthand (e.g. `today`, `3days`, `week`) | None |
| `--date-after` / `--date-before` | Check window (YYYYMMDD, now-1week) | - |
| `--since` / `--until` | Alias for above | - |
| `--orgs` | Comma-separated organization names | None |
| `--personal-limit` | Max personal repos to scan | Automatic (based on range) |
| `--org-limit` | Max repos per organization to scan | Automatic (based on range) |
| `--all-branches` | Enable scanning of all active branches | False (default branch only) |

### 📅 Advanced Usage

**1. Flexible Date Ranges (yt-dlp style)**
Supports natural language and concise formats:
- `--range 3days` (last 3 days)
- `--date-after 20240101` (YYYYMMDD)
- `--date-before now-2weeks` (relative)

**2. 🌿 Multi-Branch Scanning**
By default, the tool only counts commits on the default branch (usually `main`).
If you are working on multiple feature branches in parallel, use `--all-branches` to capture all your recent activity across these branches.
This works by intelligently analyzing your GitHub Events stream.

```bash
gh-stats --range 3days --all-branches
```

## 🧪 Clinical Trials

Tested on developers who thought they wrote "nothing" all day, only to discover they pushed 300 lines of config changes.

## 📄 License

MIT. Do whatever you want, just write code.
