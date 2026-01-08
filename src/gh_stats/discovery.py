from datetime import date
from .api import get_user_active_branches, get_user_repos, get_org_repos, search_user_commits
from .ui import Colors

def default_prompt_callback(msg):
    return input(msg)

def discover_repositories(username, since_date, until_date, orgs, personal, is_self=True, prompt_callback=default_prompt_callback):
    """
    Discover repositories based on the hybrid logic:
    1. Always check Events API for recent activity (precision layer).
    2. If date range > 90 days, prompt user for interactive fallback (history layer).
    
    Args:
        username: Target GitHub username to analyze
        since_date: Start date for the range
        until_date: End date for the range
        orgs: List of organization names to include
        personal: Whether to include personal repos
        is_self: True if username is the authenticated user (can see private repos),
                 False if querying another user (public repos only)
        prompt_callback: Callback for user prompts
    
    Returns:
        repos_to_scan: List of tuples (full_name, name)
        active_branches_map: Dict of {repo_full_name: set(branches)}
    """
    
    repos_to_scan_set = set() # (full_name, name) tuples
    active_branches_map = {} 
    
    # When querying other users without orgs, we only see their personal public repos
    if not is_self and not orgs:
        if not personal:
            print(f"{Colors.WARNING}[WARN]{Colors.ENDC} --no-personal with --user (no orgs) makes no sense. Enabling personal repos.")
            personal = True
    
    # 1. ALWAYS run Events API (Precision Layer)
    print(f"{Colors.CYAN}[...]{Colors.ENDC} Analyzing recent activity (Events API)...", end="", flush=True)
    active_branches_map = get_user_active_branches(username) # {repo: branches}
    print(f"\r{Colors.GREEN}[✔]{Colors.ENDC} Found recent activity in {len(active_branches_map)} repos")
    
    for full_name in active_branches_map.keys():
        owner, name = full_name.split('/', 1) if '/' in full_name else (username, full_name)
        
        if not is_self and not orgs:
            # When querying OTHER users without org filter: include ALL repos from Events API
            repos_to_scan_set.add((full_name, name))
        else:
            # Apply filtering logic (for self, or for other user with org filter)
            is_personal_match = personal and (owner == username)
            is_org_match = owner in orgs
            
            if is_personal_match or is_org_match:
                 repos_to_scan_set.add((full_name, name))
    
    # 2. When viewing other user with org filter, also fetch org repos
    # Events API can't see their activity in private org repos
    if not is_self and orgs:
        print(f"{Colors.CYAN}[...]{Colors.ENDC} Fetching organization repos...", end="", flush=True)
        org_repo_count = 0
        for org in orgs:
            org_repos = get_org_repos(org, limit=None)
            for r in org_repos:
                repos_to_scan_set.add((r['full_name'], r['name']))
                org_repo_count += 1
        print(f"\r{Colors.GREEN}[✔]{Colors.ENDC} Added {org_repo_count} repos from {', '.join(orgs)}")

    # 2. Check Range for Fallback (Full History Layer)
    days_ago = (date.today() - since_date).days
    
    if days_ago > 90:
        print(f"\n{Colors.WARNING}[WARN]{Colors.ENDC} Time range > 90 days. Events API covers recent 90 days.")
        print(f"To ensure coverage for older activity (>90 days ago), we can fallback to scanning repo lists.")
        
        choice = prompt_callback(f"{Colors.BOLD}Scan older repos? [a]ll, [number], [d]eepsearch, or [Enter] to skip: {Colors.ENDC}").strip().lower()
        
        limit = None
        should_fetch = False
        use_deepsearch = False
        
        if choice == 'a' or choice == 'all':
            limit = None
            should_fetch = True
            print(f" -> Scanning ALL remaining repositories.")
        elif choice == 'd' or choice == 'deepsearch':
            use_deepsearch = True
            print(f"\n{Colors.WARNING}[RATE LIMIT WARNING]{Colors.ENDC}")
            print(f"  Deep search uses GitHub Search API which has stricter rate limits:")
            print(f"  - 30 requests/minute (vs 5000/hour for regular API)")
            print(f"  - Maximum 1000 commits can be discovered")
            print(f"  This may take a while for active users.\n")
            print(f"{Colors.CYAN}[...]{Colors.ENDC} Searching commits via Search API...", end="", flush=True)
            
            found_repos = search_user_commits(username, since_date, until_date)
            
            # Apply same filtering logic as Events API results
            filtered_count = 0
            for full_name in found_repos:
                owner, name = full_name.split('/', 1) if '/' in full_name else (username, full_name)
                
                if not is_self and not orgs:
                    # When querying OTHER users without org filter: include all repos
                    repos_to_scan_set.add((full_name, name))
                    filtered_count += 1
                else:
                    # Apply filtering logic (for self, or for other user with org filter)
                    is_personal_match = personal and (owner == username)
                    is_org_match = owner in orgs
                    
                    if is_personal_match or is_org_match:
                        repos_to_scan_set.add((full_name, name))
                        filtered_count += 1
            
            print(f"\r{Colors.GREEN}[✔]{Colors.ENDC} Deep search found {len(found_repos)} repos, {filtered_count} matched filters")
        elif choice.isdigit():
            limit = int(choice)
            should_fetch = True
            print(f" -> Scanning top {limit} remaining repositories.")
        else:
            print(f" -> Skipping fallback scan. Only checking {len(repos_to_scan_set)} active repos.")
        
        if should_fetch and not use_deepsearch:
            # Fetch Personal repos
            if personal:
                print(f"{Colors.CYAN}[...]{Colors.ENDC} Fetching personal repos...", end="", flush=True)
                user_repos = get_user_repos(username, limit, is_self=is_self)
                for r in user_repos:
                    repos_to_scan_set.add((r['full_name'], r['name']))
                visibility_hint = "" if is_self else " (public only)"
                print(f"\r{Colors.GREEN}[✔]{Colors.ENDC} Found {len(user_repos)} personal repos{visibility_hint}")

            # Fetch Org repos (only when querying self)
            for org in orgs:
                print(f"{Colors.CYAN}[...]{Colors.ENDC} Fetching {org} repos...", end="", flush=True)
                org_repos = get_org_repos(org, limit)
                for r in org_repos:
                    repos_to_scan_set.add((r['full_name'], r['name']))
                print(f"\r{Colors.GREEN}[✔]{Colors.ENDC} Found {len(org_repos)} repos in {org}")
                
    else:
        print(f"{Colors.CYAN}[INFO]{Colors.ENDC} Range within 90 days. Events API coverage is sufficient.")

    return list(repos_to_scan_set), active_branches_map


