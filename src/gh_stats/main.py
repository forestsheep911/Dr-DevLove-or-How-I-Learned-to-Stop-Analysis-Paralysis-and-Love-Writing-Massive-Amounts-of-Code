#!/usr/bin/env python3
"""
gh-stats - GitHub contribution statistics tool (using Commits API)
Usage:
    gh-stats [options]

Options:
    --personal / --no-personal  Include/exclude personal repos (default: include)
    --orgs ORG1,ORG2           Filter by organizations (comma-separated)
    --since DATE               Start date (YYYY-MM-DD)
    --until DATE               End date (YYYY-MM-DD)
    --range RANGE              Shorthand: today, week, month, quarter, year
"""
import json
import subprocess
import datetime
import sys
import argparse
from collections import defaultdict

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    WARNING = '\033[93m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ENDC = '\033[0m'

def print_styled(text, color=Colors.ENDC, bold=False):
    style = color + (Colors.BOLD if bold else '')
    print(f"{style}{text}{Colors.ENDC}")

def print_progress(current, total, repo_name, status=""):
    bar_width = 20
    filled = int(bar_width * current / total) if total > 0 else 0
    bar = "█" * filled + "░" * (bar_width - filled)
    percent = int(100 * current / total) if total > 0 else 0
    # Truncate repo name if too long
    display_repo = repo_name[:30] + "..." if len(repo_name) > 33 else repo_name
    sys.stdout.write(f"\r{Colors.CYAN}[{bar}]{Colors.ENDC} {percent:3d}% │ {display_repo:<35} {status}\033[K")
    sys.stdout.flush()

def print_progress_done(message="Complete"):
    sys.stdout.write(f"\r{Colors.GREEN}[✔]{Colors.ENDC} {message}\033[K\n")
    sys.stdout.flush()

def run_gh_cmd(args, silent=False):
    try:
        result = subprocess.run(['gh'] + args, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        if not silent and e.returncode != 0:
            pass  # Silently handle auth errors
        return None
    except json.JSONDecodeError:
        return None

def get_current_user():
    data = run_gh_cmd(['api', 'user'])
    return data['login'] if data else None

def get_user_repos(username, limit=None):
    """Get repos the user owns, sorted by last push time."""
    repos = []
    page = 1
    while True:
        data = run_gh_cmd(['api', f'users/{username}/repos?per_page=100&page={page}&type=owner&sort=pushed&direction=desc'], silent=True)
        if not data:
            break
        repos.extend(data)
        if limit and len(repos) >= limit:
            repos = repos[:limit]
            break
        if len(data) < 100:
            break
        page += 1
    return repos

def get_org_repos(org, limit=None):
    """Get repos in an organization, sorted by last push time."""
    repos = []
    page = 1
    while True:
        data = run_gh_cmd(['api', f'orgs/{org}/repos?per_page=100&page={page}&sort=pushed&direction=desc'], silent=True)
        if not data:
            break
        repos.extend(data)
        if limit and len(repos) >= limit:
            repos = repos[:limit]
            break
        if len(data) < 100:
            break
        page += 1
    return repos

def get_repo_commits(repo_full_name, author, since_date, until_date):
    """Get commits by author in a repo within date range."""
    # API expects ISO format with time
    since_iso = f"{since_date}T00:00:00Z"
    until_iso = f"{until_date}T23:59:59Z"
    
    commits = []
    page = 1
    while True:
        data = run_gh_cmd([
            'api', 
            f'repos/{repo_full_name}/commits?author={author}&since={since_iso}&until={until_iso}&per_page=100&page={page}'
        ], silent=True)
        if not data:
            break
        commits.extend(data)
        if len(data) < 100:
            break
        page += 1
    return commits

def get_commit_stats(repo_full_name, sha):
    """Get additions/deletions for a specific commit."""
    data = run_gh_cmd(['api', f'repos/{repo_full_name}/commits/{sha}'], silent=True)
    if data and 'stats' in data:
        return data['stats'].get('additions', 0), data['stats'].get('deletions', 0)
    return 0, 0

def parse_date_range(range_str):
    today = datetime.date.today()
    if range_str == 'today':
        return today, today
    elif range_str == 'week':
        start = today - datetime.timedelta(days=today.weekday())
        return start, today
    elif range_str == 'month':
        return today.replace(day=1), today
    elif range_str == 'quarter':
        quarter_month = ((today.month - 1) // 3) * 3 + 1
        return today.replace(month=quarter_month, day=1), today
    elif range_str == 'year':
        return today.replace(month=1, day=1), today
    else:
        raise ValueError(f"Unknown range: {range_str}")

def main():
    parser = argparse.ArgumentParser(description="GitHub contribution statistics")
    parser.add_argument('--personal', dest='personal', action='store_true', default=True,
                        help='Include personal repos (default)')
    parser.add_argument('--no-personal', dest='personal', action='store_false',
                        help='Exclude personal repos')
    parser.add_argument('--orgs', type=str, default='',
                        help='Comma-separated organization names')
    parser.add_argument('--since', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--until', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--range', type=str, choices=['today', 'week', 'month', 'quarter', 'year'],
                        help='Date range shorthand')
    parser.add_argument('--personal-limit', type=int, default=20,
                        help='Max personal repos to scan (default: 20, 0=unlimited)')
    parser.add_argument('--org-limit', type=int, default=50,
                        help='Max repos per org to scan (default: 50, 0=unlimited)')
    args = parser.parse_args()

    # Determine date range
    if args.range:
        since_date, until_date = parse_date_range(args.range)
    else:
        since_date = datetime.datetime.strptime(args.since, '%Y-%m-%d').date() if args.since else datetime.date.today()
        until_date = datetime.datetime.strptime(args.until, '%Y-%m-%d').date() if args.until else datetime.date.today()

    # Parse orgs
    orgs = [o.strip() for o in args.orgs.split(',') if o.strip()]

    # Check gh
    if subprocess.call(['which', 'gh'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
        print_styled("Error: 'gh' CLI not installed.", Colors.RED, True)
        sys.exit(1)

    print_styled("GitHub Contribution Statistics", Colors.HEADER, True)
    print(f"Range: {since_date} to {until_date}")
    if orgs:
        print(f"Orgs: {', '.join(orgs)}")
    print(f"Personal: {'Yes' if args.personal else 'No'}")
    limits_info = []
    if args.personal and args.personal_limit > 0:
        limits_info.append(f"personal: {args.personal_limit}")
    if orgs and args.org_limit > 0:
        limits_info.append(f"org: {args.org_limit}")
    if limits_info:
        print(f"Limits: {', '.join(limits_info)} repos (sorted by recent activity)")
    print()

    # Auth
    print(f"{Colors.CYAN}[...]{Colors.ENDC} Authenticating...", end="", flush=True)
    username = get_current_user()
    if not username:
        print(f"\r{Colors.RED}[✗]{Colors.ENDC} Error: Run 'gh auth login' first.")
        sys.exit(1)
    print(f"\r{Colors.GREEN}[✔]{Colors.ENDC} Authenticated as: {username}")

    # Collect repos to scan
    repos_to_scan = []
    
    personal_limit = args.personal_limit if args.personal_limit > 0 else None
    org_limit = args.org_limit if args.org_limit > 0 else None
    
    if args.personal:
        print(f"{Colors.CYAN}[...]{Colors.ENDC} Fetching personal repos...", end="", flush=True)
        user_repos = get_user_repos(username, personal_limit)
        repos_to_scan.extend([(r['full_name'], r['name']) for r in user_repos])
        print(f"\r{Colors.GREEN}[✔]{Colors.ENDC} Found {len(user_repos)} personal repos")

    for org in orgs:
        print(f"{Colors.CYAN}[...]{Colors.ENDC} Fetching {org} repos...", end="", flush=True)
        org_repos = get_org_repos(org, org_limit)
        repos_to_scan.extend([(r['full_name'], r['name']) for r in org_repos])
        print(f"\r{Colors.GREEN}[✔]{Colors.ENDC} Found {len(org_repos)} repos in {org}")

    if not repos_to_scan:
        print_styled("No repositories to scan.", Colors.WARNING)
        return

    # Scan repos for commits
    print(f"\n{Colors.BOLD}Scanning {len(repos_to_scan)} repositories...{Colors.ENDC}\n")
    
    stats = defaultdict(lambda: {'commits': 0, 'added': 0, 'deleted': 0})
    repos_with_commits = 0
    
    for idx, (repo_full_name, repo_name) in enumerate(repos_to_scan):
        print_progress(idx, len(repos_to_scan), repo_full_name, "checking...")
        
        commits = get_repo_commits(repo_full_name, username, since_date, until_date)
        
        if commits:
            repos_with_commits += 1
            print_progress(idx, len(repos_to_scan), repo_full_name, f"found {len(commits)} commits")
            
            for commit in commits:
                stats[repo_full_name]['commits'] += 1
                sha = commit['sha']
                added, deleted = get_commit_stats(repo_full_name, sha)
                stats[repo_full_name]['added'] += added
                stats[repo_full_name]['deleted'] += deleted
    
    print_progress(len(repos_to_scan), len(repos_to_scan), "Complete", "")
    print_progress_done(f"Scanned {len(repos_to_scan)} repos, {repos_with_commits} with commits")

    if not stats:
        print_styled("\nNo commits found in the specified range.", Colors.WARNING)
        return

    # Render table
    print("\n")
    max_repo_len = max(len(r) for r in stats.keys())
    col_repo = max(max_repo_len + 2, 17)
    col_commits = 10
    col_changes = 25

    def print_sep(chars):
        print(f"{Colors.BLUE}{chars[0]}{chars[1]*col_repo}{chars[2]}{chars[1]*col_commits}{chars[2]}{chars[1]*col_changes}{chars[3]}{Colors.ENDC}")

    print_sep("┌─┬┐")
    print(f"{Colors.BLUE}│{Colors.ENDC} {Colors.BOLD}{'Repository':<{col_repo-1}}{Colors.ENDC}{Colors.BLUE}│{Colors.ENDC} {Colors.BOLD}{'Commits':<{col_commits-1}}{Colors.ENDC}{Colors.BLUE}│{Colors.ENDC} {Colors.BOLD}{'Changes':<{col_changes-1}}{Colors.ENDC}{Colors.BLUE}│{Colors.ENDC}")
    print_sep("├─┼┤")

    total_commits = total_added = total_deleted = 0
    for repo, data in sorted(stats.items(), key=lambda x: x[1]['commits'], reverse=True):
        total_commits += data['commits']
        total_added += data['added']
        total_deleted += data['deleted']
        changes_str = f"{Colors.GREEN}+{data['added']}{Colors.ENDC} / {Colors.RED}-{data['deleted']}{Colors.ENDC}"
        visible_len = len(f"+{data['added']} / -{data['deleted']}")
        padding = col_changes - 1 - visible_len
        print(f"{Colors.BLUE}│{Colors.ENDC} {Colors.CYAN}{repo:<{col_repo-1}}{Colors.ENDC}{Colors.BLUE}│{Colors.ENDC} {str(data['commits']):<{col_commits-1}}{Colors.BLUE}│{Colors.ENDC} {changes_str}{' '*padding}{Colors.BLUE}│{Colors.ENDC}")

    print_sep("└─┴┘")

    print(f"\n{Colors.BOLD}Summary ({since_date} ~ {until_date}):{Colors.ENDC}")
    print(f"  • Active Projects: {Colors.CYAN}{len(stats)}{Colors.ENDC}")
    print(f"  • Total Commits:   {Colors.CYAN}{total_commits}{Colors.ENDC}")
    print(f"  • Total Growth:    {Colors.GREEN}+{total_added}{Colors.ENDC} lines")
    print(f"  • Total Cleaning:  {Colors.RED}-{total_deleted}{Colors.ENDC} lines")

if __name__ == "__main__":
    main()
