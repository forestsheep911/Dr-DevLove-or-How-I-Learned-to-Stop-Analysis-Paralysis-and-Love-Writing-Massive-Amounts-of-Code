"""
Portrait module: Aggregates Team and Repo portraits.
"""
from collections import defaultdict
import datetime

def generate_team_portrait(team_stats):
    """
    Analyze team working habits.
    
    Returns:
    {
        'weekday_stats': {0: count, 1: count...},
        'hour_stats': {0: count... 23: count},
        'avg_lines_per_commit': float
    }
    """
    weekday_stats = defaultdict(int)
    hour_stats = defaultdict(int)
    total_commits = 0
    total_changes = 0
    
    for user_data in team_stats.values():
        commits = user_data['commits']
        added = user_data['added']
        deleted = user_data['deleted']
        
        total_commits += commits
        total_changes += (added + deleted)
        
        for msg in user_data.get('messages', []):
            if 'date' in msg and isinstance(msg['date'], datetime.datetime):
                dt = msg['date']
                # Convert UTC to local timezone
                if dt.tzinfo is not None:
                    dt = dt.astimezone()  # Converts to system local timezone
                weekday_stats[dt.weekday()] += 1
                hour_stats[dt.hour] += 1
                
    avg_lines = (total_changes / total_commits) if total_commits > 0 else 0
    
    return {
        'weekday_stats': dict(weekday_stats),
        'hour_stats': dict(hour_stats),
        'avg_lines_per_commit': avg_lines
    }


def generate_repo_portrait(team_stats, all_repos_count):
    """
    Analyze repository traits.
    
    Returns:
    {
        'net_growth_champion': (repo, net_growth),
        'refactor_champion': (repo, total_changes),
        'slimming_champion': (repo, net_growth), # Most negative
        'idle_repos_count': int
    }
    """
    # Aggregate by repo
    repo_stats = {} # repo -> {net, total}
    
    for user_data in team_stats.values():
        repos = user_data.get('repos', {})
        for repo_name, stats in repos.items():
            if repo_name not in repo_stats:
                repo_stats[repo_name] = {'net': 0, 'total': 0}
            
            repo_stats[repo_name]['net'] += (stats['added'] - stats['deleted'])
            repo_stats[repo_name]['total'] += (stats['added'] + stats['deleted'])
            
    active_repos_count = len(repo_stats)
    idle_repos_count = max(0, all_repos_count - active_repos_count)
    
    # Champions
    sorted_by_net = sorted(repo_stats.items(), key=lambda x: x[1]['net'], reverse=True)
    sorted_by_total = sorted(repo_stats.items(), key=lambda x: x[1]['total'], reverse=True)
    
    net_growth_champion = (None, 0)
    if sorted_by_net:
        top = sorted_by_net[0]
        net_growth_champion = (top[0], top[1]['net'])
        
    refactor_champion = (None, 0)
    if sorted_by_total:
        top = sorted_by_total[0]
        refactor_champion = (top[0], top[1]['total'])
        
    slimming_champion = (None, 0)
    if sorted_by_net:
        bottom = sorted_by_net[-1]
        if bottom[1]['net'] < 0:
            slimming_champion = (bottom[0], bottom[1]['net'])
            
    return {
        'net_growth_champion': net_growth_champion,
        'refactor_champion': refactor_champion,
        'slimming_champion': slimming_champion,
        'idle_repos_count': idle_repos_count
    }
