#!/usr/bin/env python3
import sys
import argparse
import datetime
import shutil

from .api import get_current_user
from .ui import Colors, print_styled, render_table, generate_ascii_table, generate_markdown_table
from .date_parser import parse_date_range, parse_relative_date
from .discovery import discover_repositories
from .scanner import scan_repositories
from .exporter import generate_markdown, write_export_file

def main():
    parser = argparse.ArgumentParser(description="GitHub contribution statistics")
    parser.add_argument('--user', type=str, help='Target GitHub username (defaults to authenticated user)')
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
    parser.add_argument('--full-message', action='store_true', help='Include full commit message body in export')
    parser.add_argument('--output', '-o', type=str, help='Specify output filename for export')
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
    authenticated_user = get_current_user()
    if not authenticated_user:
        print(f"\r{Colors.RED}[✗]{Colors.ENDC} Error: Run 'gh auth login' first.")
        sys.exit(1)
    print(f"\r{Colors.GREEN}[✔]{Colors.ENDC} Authenticated as: {authenticated_user}")
    
    # Determine target user
    target_user = args.user if args.user else authenticated_user
    is_self = (target_user == authenticated_user)
    
    if not is_self:
        print(f"{Colors.CYAN}[INFO]{Colors.ENDC} Analyzing user: {target_user} (public repos only)")
        if orgs:
            print(f"{Colors.WARNING}[WARN]{Colors.ENDC} --orgs is ignored when using --user (can only see target's personal public repos)")
    
    # 1. Discovery Phase
    repos_to_scan, active_branches_map = discover_repositories(
        username=target_user,
        since_date=since_date,
        until_date=until_date,
        orgs=orgs,
        personal=args.personal,
        is_self=is_self
    )

    if not repos_to_scan:
        print_styled("No repositories to scan.", Colors.WARNING)
        return

    # 2. Scanning Phase
    stats, repos_with_commits = scan_repositories(
        repos_to_scan=repos_to_scan,
        active_branches_map=active_branches_map,
        username=target_user,
        since_date=since_date,
        until_date=until_date,
        collect_messages=(args.export_commits or args.full_message or args.output is not None)
    )

    # 3. Output Phase
    msg_content = ""
    if args.export_commits or args.full_message:
        msg_content = generate_markdown(stats, since_date, until_date, full_message=args.full_message)

    if args.output:
        # File Mode: Combine Markdown Table + Messages
        print_styled(f"\nGenerating report...", Colors.CYAN)
        table_str_file = generate_markdown_table(stats, since_date, until_date)
        
        # Combine: Markdown table first, then commit details
        final_content = f"{table_str_file}\n\n{msg_content}"
        
        filename = write_export_file(final_content, since_date, until_date, args.output)
        print(f"{Colors.GREEN}[✔]{Colors.ENDC} Exported all data to: {filename}")
    else:
        # Console Mode: Print Table (Color) + Messages (if any)
        print(generate_ascii_table(stats, since_date, until_date, use_colors=True))
        if msg_content:
            print("\nDetailed Report:\n")
            print(msg_content)

if __name__ == "__main__":
    main()
