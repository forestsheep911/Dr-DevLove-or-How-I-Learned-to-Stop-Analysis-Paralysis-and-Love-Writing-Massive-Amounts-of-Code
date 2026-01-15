#!/usr/bin/env python3
import sys
import argparse
import datetime
import os
import shutil

from .api import get_current_user, get_org_repos
from .ui import Colors, print_styled, render_table, generate_ascii_table, generate_markdown_table, generate_team_table, generate_team_markdown_table, print_highlights
from .date_parser import parse_date_range, parse_relative_date
from .discovery import discover_repositories
from .scanner import scan_repositories, scan_org_team_stats
from .exporter import generate_markdown, generate_team_markdown, write_export_file, generate_highlights_markdown, DEFAULT_EXPORT_DIR
from .highlights import generate_highlights
from .args import create_parser, parse_with_diagnostics, format_diagnostics

def main():
    # Force UTF-8 stdout for emoji support on Windows
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

    parser = create_parser()
    args = parser.parse_args()

    # Dev mode: extensive diagnostics before execution
    if args.dev:
        print_styled("=== DEVELOPMENT MODE ===", Colors.HEADER, True)
        # Quote arguments if they contain spaces to make the command valid for copy-pasting
        quoted_argv = [f'"{arg}"' if ' ' in arg else arg for arg in sys.argv]
        print(f"Command: {' '.join(quoted_argv)}\n")
        
        _, diag_result = parse_with_diagnostics()
        print(format_diagnostics(diag_result))
        
        if not diag_result.is_valid:
            print_styled("[X] Stopping execution due to configuration errors.", Colors.RED)
            return

        print_styled("[OK] Configuration valid. Proceeding with execution...", Colors.GREEN)
        print("="*40 + "\n")

    # Dry-run mode: show diagnostics and exit
    if args.dry_run:
        _, diag_result = parse_with_diagnostics()
        output = format_diagnostics(diag_result)
        if args.output:
            import datetime as dt
            output_name = args.output
            if not output_name.endswith('.txt') and not output_name.endswith('.md'):
                output_name += '.txt'
            dir_part = os.path.dirname(output_name)
            file_part = os.path.basename(output_name)
            target_dir = dir_part if dir_part else DEFAULT_EXPORT_DIR
            if target_dir and not os.path.exists(target_dir):
                os.makedirs(target_dir)
            filename = os.path.join(target_dir, file_part) if target_dir else file_part
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# Dry Run Diagnostics\n")
                f.write(f"# Generated: {dt.datetime.now().isoformat()}\n\n")
                f.write(output)
            print(f"{Colors.GREEN}[OK]{Colors.ENDC} Dry-run diagnostics saved to: {filename}")
        else:
            print(output)
        return

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
    
    # --arena-top implies --arena
    if args.arena_top != 5:  # User explicitly set arena-top
        args.arena = True
    
    # Check --arena requires --org-summary
    if args.arena and not args.org_summary:
        print_styled("Error: --arena requires --org-summary to be specified.", Colors.RED)
        sys.exit(1)

    print_styled("GitHub Contribution Statistics", Colors.HEADER, True)
    print(f"Range: {since_date} to {until_date}")
    if orgs: print(f"Orgs: {', '.join(orgs)}")
    print(f"Personal: {'Yes' if args.personal else 'No'}")
    print(f"Exclude Noise: {'Yes' if args.exclude_noise else 'No'}")
    print()

    # Auth
    print(f"{Colors.CYAN}[...]{Colors.ENDC} Authenticating...", end="", flush=True)
    authenticated_user = get_current_user()
    if not authenticated_user:
        print(f"\r{Colors.RED}[X]{Colors.ENDC} Error: Run 'gh auth login' first.")
        sys.exit(1)
    print(f"\r{Colors.GREEN}[OK]{Colors.ENDC} Authenticated as: {authenticated_user}")
    
    # Determine target user
    target_user = args.user if args.user else authenticated_user
    is_self = (target_user == authenticated_user)
    
    if not is_self:
        if orgs:
            print(f"{Colors.CYAN}[INFO]{Colors.ENDC} Analyzing user: {target_user} in orgs: {', '.join(orgs)}")
        else:
            print(f"{Colors.CYAN}[INFO]{Colors.ENDC} Analyzing user: {target_user} (public repos only)")
    
    # Org Summary mode: --org-summary
    if args.org_summary:
        # Mutual exclusion check
        if orgs:
            print_styled("Error: --org-summary and --orgs are mutually exclusive.", Colors.RED)
            sys.exit(1)
        
        # --arena requires --org-summary (already checked by being inside this block)
        org = args.org_summary
        
        print(f"{Colors.CYAN}[INFO]{Colors.ENDC} Org Summary mode: analyzing organization '{org}'")
        
        # Fetch all org repos
        repos_to_scan = []
        print(f"{Colors.CYAN}[...]{Colors.ENDC} Fetching organization repos...", end="", flush=True)
        org_repos = get_org_repos(org, limit=None)
        for r in org_repos:
            repos_to_scan.append((r['full_name'], r['name']))
        print(f"\r{Colors.GREEN}[OK]{Colors.ENDC} Found {len(repos_to_scan)} repos in {org}")
        
        if not repos_to_scan:
            print_styled("No repositories found in the specified org.", Colors.WARNING)
            return
        
        # Scan for team stats
        team_stats, repos_with_commits = scan_org_team_stats(
            repos_to_scan=repos_to_scan,
            since_date=since_date,
            until_date=until_date,
            collect_messages=(args.export_commits or args.full_message or args.output is not None),
            exclude_noise=args.exclude_noise
        )
        
        if not team_stats:
            print_styled("No commits found in the specified range.", Colors.WARNING)
            return
        
        # Output - use new format functions
        from .ui import generate_org_summary_output, generate_org_summary_markdown
        
        arena_top = args.arena_top if args.arena_top > 0 else None  # None means all
        
        if args.output:
            print_styled(f"\nGenerating org summary report...", Colors.CYAN)
            content = generate_org_summary_markdown(team_stats, since_date, until_date, org, args.arena, arena_top)
            filename = write_export_file(content, since_date, until_date, args.output)
            print(f"{Colors.GREEN}[OK]{Colors.ENDC} Exported org summary to: {filename}")
        else:
            print(generate_org_summary_output(team_stats, since_date, until_date, org, args.arena, arena_top, use_colors=True))
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
        collect_messages=(args.export_commits or args.full_message or args.output is not None),
        exclude_noise=args.exclude_noise
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
        print(f"{Colors.GREEN}[OK]{Colors.ENDC} Exported all data to: {filename}")
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
