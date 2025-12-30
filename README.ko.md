# Dr. DevLove (개발의 사랑)
### *또는: 내가 어떻게 분석 마비를 멈추고 방大な 양의 코드를 쓰는 것을 사랑하게 되었는가*

[![GitHub license](https://img.shields.io/github/license/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code)](https://github.com/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code/blob/main/LICENSE)

> "여러분, 여기서 싸우면 안 됩니다! 여기는 작전실입니다!" — *닥터 스트レンジ러브*
>
> "개발자 여러분, 여기서 너무 생각하면 안 됩니다! 여기는 IDE입니다!" — *닥터 데브러브*

깜빡이는 커서를 멍하니 바라보는 데 지쳤나요? 만성적인 *분석 마비*에 시달리고 있나요? 코드를 쓰는 시간보다 계획하는 데 더 많은 시간을 소비하고 있나요?

**Dr. DevLove** (별칭 `gh-stats`)가 당신의 처방전입니다. 이 도구는 당신이 *일하고 있음*을 증명하는 CLI 도구입니다. 로컬 클론 없이도(디스크 공간은 소중하니까요) GitHub 전체에서의 일일 코드 기여를 추적하여 당신의 존재를 증명합니다.

---

[English](./README.md) | [🇨🇳 简体中文](./README.zh-CN.md) | [🇹🇼 繁體中文](./README.zh-TW.md) | [🇯🇵 日本語](./README.ja.md) | [🇰🇷 한국어](./README.ko.md) | [🇪🇸 Español](./README.es.md) | [🇫🇷 Français](./README.fr.md) | [🇸🇦 العربية](./README.ar.md) | [🇮🇳 हिन्दी](./README.hi.md)

---

## 💊 처방 (주요 기능)

*   **원격 진단**: API를 통해 GitHub 활동을 직접 스캔합니다. 로컬 저장소가 필요 없습니다.
*   **바이탈 사인**: 임포스터 증후군보다 빠르게 회전하는 진행 표시줄과 아름다운 컬러 터미널 출력.
*   **확장 가능한 치료**: 개인 프로젝트부터 대규모 조직까지 모두 지원합니다.
*   **시간 여행**: `today` (오늘), `yesterday` (어제), `thisweek` (이번 주), `lastweek` (지난주) 등 유연한 기간 설정.
*   **증거 수집**: 모든 커밋 메시지를 Markdown 파일로 내보내기. AI 분석이나 주간 보고서 작성에 완벽합니다.
*   **트리아지 모드**: 마지막 푸시 날짜순으로 저장소를 자동 정렬하여 최근 프로젝트를 우선적으로 보여줍니다.

## 📥 복용 방법 (설치)

Dr. DevLove는 Python 3.9 이상과 GitHub CLI (`gh`)가 필요합니다.

### 1. 의존성 설치

```bash
# GitHub CLI 설치
brew install gh
gh auth login
gh auth refresh -s read:org  # 조직 저장소 스캔 시 필수
```

### 2. Poetry 설치

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 3. 복용

```bash
git clone https://github.com/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code.git
cd Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code
poetry install
```

## 📋 용법 및 용량 (사용법)

```bash
# 오늘 한 일을 확인
poetry run gh-stats --range today

# 이번 달에 일했음을 상사에게 증명
poetry run gh-stats --range thismonth --orgs YOUR_COMPANY_ORG

# AI 요약용 내보내기 - 지난주 모든 커밋 메시지 출력
poetry run gh-stats --range lastweek --export-commits
```

### 파라미터

| 플래그 | 효과 | 기본값 |
| :--- | :--- | :--- |
| `--range` | 날짜 단축어 (`today`, `yesterday`, `lastweek`, `3days` 등) | 없음 |
| `--no-personal` | 개인 저장소 제외 | - |
| `--export-commits` | 커밋 메시지를 Markdown으로 내보내기 | False |
| `--all-branches` | 모든 활성 브랜치 스캔 | False |

## 📄 라이선스

MIT. 원하는 대로 사용하세요. 그저 코드를 쓰세요.
