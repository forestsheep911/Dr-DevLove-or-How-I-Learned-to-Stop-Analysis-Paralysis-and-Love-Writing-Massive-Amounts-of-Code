import json
import subprocess

from .noise import is_noise_path

def run_gh_cmd(args, silent=False):
    try:
        result = subprocess.run(['gh'] + args, capture_output=True, encoding='utf-8', check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError:
        return None
    except json.JSONDecodeError:
        return None

def get_current_user():
    data = run_gh_cmd(['api', 'user'])
    return data['login'] if data else None

def get_user_repos(username, limit=None, is_self=True):
    """
    Fetch repositories for a user.
    
    Args:
        username: GitHub username
        limit: Max repos to fetch (None = unlimited)
        is_self: If True, query authenticated user (includes private repos).
                 If False, query other user (public repos only).
    
    Returns:
        List of repository objects
    """
    repos = []
    page = 1
    
    if is_self:
        # Authenticated user: use /user/repos to include private repos
        endpoint = 'user/repos'
        query_params = 'affiliation=owner'
    else:
        # Other user: use /users/{username}/repos (public repos only)
        endpoint = f'users/{username}/repos'
        query_params = 'type=owner'
    
    while True:
        data = run_gh_cmd(['api', f'{endpoint}?per_page=100&page={page}&{query_params}&sort=pushed&direction=desc'], silent=True)
        if not data: break
        repos.extend(data)
        if limit and len(repos) >= limit:
            return repos[:limit]
        if len(data) < 100: break
        page += 1
    return repos

def get_org_repos(org, limit=None):
    repos = []
    page = 1
    while True:
        data = run_gh_cmd(['api', f'orgs/{org}/repos?per_page=100&page={page}&sort=pushed&direction=desc'], silent=True)
        if not data: break
        repos.extend(data)
        if limit and len(repos) >= limit:
            return repos[:limit]
        if len(data) < 100: break
        page += 1
    return repos

import datetime

def get_user_active_branches(username):
    """
    Fetch recent PushEvents to find which branches were active.
    Returns a dict: {repo_full_name: set(branch_names)}
    """
    active_branches = {}
    page = 1
    # Check last 300 events or so (3 pages) to cover 'today' and 'week' activity adequately
    max_pages = 3 
    
    while page <= max_pages:
        data = run_gh_cmd(['api', f'users/{username}/events?per_page=100&page={page}'], silent=True)
        if not data: break
        
        for event in data:
            repo_name = event['repo']['name']
            
            if event['type'] == 'PushEvent':
                # payload.ref looks like 'refs/heads/main' or 'refs/heads/feature-x'
                ref = event['payload'].get('ref', '')
                if ref.startswith('refs/heads/'):
                    branch = ref.replace('refs/heads/', '')
                    if repo_name not in active_branches:
                        active_branches[repo_name] = set()
                    active_branches[repo_name].add(branch)
            
            elif event['type'] == 'CreateEvent':
                # extensive support for new branches
                if event['payload'].get('ref_type') == 'branch':
                    branch = event['payload'].get('ref')
                    if branch:
                        if repo_name not in active_branches:
                            active_branches[repo_name] = set()
                        active_branches[repo_name].add(branch)
        
        if len(data) < 100: break
        page += 1
        
    return active_branches

def get_repo_commits(repo_full_name, author, since_date, until_date, branches=None):
    # Determine local timezone offset
    local_tz = datetime.datetime.now().astimezone().tzinfo
    
    # Create local datetime objects for start and end of day
    since_dt = datetime.datetime.combine(since_date, datetime.time.min, tzinfo=local_tz)
    until_dt = datetime.datetime.combine(until_date, datetime.time.max, tzinfo=local_tz)
    
    # Convert to UTC
    since_utc = since_dt.astimezone(datetime.timezone.utc)
    until_utc = until_dt.astimezone(datetime.timezone.utc)
    
    # Format as API expects (ISO 8601 with Z)
    since_iso = since_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    until_iso = until_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    commits = []
    seen_shas = set()
    
    # If no specific branches provided, default to None (which implies default branch)
    # We always include None to ensure we check the default branch too, 
    # unless specific branches are strictly required. 
    # But usually 'branches' list passed here will be supplementary to default.
    # actually, let's just make target_refs list.
    
    target_refs = set()
    target_refs.add(None) # None means default branch
    if branches:
        target_refs.update(branches)
        
    for ref in target_refs:
        page = 1
        while True:
            cmd = [
                'api', 
                f'repos/{repo_full_name}/commits?author={author}&since={since_iso}&until={until_iso}&per_page=100&page={page}'
            ]
            if ref:
                cmd[-1] += f"&sha={ref}"
                
            data = run_gh_cmd(cmd, silent=True)
            if not data: break
            
            for commit in data:
                sha = commit['sha']
                if sha not in seen_shas:
                    seen_shas.add(sha)
                    commits.append(commit)
            
            if len(data) < 100: break
            page += 1
            
    return commits

def get_repo_all_commits(repo_full_name, since_date, until_date):
    """Get all commits from a repo without filtering by author."""
    local_tz = datetime.datetime.now().astimezone().tzinfo
    
    since_dt = datetime.datetime.combine(since_date, datetime.time.min, tzinfo=local_tz)
    until_dt = datetime.datetime.combine(until_date, datetime.time.max, tzinfo=local_tz)
    
    since_utc = since_dt.astimezone(datetime.timezone.utc)
    until_utc = until_dt.astimezone(datetime.timezone.utc)
    
    since_iso = since_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    until_iso = until_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    commits = []
    page = 1
    while True:
        cmd = [
            'api', 
            f'repos/{repo_full_name}/commits?since={since_iso}&until={until_iso}&per_page=100&page={page}'
        ]
        data = run_gh_cmd(cmd, silent=True)
        if not data: break
        commits.extend(data)
        if len(data) < 100: break
        page += 1
            
    return commits

def get_commit_stats(repo_full_name, sha, exclude_noise=False):
    data = run_gh_cmd(['api', f'repos/{repo_full_name}/commits/{sha}'], silent=True)
    if not data:
        return 0, 0
    if exclude_noise:
        files = data.get('files') or []
        if files:
            added = 0
            deleted = 0
            for file_info in files:
                filename = file_info.get('filename', '')
                if filename and is_noise_path(filename):
                    continue
                added += file_info.get('additions', 0)
                deleted += file_info.get('deletions', 0)
            return added, deleted
    if 'stats' in data:
        return data['stats'].get('additions', 0), data['stats'].get('deletions', 0)
    return 0, 0

def search_user_commits(username, since_date, until_date):
    """
    Use GitHub Search API to find repositories where user has commits.
    This can discover contributions beyond the 90-day Events API limit.
    
    Args:
        username: GitHub username
        since_date: Start date (date object)
        until_date: End date (date object)
    
    Returns:
        Set of unique repository full_names (e.g., {'owner/repo1', 'owner/repo2'})
    
    Note: Search API has stricter rate limits (30 requests/minute).
          Maximum 1000 results can be returned.
    """
    import time
    
    repos_found = set()
    page = 1
    max_pages = 10  # 100 results per page * 10 = 1000 max results
    
    # Format dates for search query: YYYY-MM-DD
    since_str = since_date.strftime('%Y-%m-%d')
    until_str = until_date.strftime('%Y-%m-%d')
    
    # Search query: author:{username} committer-date:{since}..{until}
    query = f'author:{username}+committer-date:{since_str}..{until_str}'
    
    while page <= max_pages:
        # Search API requires special Accept header for commits
        cmd = [
            'api',
            '-H', 'Accept: application/vnd.github.cloak-preview+json',
            f'search/commits?q={query}&per_page=100&page={page}&sort=committer-date&order=desc'
        ]
        
        data = run_gh_cmd(cmd, silent=True)
        
        if not data:
            break
            
        items = data.get('items', [])
        if not items:
            break
            
        for item in items:
            repo = item.get('repository', {})
            full_name = repo.get('full_name')
            if full_name:
                repos_found.add(full_name)
        
        # Check if we've fetched all results
        total_count = data.get('total_count', 0)
        if page * 100 >= total_count or page * 100 >= 1000:
            break
            
        page += 1
        # Small delay to be nice to rate limits
        time.sleep(0.5)
    
    return repos_found

