#!/usr/bin/env python3
"""
JSON 导出模块 - 将统计数据导出为 JSON 格式供 Web 前端使用
"""
import json
import datetime
from collections import defaultdict
from typing import Any, Dict, List, Optional


def export_to_json(
    stats: Dict,
    since_date: datetime.date,
    until_date: datetime.date,
    user: str,
    highlights: Optional[Dict] = None,
    portrait: Optional[Dict] = None,
    team_stats: Optional[Dict] = None,
    arena: Optional[List] = None,
    org: Optional[str] = None,
) -> str:
    """
    将统计数据导出为 JSON 格式
    
    Args:
        stats: 仓库统计数据 {repo_name: {commits, added, deleted, messages}}
        since_date: 开始日期
        until_date: 结束日期
        user: 用户名
        highlights: 亮点数据 (可选)
        portrait: 画像数据 (可选)
        team_stats: 团队统计数据 (可选，用于 org-summary 模式)
        arena: 竞技场排名 (可选)
        org: 组织名 (可选，用于 org-summary 模式)
        
    Returns:
        JSON 字符串
    """
    data = {
        "meta": {
            "user": user,
            "dateRange": {
                "since": since_date.isoformat(),
                "until": until_date.isoformat(),
            },
            "generatedAt": datetime.datetime.now().isoformat(),
            "mode": "org-summary" if org else "personal",
        }
    }
    
    if org:
        data["meta"]["org"] = org
    
    # 计算汇总
    if team_stats:
        # Org-summary 模式
        total_commits = sum(d['commits'] for d in team_stats.values())
        total_added = sum(d['added'] for d in team_stats.values())
        total_deleted = sum(d['deleted'] for d in team_stats.values())
        
        # 从 team_stats 中提取所有仓库
        all_repos = set()
        for user_data in team_stats.values():
            all_repos.update(user_data.get('repos', {}).keys())
        
        # 计算活跃天数
        all_dates = set()
        for user_data in team_stats.values():
            for msg in user_data.get('messages', []):
                if isinstance(msg['date'], datetime.datetime):
                    all_dates.add(msg['date'].date())
                elif isinstance(msg['date'], datetime.date):
                    all_dates.add(msg['date'])
        
        data["summary"] = {
            "totalCommits": total_commits,
            "totalAdded": total_added,
            "totalDeleted": total_deleted,
            "netGrowth": total_added - total_deleted,
            "activeDays": len(all_dates),
            "activeRepos": len(all_repos),
        }
        
        # 仓库统计 (合并所有用户的贡献)
        repo_stats = defaultdict(lambda: {"commits": 0, "added": 0, "deleted": 0})
        for user_data in team_stats.values():
            for repo_name, repo_data in user_data.get('repos', {}).items():
                repo_stats[repo_name]["commits"] += repo_data['commits']
                repo_stats[repo_name]["added"] += repo_data['added']
                repo_stats[repo_name]["deleted"] += repo_data['deleted']
        
        data["repos"] = [
            {
                "name": name,
                "commits": d["commits"],
                "added": d["added"],
                "deleted": d["deleted"],
            }
            for name, d in sorted(repo_stats.items(), key=lambda x: x[1]["commits"], reverse=True)
        ]
        
        # 时间线 (按日期聚合)
        timeline = defaultdict(lambda: {"commits": 0, "added": 0, "deleted": 0})
        for user_data in team_stats.values():
            for msg in user_data.get('messages', []):
                if isinstance(msg['date'], datetime.datetime):
                    date_str = msg['date'].strftime('%Y-%m-%d')
                else:
                    date_str = msg['date'].isoformat()
                timeline[date_str]["commits"] += 1
                timeline[date_str]["added"] += msg.get('added', 0)
                timeline[date_str]["deleted"] += msg.get('deleted', 0)
        
        data["timeline"] = [
            {"date": date, **counts}
            for date, counts in sorted(timeline.items())
        ]
        
    else:
        # Personal 模式
        total_commits = sum(d['commits'] for d in stats.values())
        total_added = sum(d['added'] for d in stats.values())
        total_deleted = sum(d['deleted'] for d in stats.values())
        
        # 计算活跃天数
        all_dates = set()
        for repo_data in stats.values():
            for msg in repo_data.get('messages', []):
                if isinstance(msg['date'], datetime.datetime):
                    all_dates.add(msg['date'].date())
                elif isinstance(msg['date'], datetime.date):
                    all_dates.add(msg['date'])
        
        active_repos = sum(1 for d in stats.values() if d['commits'] > 0)
        
        data["summary"] = {
            "totalCommits": total_commits,
            "totalAdded": total_added,
            "totalDeleted": total_deleted,
            "netGrowth": total_added - total_deleted,
            "activeDays": len(all_dates),
            "activeRepos": active_repos,
        }
        
        # 仓库统计
        data["repos"] = [
            {
                "name": name,
                "commits": d["commits"],
                "added": d["added"],
                "deleted": d["deleted"],
            }
            for name, d in sorted(stats.items(), key=lambda x: x[1]["commits"], reverse=True)
            if d["commits"] > 0
        ]
        
        # 时间线 (按日期聚合)
        timeline = defaultdict(lambda: {"commits": 0, "added": 0, "deleted": 0})
        for repo_data in stats.values():
            for msg in repo_data.get('messages', []):
                if isinstance(msg['date'], datetime.datetime):
                    date_str = msg['date'].strftime('%Y-%m-%d')
                else:
                    date_str = msg['date'].isoformat()
                timeline[date_str]["commits"] += 1
                timeline[date_str]["added"] += msg.get('added', 0)
                timeline[date_str]["deleted"] += msg.get('deleted', 0)
        
        data["timeline"] = [
            {"date": date, **counts}
            for date, counts in sorted(timeline.items())
        ]
    
    # 亮点数据
    if highlights:
        data["highlights"] = _format_highlights(highlights)
    
    # 画像数据
    if portrait:
        data["portrait"] = _format_portrait(portrait)
    
    # 竞技场排名
    if arena:
        data["arena"] = arena
    
    return json.dumps(data, ensure_ascii=False, indent=2)


def _format_highlights(highlights: Dict) -> Dict:
    """格式化亮点数据"""
    result = {}
    
    if 'streak' in highlights:
        s = highlights['streak']
        result["streak"] = {
            "days": s['days'],
            "start": s['start'].isoformat() if hasattr(s['start'], 'isoformat') else str(s['start']),
            "end": s['end'].isoformat() if hasattr(s['end'], 'isoformat') else str(s['end']),
        }
    
    if 'best_day' in highlights:
        b = highlights['best_day']
        result["bestDay"] = {
            "date": b['date'] if isinstance(b['date'], str) else b['date'].isoformat(),
            "commits": b['commits'],
            "changes": b['changes'],
        }
    
    if 'favorite_weekday' in highlights:
        w = highlights['favorite_weekday']
        weekday_map = {
            'Monday': (0, '周一'),
            'Tuesday': (1, '周二'),
            'Wednesday': (2, '周三'),
            'Thursday': (3, '周四'),
            'Friday': (4, '周五'),
            'Saturday': (5, '周六'),
            'Sunday': (6, '周日'),
        }
        day_index, day_cn = weekday_map.get(w['day'], (0, w['day']))
        result["favoriteWeekday"] = {
            "day": day_cn,
            "dayIndex": day_index,
            "commits": w.get('commits', 0),
            "changes": w.get('changes', 0),
        }
    
    if 'best_repo' in highlights:
        r = highlights['best_repo']
        result["bestRepo"] = {
            "name": r['name'],
            "commits": r['commits'],
        }
    
    if 'longest_break' in highlights:
        b = highlights['longest_break']
        result["longestBreak"] = {
            "days": b['days'],
            "start": b['start'].isoformat() if hasattr(b['start'], 'isoformat') else str(b['start']),
            "end": b['end'].isoformat() if hasattr(b['end'], 'isoformat') else str(b['end']),
        }
    
    return result


def _format_portrait(portrait: Dict) -> Dict:
    """格式化画像数据"""
    result = {
        "weekdayStats": portrait.get('weekday_stats', {}),
        "hourStats": portrait.get('hour_stats', {}),
        "avgLinesPerCommit": portrait.get('avg_lines_per_commit', 0),
    }
    
    # 仓库冠军
    champions = {}
    if 'net_growth_champion' in portrait and portrait['net_growth_champion']:
        name, value = portrait['net_growth_champion']
        champions["growth"] = {"name": name, "value": value}
    
    if 'refactor_champion' in portrait and portrait['refactor_champion']:
        name, value = portrait['refactor_champion']
        champions["refactor"] = {"name": name, "value": value}
    
    if 'slimming_champion' in portrait and portrait['slimming_champion']:
        name, value = portrait['slimming_champion']
        champions["slimming"] = {"name": name, "value": value}
    
    if champions:
        result["repoChampions"] = champions
    
    return result


def generate_arena_data(team_stats: Dict, top_n: Optional[int] = None) -> List[Dict]:
    """
    生成竞技场排名数据
    
    Args:
        team_stats: 团队统计数据
        top_n: 返回前 N 名，None 表示全部
        
    Returns:
        排名列表
    """
    # 按提交数排序
    sorted_users = sorted(
        team_stats.items(),
        key=lambda x: (x[1]['commits'], x[1]['added']),
        reverse=True
    )
    
    if top_n:
        sorted_users = sorted_users[:top_n]
    
    return [
        {
            "rank": i + 1,
            "user": user,
            "commits": data['commits'],
            "added": data['added'],
            "deleted": data['deleted'],
            "netGrowth": data['added'] - data['deleted'],
        }
        for i, (user, data) in enumerate(sorted_users)
    ]
