#!/usr/bin/env python3
import sys
import argparse
import datetime
import shutil

from .api import get_current_user, get_org_repos
from .ui import Colors, print_styled, render_table, generate_ascii_table, generate_markdown_table, generate_team_table, generate_team_markdown_table, print_highlights
from .date_parser import parse_date_range, parse_relative_date
from .discovery import discover_repositories
from .scanner import scan_repositories, scan_org_team_stats
from .exporter import generate_markdown, generate_team_markdown, write_export_file, generate_highlights_markdown
from .highlights import generate_highlights

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
    parser.add_argument('--org-users', action='store_true', help='Compare all contributors in the specified org(s)')
    parser.add_argument('--highlights', action='store_true', help='Show insights like longest streak and most productive day')
    parser.add_argument('--group-by', type=str, choices=['user', 'repo'], default='user', help='Group export by user or repo (for --org-users)')
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
        if orgs:
            print(f"{Colors.CYAN}[INFO]{Colors.ENDC} Analyzing user: {target_user} in orgs: {', '.join(orgs)}")
        else:
            print(f"{Colors.CYAN}[INFO]{Colors.ENDC} Analyzing user: {target_user} (public repos only)")
    
    # Team mode: --org-users
    if args.org_users:
        if not orgs:
            print_styled("Error: --org-users requires --orgs to be specified.", Colors.RED)
            sys.exit(1)
        
        print(f"{Colors.CYAN}[INFO]{Colors.ENDC} Team mode: comparing all contributors in {', '.join(orgs)}")
        
        # Fetch all org repos (no limit prompt for team mode)
        repos_to_scan = []
        print(f"{Colors.CYAN}[...]{Colors.ENDC} Fetching organization repos...", end="", flush=True)
        for org in orgs:
            org_repos = get_org_repos(org, limit=None)
            for r in org_repos:
                repos_to_scan.append((r['full_name'], r['name']))
        print(f"\r{Colors.GREEN}[✔]{Colors.ENDC} Found {len(repos_to_scan)} repos in {', '.join(orgs)}")
        
        if not repos_to_scan:
            print_styled("No repositories found in the specified org(s).", Colors.WARNING)
            return
        
        # Scan for team stats
        team_stats, repos_with_commits = scan_org_team_stats(
            repos_to_scan=repos_to_scan,
            since_date=since_date,
            until_date=until_date,
            collect_messages=(args.export_commits or args.full_message or args.output is not None)
        )
        
        if not team_stats:
            print_styled("No commits found in the specified range.", Colors.WARNING)
            return
        
        # Output
        msg_content = ""
        if args.export_commits or args.full_message:
            msg_content = generate_team_markdown(team_stats, since_date, until_date, 
                                                  group_by=args.group_by, full_message=args.full_message)
        
        if args.output:
            print_styled(f"\nGenerating team report...", Colors.CYAN)
            table_str_file = generate_team_markdown_table(team_stats, since_date, until_date)
            final_content = f"{table_str_file}\n\n{msg_content}"
            filename = write_export_file(final_content, since_date, until_date, args.output)
            print(f"{Colors.GREEN}[✔]{Colors.ENDC} Exported team data to: {filename}")
        else:
            print(generate_team_table(team_stats, since_date, until_date, use_colors=True))
            if msg_content:
                print("\nDetailed Team Report:\n")
                print(msg_content)
        return
    
    # Normal mode (non-team)
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
    highlights = None
    if args.highlights:
        print_styled(f"\nComputing highlights...", Colors.CYAN)
        highlights = generate_highlights(stats)

    msg_content = ""
    # Note: We don't pass highlights here, we handle them separately for flexibility
    if args.export_commits or args.full_message:
        msg_content = generate_markdown(stats, since_date, until_date, full_message=args.full_message)

    if args.output:
        # File Mode: Combine Markdown Table + Highlights + Messages
        print_styled(f"\nGenerating report...", Colors.CYAN)
        table_str_file = generate_markdown_table(stats, since_date, until_date)
        
        parts = [table_str_file]
        
        if highlights:
            hl_str = generate_highlights_markdown(highlights)
            if hl_str:
                parts.append(hl_str)
                
        if msg_content:
            parts.append(msg_content)
        
        final_content = "\n\n".join(parts)
        
        filename = write_export_file(final_content, since_date, until_date, args.output)
        print(f"{Colors.GREEN}[✔]{Colors.ENDC} Exported all data to: {filename}")
    else:
        # Console Mode: Print Table (Color) + Highlights + Messages (if any)
        print(generate_ascii_table(stats, since_date, until_date, use_colors=True))
        
        if highlights:
            print_highlights(highlights)
            
        if msg_content:
            print("\nDetailed Report:\n")
            print(msg_content)

if __name__ == "__main__":
    main()
