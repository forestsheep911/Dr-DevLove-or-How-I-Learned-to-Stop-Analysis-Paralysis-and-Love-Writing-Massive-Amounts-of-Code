#!/usr/bin/env python3
import sys
import argparse
import datetime
import shutil

from .api import get_current_user
from .ui import Colors, print_styled, render_table
from .date_parser import parse_date_range, parse_relative_date
from .discovery import discover_repositories
from .scanner import scan_repositories
from .exporter import generate_markdown, write_export_file

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
    parser.add_argument('--export-commits', action='store_true', help='Export commit messages to a Markdown file')
    args = parser.parse_args()

    # Remove defaults_map and automatic limit logic
    personal_limit = args.personal_limit
    org_limit = args.org_limit

    # Date Logic
    # 1. Start with 'range' preset if exists
    if args.range:
        try:
            since_date, until_date = parse_date_range(args.range)
        except ValueError:
            since_date = datetime.date.today()
            until_date = datetime.date.today()
    else:
        since_date = datetime.date.today()
        until_date = datetime.date.today()

    # 2. Override with explicit flags
    if args.since:
        try:
            since_date = parse_relative_date(args.since)
        except ValueError:
            pass
    if args.until:
        try:
            until_date = parse_relative_date(args.until)
        except ValueError:
            pass

    orgs = [o.strip() for o in args.orgs.split(',') if o.strip()]

    # Check gh
    if shutil.which('gh') is None:
        print_styled("Error: 'gh' CLI not installed.", Colors.RED, True)
        sys.exit(1)

    print_styled("GitHub Contribution Statistics", Colors.HEADER, True)
    print(f"Range: {since_date} to {until_date}")
    if orgs: print(f"Orgs: {', '.join(orgs)}")
    print(f"Personal: {'Yes' if args.personal else 'No'}")
    print()

    # Auth
    print(f"{Colors.CYAN}[...]{Colors.ENDC} Authenticating...", end="", flush=True)
    username = get_current_user()
    if not username:
        print(f"\r{Colors.RED}[✗]{Colors.ENDC} Error: Run 'gh auth login' first.")
        sys.exit(1)
    print(f"\r{Colors.GREEN}[✔]{Colors.ENDC} Authenticated as: {username}")
    
    # 1. Discovery Phase
    repos_to_scan, active_branches_map = discover_repositories(
        username=username,
        since_date=since_date,
        orgs=orgs,
        personal=args.personal
    )

    if not repos_to_scan:
        print_styled("No repositories to scan.", Colors.WARNING)
        return

    # 2. Scanning Phase
    stats, repos_with_commits = scan_repositories(
        repos_to_scan=repos_to_scan,
        active_branches_map=active_branches_map,
        username=username,
        since_date=since_date,
        until_date=until_date,
        collect_messages=args.export_commits
    )

    if args.export_commits and stats:
        print_styled("\nGenerating export file...", Colors.CYAN)
        md_content = generate_markdown(stats, since_date, until_date)
        filename = write_export_file(md_content, since_date, until_date)
        print(f"{Colors.GREEN}[✔]{Colors.ENDC} Exported to: {filename}")

    # 3. Output Phase
    render_table(stats, since_date, until_date)

if __name__ == "__main__":
    main()
