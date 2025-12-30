#!/usr/bin/env python3
import sys
import argparse
import datetime
import subprocess
from collections import defaultdict

from .api import get_current_user, get_user_repos, get_org_repos, get_repo_commits, get_commit_stats, get_user_active_branches
from .ui import Colors, print_styled, print_progress, print_progress_done, render_table
from .utils import parse_date_range, parse_relative_date

def main():
    parser = argparse.ArgumentParser(description="GitHub contribution statistics")
    parser.add_argument('--personal', dest='personal', action='store_true', default=True, help='Include personal repos (default)')
    parser.add_argument('--no-personal', dest='personal', action='store_false', help='Exclude personal repos')
    parser.add_argument('--orgs', type=str, default='', help='Comma-separated organization names')
    
    # Date selection (yt-dlp style aliases)
    parser.add_argument('--since', '--date-after', dest='since', type=str, help='Start date (YYYY-MM-DD, YYYYMMDD, or relative like "today-1week")')
    parser.add_argument('--until', '--date-before', dest='until', type=str, help='End date (YYYY-MM-DD, YYYYMMDD, or relative like "today")')
    
    # choices removed to allow flexible formats like '3days', 'today-1week'
    parser.add_argument('--range', type=str, help='Date range preset (e.g., today, week, 3days)')
    parser.add_argument('--personal-limit', type=int, help='Max personal repos to scan (0=unlimited)')
    parser.add_argument('--org-limit', type=int, help='Max repos per org to scan (0=unlimited)')
    parser.add_argument('--all-branches', action='store_true', help='Scan all active branches (found via Events API) instead of just default branch')
    args = parser.parse_args()

    # Dynamic defaults for limits based on range
    # Format: (personal_limit, org_limit)
    defaults_map = {
        'today': (4, 8),
        'yesterday': (4, 8),
        'thisweek': (8, 16),
        'week': (8, 16),
        'lastweek': (8, 16),
        'thismonth': (20, 50),
        'month': (20, 50),
        'lastmonth': (20, 50),
        'quarter': (30, 80),
        'thisyear': (50, 100),
        'year': (50, 100),
        'lastyear': (50, 100)
    }
    
    # Determine defaults. If range is custom (e.g. '3days'), try to map to closest or default to week-ish?
    # Actually, let's keep it simple: if known key use it, else default (20, 50).
    default_key = args.range if args.range in defaults_map else 'default'
    default_personal, default_org = defaults_map.get(default_key, (20, 50))
    
    personal_limit = args.personal_limit if args.personal_limit is not None else default_personal
    org_limit = args.org_limit if args.org_limit is not None else default_org

    # Date Logic
    # 1. Start with 'range' preset if exists
    if args.range:
        try:
            since_date, until_date = parse_date_range(args.range)
        except ValueError:
            # If range is not a known keyword but parseable as relative date, parse_date_range handles it
            # If it fails, we default to today
             since_date = datetime.date.today()
             until_date = datetime.date.today()
    else:
        # Default to today if nothing specified
        since_date = datetime.date.today()
        until_date = datetime.date.today()

    # 2. Override with explicit flags (date-after / date-before)
    if args.since:
        try:
            since_date = parse_relative_date(args.since)
        except ValueError:
            pass # Or exit? parse_relative_date raises error usually.
            
    if args.until:
        try:
            until_date = parse_relative_date(args.until)
        except ValueError:
            pass 
            
    # If no range AND no specific dates provided? Logic above sets default to today.
    # But if user provides ONLY --until, since_date remains today? 
    # Usually if only Until is provided, Since implies "beginning of time"? Or "today"?
    # For daily stats, defaulting "Since" to "Today" is risky if "Until" is "Yesterday".
    # Case: --date-before yesterday. Since=Today, Until=Yesterday. -> Empty range.
    # Adjust: If only Until provided, maybe Since should be unlimited? 
    # But this tool is for "stats", usually implies a window.
    # Let's keep it explicit. If you say --date-before yesterday, you likely want --range week --date-before yesterday?
    # Or just let user enable Since.
    # However, if 'range' wasn't provided, Since/Until defaulted to Today/Today.
    # If I set Until=Yesterday, Since is still Today. Range is inverted.
    # Fix: If Start > End, swap them? Or error?
    if since_date > until_date and not (args.range and not args.since):
         # If purely inferred, maybe we shouldn't error but warn. 
         # But if user said --since tomorrow, that's weird.
         pass

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
    
    # Active branches detection (for recent activity)
    active_branches_map = {}
    if args.all_branches and (args.range in ['today', 'yesterday', 'thisweek', 'week'] or (args.range is None and not args.since)):
        print(f"{Colors.CYAN}[...]{Colors.ENDC} Analyzing recent activity (Events API)...", end="", flush=True)
        active_branches_map = get_user_active_branches(username)
        print(f"\r{Colors.GREEN}[✔]{Colors.ENDC} Analyzed activity across {len(active_branches_map)} repos")

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
        
        # Determine strict branches to check if we have data
        target_branches = active_branches_map.get(repo_full_name) # Returns Set or None
        
        commits = get_repo_commits(repo_full_name, username, since_date, until_date, target_branches)
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
