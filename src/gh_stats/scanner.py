from collections import defaultdict
from .api import get_repo_commits, get_commit_stats
from .ui import Colors, print_progress, print_progress_done

def scan_repositories(repos_to_scan, active_branches_map, username, since_date, until_date, collect_messages=False):
    """
    Scan the provided repositories for commits and statistics.
    
    Args:
        repos_to_scan: List of tuples (repo_full_name, repo_name)
        active_branches_map: Dict of {repo_full_name: set(branches)}
        username: GitHub username
        since_date: Start date
        until_date: End date
        collect_messages: If True, detailed commit messages are collected
        
    Returns:
        stats: defaultdict containing commit counts, line changes, and optionally messages
        repos_with_commits: Count of repos found to have relevant commits
    """
    print(f"\n{Colors.BOLD}Scanning {len(repos_to_scan)} repositories...{Colors.ENDC}\n")
    # stats dict structure: {'commits': int, 'added': int, 'deleted': int, 'messages': list}
    stats = defaultdict(lambda: {'commits': 0, 'added': 0, 'deleted': 0, 'messages': []})
    repos_with_commits = 0
    
    import datetime
    
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
                
                if collect_messages:
                    # Extract date and message
                    # date format from API: "2023-12-30T12:00:00Z"
                    commit_data = commit.get('commit', {})
                    author_date_str = commit_data.get('author', {}).get('date')
                    message = commit_data.get('message', '')
                    
                    if author_date_str:
                        # Simple parsing, assuming UTC 'Z' or simple ISO
                        # To keep it robust but simple, let's just use first 10 chars YYYY-MM-DD
                        # Ideally use datetime.fromisoformat replacing Z
                        try:
                            # python 3.11+ handles Z, earlier needs replace
                            dt = datetime.datetime.fromisoformat(author_date_str.replace('Z', '+00:00'))
                            date_obj = dt.date()
                        except ValueError:
                            date_obj = since_date # Fallback if parsing fails?
                            
                        stats[repo_full_name]['messages'].append({
                            'date': date_obj,
                            'message': message
                        })
    
    print_progress(len(repos_to_scan), len(repos_to_scan), "Complete", "")
    print_progress_done(f"Scanned {len(repos_to_scan)} repos, {repos_with_commits} with commits")
    
    return stats, repos_with_commits
