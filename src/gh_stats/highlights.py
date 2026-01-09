from datetime import timedelta
import calendar
from collections import defaultdict

def generate_highlights(stats):
    """
    Generate highlights statistics from the collected data.
    
    Args:
        stats: Dictionary of repo stats (same format as scan_repositories output)
               {repo: {commits, added, deleted, messages: [{date, ...}]}}
               
    Returns:
        dict: A dictionary containing highlight metrics.
    """
    highlights = {}
    
    # Flatten all commit dates
    all_dates = []
    repo_commits = {}
    
    for repo, data in stats.items():
        repo_commits[repo] = data['commits']
        for msg in data.get('messages', []):
            if 'date' in msg and msg['date']:
                all_dates.append({
                    'date': msg['date'].date(),
                    'repo': repo,
                    'datetime': msg['date']
                })
                
    if not all_dates:
        return None

    # Sort dates
    all_dates.sort(key=lambda x: x['date'])
    unique_dates = sorted(list(set(d['date'] for d in all_dates)))
    
    # 1. Longest Streak
    longest_streak = 0
    current_streak = 0
    streak_end_date = None
    streak_start_date = None
    
    temp_streak = 0
    temp_start = None
    
    if unique_dates:
        temp_streak = 1
        temp_start = unique_dates[0]
        max_streak_start = temp_start
        max_streak_end = temp_start
        max_streak = 1
        
        for i in range(1, len(unique_dates)):
            delta = (unique_dates[i] - unique_dates[i-1]).days
            if delta == 1:
                temp_streak += 1
            else:
                if temp_streak > max_streak:
                    max_streak = temp_streak
                    max_streak_start = temp_start
                    max_streak_end = unique_dates[i-1]
                temp_streak = 1
                temp_start = unique_dates[i]
        
        # Check last streak
        if temp_streak > max_streak:
            max_streak = temp_streak
            max_streak_start = temp_start
            max_streak_end = unique_dates[-1]
            
        longest_streak = max_streak
        highlights['streak'] = {
            'days': longest_streak,
            'start': max_streak_start,
            'end': max_streak_end
        }

    # 2. Most Productive Day
    day_counts = defaultdict(int)
    for d in all_dates:
        day_counts[d['date']] += 1
        
    if day_counts:
        best_day = max(day_counts.items(), key=lambda x: x[1])
        highlights['best_day'] = {
            'date': best_day[0],
            'commits': best_day[1]
        }

    # 3. Favorite Weekday
    weekday_counts = defaultdict(int)
    for d in all_dates:
        # weekday(): 0 = Mon, 6 = Sun
        weekday_counts[d['datetime'].weekday()] += 1
        
    if weekday_counts:
        best_weekday_idx = max(weekday_counts.items(), key=lambda x: x[1])[0]
        weekday_name = calendar.day_name[best_weekday_idx]
        highlights['favorite_weekday'] = {
            'day': weekday_name,
            'commits': weekday_counts[best_weekday_idx],
            'total_commits': len(all_dates)
        }
        
    # 4. Repo Love
    if repo_commits:
        best_repo = max(repo_commits.items(), key=lambda x: x[1])
        highlights['best_repo'] = {
            'name': best_repo[0],
            'commits': best_repo[1]
        }
        
    # 5. Longest Break
    if unique_dates and len(unique_dates) > 1:
        max_break = 0
        max_break_start = None
        max_break_end = None
        
        for i in range(1, len(unique_dates)):
            delta = (unique_dates[i] - unique_dates[i-1]).days
            if delta > 1:
                break_days = delta - 1
                if break_days > max_break:
                    max_break = break_days
                    max_break_start = unique_dates[i-1] + timedelta(days=1)
                    max_break_end = unique_dates[i] - timedelta(days=1)
        
        if max_break > 0:
            highlights['longest_break'] = {
                'days': max_break,
                'start': max_break_start,
                'end': max_break_end
            }

    return highlights
