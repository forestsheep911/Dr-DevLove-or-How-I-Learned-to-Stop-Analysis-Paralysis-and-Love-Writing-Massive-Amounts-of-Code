#!/usr/bin/env python3
import sys
import argparse
import datetime
import subprocess
from collections import defaultdict

from .api import get_current_user, get_user_repos, get_org_repos, get_repo_commits, get_commit_stats
from .ui import Colors, print_styled, print_progress, print_progress_done, render_table
from .utils import parse_date_range

def main():
    parser = argparse.ArgumentParser(description="GitHub contribution statistics")
    parser.add_argument('--personal', dest='personal', action='store_true', default=True, help='Include personal repos (default)')
    parser.add_argument('--no-personal', dest='personal', action='store_false', help='Exclude personal repos')
    parser.add_argument('--orgs', type=str, default='', help='Comma-separated organization names')
    parser.add_argument('--since', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--until', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--range', type=str, choices=['today', 'week', 'month', 'quarter', 'year'], help='Date range shorthand')
    parser.add_argument('--personal-limit', type=int, help='Max personal repos to scan (0=unlimited)')
    parser.add_argument('--org-limit', type=int, help='Max repos per org to scan (0=unlimited)')
    args = parser.parse_args()

    # Dynamic defaults for limits based on range
    # Format: (personal_limit, org_limit)
    defaults = {
        'today': (4, 8),
        'week': (8, 16),
        'month': (20, 50),
        'quarter': (30, 80),
        'year': (50, 100)
    }
    
    # Default to 'today' settings if no range specified or custom date range used
    default_personal, default_org = defaults.get(args.range, (20, 50))
    
    personal_limit = args.personal_limit if args.personal_limit is not None else default_personal
    org_limit = args.org_limit if args.org_limit is not None else default_org

    # Dates
    if args.range:
        since_date, until_date = parse_date_range(args.range)
    else:
        since_date = datetime.datetime.strptime(args.since, '%Y-%m-%d').date() if args.since else datetime.date.today()
        until_date = datetime.datetime.strptime(args.until, '%Y-%m-%d').date() if args.until else datetime.date.today()

    orgs = [o.strip() for o in args.orgs.split(',') if o.strip()]

    # Check gh
    if subprocess.call(['which', 'gh'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
        print_styled("Error: 'gh' CLI not installed.", Colors.RED, True)
        sys.exit(1)

    print_styled("GitHub Contribution Statistics", Colors.HEADER, True)
    print(f"Range: {since_date} to {until_date}")
    if orgs: print(f"Orgs: {', '.join(orgs)}")
    print(f"Personal: {'Yes' if args.personal else 'No'}")
    
    limits_info = []
    if args.personal and personal_limit > 0: limits_info.append(f"personal: {personal_limit}")
    else: limits_info.append("personal: unlimited")
    
    if orgs and org_limit > 0: limits_info.append(f"org: {org_limit}")
    elif orgs: limits_info.append("org: unlimited")
    
    if limits_info: print(f"Limits: {', '.join(limits_info)}")
    print()

    # Auth
    print(f"{Colors.CYAN}[...]{Colors.ENDC} Authenticating...", end="", flush=True)
    username = get_current_user()
    if not username:
        print(f"\r{Colors.RED}[✗]{Colors.ENDC} Error: Run 'gh auth login' first.")
        sys.exit(1)
    print(f"\r{Colors.GREEN}[✔]{Colors.ENDC} Authenticated as: {username}")

    # Repos
    repos_to_scan = []
    if args.personal:
        print(f"{Colors.CYAN}[...]{Colors.ENDC} Fetching personal repos...", end="", flush=True)
        user_repos = get_user_repos(username, personal_limit if personal_limit > 0 else None)
        repos_to_scan.extend([(r['full_name'], r['name']) for r in user_repos])
        print(f"\r{Colors.GREEN}[✔]{Colors.ENDC} Found {len(user_repos)} personal repos")

    for org in orgs:
        print(f"{Colors.CYAN}[...]{Colors.ENDC} Fetching {org} repos...", end="", flush=True)
        org_repos = get_org_repos(org, org_limit if org_limit > 0 else None)
        repos_to_scan.extend([(r['full_name'], r['name']) for r in org_repos])
        print(f"\r{Colors.GREEN}[✔]{Colors.ENDC} Found {len(org_repos)} repos in {org}")

    if not repos_to_scan:
        print_styled("No repositories to scan.", Colors.WARNING)
        return

    # Scanning
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
                added, deleted = get_commit_stats(repo_full_name, commit['sha'])
                stats[repo_full_name]['added'] += added
                stats[repo_full_name]['deleted'] += deleted
    
    print_progress(len(repos_to_scan), len(repos_to_scan), "Complete", "")
    print_progress_done(f"Scanned {len(repos_to_scan)} repos, {repos_with_commits} with commits")

    # Output
    render_table(stats, since_date, until_date)

if __name__ == "__main__":
    main()
