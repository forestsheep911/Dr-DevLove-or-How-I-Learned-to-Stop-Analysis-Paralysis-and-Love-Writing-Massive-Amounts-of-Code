from collections import defaultdict
from .api import get_repo_commits, get_commit_stats
from .ui import Colors, print_progress, print_progress_done

def scan_repositories(repos_to_scan, active_branches_map, username, since_date, until_date, collect_messages=False, exclude_noise=False):
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
            total_commits = len(commits)
            for commit_idx, commit in enumerate(commits, 1):
                print_progress(idx, len(repos_to_scan), repo_full_name, f"fetching stats {commit_idx}/{total_commits}")
                stats[repo_full_name]['commits'] += 1
                added, deleted = get_commit_stats(repo_full_name, commit['sha'], exclude_noise=exclude_noise)
                stats[repo_full_name]['added'] += added
                stats[repo_full_name]['deleted'] += deleted
                
                # Always extract date for Active Days stat
                commit_data = commit.get('commit', {})
                author_date_str = commit_data.get('author', {}).get('date')
                
                if author_date_str:
                    try:
                        dt = datetime.datetime.fromisoformat(author_date_str.replace('Z', '+00:00')).astimezone()
                        date_obj = dt
                    except ValueError:
                        date_obj = datetime.datetime.combine(since_date, datetime.time.min)
                    
                    # Always store date and stats, optionally store message
                    msg_entry = {'date': date_obj, 'added': added, 'deleted': deleted}
                    if collect_messages:
                        message = commit_data.get('message', '')
                        msg_entry['message'] = message
                    
                    stats[repo_full_name]['messages'].append(msg_entry)
    
    print_progress(len(repos_to_scan), len(repos_to_scan), "Complete", "")
    print_progress_done(f"Scanned {len(repos_to_scan)} repos, {repos_with_commits} with commits")
    
    return stats, repos_with_commits

def scan_org_team_stats(repos_to_scan, since_date, until_date, collect_messages=False, exclude_noise=False):
    """
    Scan org repositories and aggregate stats by author.
    
    Returns:
        team_stats: dict {author: {commits, added, deleted, repos: {repo: {...}}, messages: []}}
    """
    from .api import get_repo_all_commits, get_commit_stats
    
    print(f"\n{Colors.BOLD}Scanning {len(repos_to_scan)} repositories for team stats...{Colors.ENDC}\n")
    
    # Structure: {author: {commits, added, deleted, repos: {repo: {commits, added, deleted}}, messages: []}}
    team_stats = defaultdict(lambda: {
        'commits': 0, 'added': 0, 'deleted': 0, 
        'repos': defaultdict(lambda: {'commits': 0, 'added': 0, 'deleted': 0}),
        'messages': []
    })
    repos_with_commits = 0
    
    import datetime
    
    for idx, (repo_full_name, repo_name) in enumerate(repos_to_scan):
        print_progress(idx, len(repos_to_scan), repo_full_name, "checking...")
        
        commits = get_repo_all_commits(repo_full_name, since_date, until_date)
        if commits:
            repos_with_commits += 1
            total_commits = len(commits)
            for commit_idx, commit in enumerate(commits, 1):
                print_progress(idx, len(repos_to_scan), repo_full_name, f"stats {commit_idx}/{total_commits}")
                
                # Get author from commit
                author = commit.get('author', {})
                if author:
                    author_login = author.get('login', 'unknown')
                else:
                    # Fallback to commit author name
                    author_login = commit.get('commit', {}).get('author', {}).get('name', 'unknown')
                
                # Get stats
                added, deleted = get_commit_stats(repo_full_name, commit['sha'], exclude_noise=exclude_noise)
                
                # Update team stats
                team_stats[author_login]['commits'] += 1
                team_stats[author_login]['added'] += added
                team_stats[author_login]['deleted'] += deleted
                team_stats[author_login]['repos'][repo_full_name]['commits'] += 1
                team_stats[author_login]['repos'][repo_full_name]['added'] += added
                team_stats[author_login]['repos'][repo_full_name]['deleted'] += deleted
                
                # Always extract date for Active Days stat
                commit_data = commit.get('commit', {})
                author_date_str = commit_data.get('author', {}).get('date')
                
                if author_date_str:
                    try:
                        dt = datetime.datetime.fromisoformat(author_date_str.replace('Z', '+00:00')).astimezone()
                        date_obj = dt
                    except ValueError:
                        date_obj = datetime.datetime.combine(since_date, datetime.time.min)
                    
                    # Always store date and stats, optionally store message
                    msg_entry = {'date': date_obj, 'repo': repo_full_name, 'added': added, 'deleted': deleted}
                    if collect_messages:
                        message = commit_data.get('message', '')
                        msg_entry['message'] = message
                    
                    team_stats[author_login]['messages'].append(msg_entry)
    
    print_progress(len(repos_to_scan), len(repos_to_scan), "Complete", "")
    print_progress_done(f"Scanned {len(repos_to_scan)} repos, {repos_with_commits} with commits")
    
    return dict(team_stats), repos_with_commits
