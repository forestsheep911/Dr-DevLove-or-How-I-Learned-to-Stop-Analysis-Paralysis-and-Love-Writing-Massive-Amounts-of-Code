#!/bin/zsh
#
# gh-stats.sh - GitHub contribution statistics (pure shell version)
# Requires: gh, jq
#
# Usage:
#   ./gh-stats.sh [options]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# Defaults
PERSONAL=true
ORGS=""
SINCE_DATE=""
UNTIL_DATE=""
RANGE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --personal) PERSONAL=true; shift ;;
        --no-personal) PERSONAL=false; shift ;;
        --orgs) ORGS="$2"; shift 2 ;;
        --since) SINCE_DATE="$2"; shift 2 ;;
        --until) UNTIL_DATE="$2"; shift 2 ;;
        --range) RANGE="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: $0 [--personal|--no-personal] [--orgs ORG1,ORG2] [--since DATE] [--until DATE] [--range today|week|month|quarter|year]"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Calculate date range
if [[ -n "$RANGE" ]]; then
    TODAY=$(date +%Y-%m-%d)
    case $RANGE in
        today) SINCE_DATE="$TODAY"; UNTIL_DATE="$TODAY" ;;
        week)
            DOW=$(date +%u)
            SINCE_DATE=$(date -v-$((DOW-1))d +%Y-%m-%d)
            UNTIL_DATE="$TODAY"
            ;;
        month) SINCE_DATE=$(date +%Y-%m-01); UNTIL_DATE="$TODAY" ;;
        quarter)
            MONTH=$(date +%-m)
            QS=$(( ((MONTH - 1) / 3) * 3 + 1 ))
            SINCE_DATE=$(printf "%s-%02d-01" "$(date +%Y)" "$QS")
            UNTIL_DATE="$TODAY"
            ;;
        year) SINCE_DATE=$(date +%Y-01-01); UNTIL_DATE="$TODAY" ;;
        *) echo "Unknown range: $RANGE"; exit 1 ;;
    esac
fi

[[ -z "$SINCE_DATE" ]] && SINCE_DATE=$(date +%Y-%m-%d)
[[ -z "$UNTIL_DATE" ]] && UNTIL_DATE=$(date +%Y-%m-%d)

# Check dependencies
for cmd in gh jq; do
    command -v $cmd &>/dev/null || { echo -e "${RED}Error: '$cmd' not installed.${NC}"; exit 1; }
done

# Header
echo -e "${BOLD}GitHub Contribution Statistics${NC}"
echo "Range: $SINCE_DATE to $UNTIL_DATE"
[[ -n "$ORGS" ]] && echo "Orgs: $ORGS"
echo "Personal: $PERSONAL"
echo ""

# Auth
GH_USER=$(gh api user --jq '.login' 2>/dev/null)
[[ -z "$GH_USER" ]] && { echo -e "${RED}Error: Run 'gh auth login' first.${NC}"; exit 1; }
echo -e "${GREEN}[✔]${NC} Authenticated as: $GH_USER"

# Fetch all events (merge pages)
echo -n "Fetching events..."
EVENTS=$(gh api "users/$GH_USER/events?per_page=100" 2>/dev/null || echo "[]")
for page in 2 3; do
    PAGE=$(gh api "users/$GH_USER/events?per_page=100&page=$page" 2>/dev/null || echo "[]")
    [[ "$PAGE" == "[]" ]] && break
    EVENTS=$(echo "$EVENTS $PAGE" | jq -s 'add')
done
echo -e " ${GREEN}Done${NC}"

# Extract repo+sha pairs
COMMITS=$(echo "$EVENTS" | jq -r --arg since "$SINCE_DATE" --arg until "$UNTIL_DATE" --arg user "$GH_USER" --arg personal "$PERSONAL" --arg orgs "$ORGS" '
    .[] | select(.type == "PushEvent") |
    (.created_at | split("T")[0]) as $date |
    select($date >= $since and $date <= $until) |
    .repo.name as $repo |
    ($repo | split("/")[0]) as $owner |
    (if $personal == "false" and $owner == $user then empty
     elif $orgs != "" and $owner != $user and ([$orgs | split(",")[] | select(. == $owner)] | length == 0) then empty
     else . end) |
    "\($repo) \(.payload.head)"
' 2>/dev/null | sort -u)

COMMIT_COUNT=0
if [[ -n "$COMMITS" ]]; then
    COMMIT_COUNT=$(echo "$COMMITS" | wc -l | tr -d ' ')
fi
echo "Found $COMMIT_COUNT commits"

if [[ "$COMMIT_COUNT" -eq 0 ]]; then
    echo -e "${CYAN}No commits found in the specified range.${NC}"
    exit 0
fi

# Fetch stats and aggregate
echo -n "Fetching stats..."
STATS_RAW=""
while IFS=' ' read -r REPO SHA; do
    [[ -z "$REPO" || -z "$SHA" ]] && continue
    S=$(gh api "repos/$REPO/commits/$SHA" --jq '.stats // {} | "\(.additions // 0) \(.deletions // 0)"' 2>/dev/null || echo "0 0")
    STATS_RAW="$STATS_RAW$REPO $S\n"
done <<< "$COMMITS"
echo -e " ${GREEN}Done${NC}"
echo ""

# Aggregate and print
echo "$STATS_RAW" | awk -v blue="$BLUE" -v cyan="$CYAN" -v green="$GREEN" -v red="$RED" -v bold="$BOLD" -v nc="$NC" -v since="$SINCE_DATE" -v until="$UNTIL_DATE" '
BEGIN {
    # Table header
    printf "%s┌──────────────────────────────┬──────────┬─────────────────────────┐%s\n", blue, nc
    printf "%s│%s %s%-28s%s %s│%s %s%-8s%s %s│%s %s%-23s%s %s│%s\n", blue, nc, bold, "Repository", nc, blue, nc, bold, "Commits", nc, blue, nc, bold, "Changes", nc, blue, nc
    printf "%s├──────────────────────────────┼──────────┼─────────────────────────┤%s\n", blue, nc
}
NF >= 3 {
    repo=$1; added=$2; deleted=$3
    commits[repo]++
    additions[repo] += added
    deletions[repo] += deleted
    total_commits++
    total_added += added
    total_deleted += deleted
}
END {
    for (r in commits) {
        printf "%s│%s %s%-28s%s %s│%s %-8s %s│%s %s+%-10s%s%s-%-10s%s %s│%s\n", blue, nc, cyan, r, nc, blue, nc, commits[r], blue, nc, green, additions[r], nc, red, deletions[r], nc, blue, nc
        repo_count++
    }
    printf "%s└──────────────────────────────┴──────────┴─────────────────────────┘%s\n", blue, nc
    print ""
    printf "%sSummary (%s ~ %s):%s\n", bold, since, until, nc
    printf "  • Active Projects: %s%d%s\n", cyan, repo_count, nc
    printf "  • Total Commits:   %s%d%s\n", cyan, total_commits, nc
    printf "  • Total Growth:    %s+%d%s lines\n", green, total_added, nc
    printf "  • Total Cleaning:  %s-%d%s lines\n", red, total_deleted, nc
}'
