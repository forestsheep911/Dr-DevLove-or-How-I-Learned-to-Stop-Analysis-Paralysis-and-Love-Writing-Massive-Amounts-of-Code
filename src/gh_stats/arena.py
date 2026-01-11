"""
Arena module: Competition rankings for org-summary mode.
"""
from collections import defaultdict
import datetime


def calculate_user_streak(messages, since_date, until_date):
    """
    Calculate the longest consecutive commit streak for a user.
    Returns (streak_days, start_date, end_date) or None if no commits.
    """
    if not messages:
        return None
    
    # Extract unique dates
    dates = set()
    for msg in messages:
        if 'date' in msg:
            d = msg['date']
            if isinstance(d, datetime.datetime):
                dates.add(d.date())
            elif isinstance(d, datetime.date):
                dates.add(d)
    
    if not dates:
        return None
    
    sorted_dates = sorted(dates)
    
    max_streak = 1
    max_start = sorted_dates[0]
    max_end = sorted_dates[0]
    
    current_streak = 1
    current_start = sorted_dates[0]
    
    for i in range(1, len(sorted_dates)):
        if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
            current_streak += 1
        else:
            if current_streak > max_streak:
                max_streak = current_streak
                max_start = current_start
                max_end = sorted_dates[i-1]
            current_streak = 1
            current_start = sorted_dates[i]
    
    # Check the last streak
    if current_streak > max_streak:
        max_streak = current_streak
        max_start = current_start
        max_end = sorted_dates[-1]
    
    return (max_streak, max_start, max_end)


def generate_arena_rankings(team_stats, since_date, until_date):
    """
    Generate competition rankings from team stats.
    
    Returns dict:
    {
        'commit_ranking': [(user, count), ...],
        'additions_ranking': [(user, added), ...],
        'deletions_ranking': [(user, deleted), ...],
        'total_changes_ranking': [(user, changes), ...],
        'longest_streak_ranking': [(user, days, start, end), ...],
        'avg_commit_size_ranking': [(user, avg_lines), ...],
    }
    """
    rankings = {}
    
    # Commit ranking (descending)
    rankings['commit_ranking'] = sorted(
        [(user, data['commits']) for user, data in team_stats.items()],
        key=lambda x: x[1], reverse=True
    )
    
    # Code additions ranking (descending)
    rankings['additions_ranking'] = sorted(
        [(user, data['added']) for user, data in team_stats.items()],
        key=lambda x: x[1], reverse=True
    )
    
    # Code deletions ranking (descending - more deletions = higher rank)
    rankings['deletions_ranking'] = sorted(
        [(user, data['deleted']) for user, data in team_stats.items()],
        key=lambda x: x[1], reverse=True
    )
    
    # Total changes ranking (added + deleted, descending)
    rankings['total_changes_ranking'] = sorted(
        [(user, data['added'] + data['deleted']) for user, data in team_stats.items()],
        key=lambda x: x[1], reverse=True
    )
    
    # Longest streak ranking
    streak_data = []
    for user, data in team_stats.items():
        streak = calculate_user_streak(data.get('messages', []), since_date, until_date)
        if streak:
            streak_data.append((user, streak[0], streak[1], streak[2]))
    rankings['longest_streak_ranking'] = sorted(streak_data, key=lambda x: x[1], reverse=True)
    
    # Average commit size ranking (ascending - smaller avg is better practice)
    avg_size_data = []
    for user, data in team_stats.items():
        if data['commits'] > 0:
            avg = (data['added'] + data['deleted']) / data['commits']
            avg_size_data.append((user, round(avg, 1)))
    rankings['avg_commit_size_ranking'] = sorted(avg_size_data, key=lambda x: x[1], reverse=True)
    
    return rankings
