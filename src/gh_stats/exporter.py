from collections import defaultdict
import datetime

def generate_markdown(stats, since_date, until_date, full_message=False, highlights=None):
    """
    Generates a Markdown string from the commit statistics.
    
    Args:
        stats: Dictionary containing commit data. 
               Expected structure: {repo_full_name: {'messages': [{'date': ..., 'message': ...}], ...}}
        since_date: Start date of the range
        until_date: End date of the range
        full_message: If True, includes the full commit message body.
        highlights: Optional dict of highlights data.
        
    Returns:
        str: Formatted Markdown string
    """
    md = []
    
    # Use standalone function if highlights exist
    if highlights:
        md.append(generate_highlights_markdown(highlights))
        md.append("")
        
    md.append(f"# GitHub Activity Report ({since_date} to {until_date})\n")

def generate_highlights_markdown(highlights):
    """Generate markdown section for highlights."""
    if not highlights:
        return ""
        
    md = []
    md.append("## ✨ Highlights")
    if 'streak' in highlights:
        s = highlights['streak']
        start = s['start'].strftime('%Y-%m-%d')
        end = s['end'].strftime('%Y-%m-%d')
        md.append(f"- **🔥 Longest Streak:** {s['days']} days ({start} ~ {end})")
        
    if 'best_day' in highlights:
        b = highlights['best_day']
        md.append(f"- **🏆 Most Productive Day:** {b['date']} ({b['commits']} commits)")
        
    if 'favorite_weekday' in highlights:
        w = highlights['favorite_weekday']
        pct = w['commits'] / w['total_commits'] * 100
        md.append(f"- **📅 Favorite Weekday:** {w['day']} ({pct:.0f}% of commits)")
        
    if 'best_repo' in highlights:
        r = highlights['best_repo']
        md.append(f"- **❤️  Repo Love:** {r['name']} ({r['commits']} commits)")
    
    return "\n".join(md)
    
    # Sort repos by commit count (desc) seems useful, or just alphabetical. 
    # Let's do active repos first (more commits).
    sorted_repos = sorted(stats.items(), key=lambda x: len(x[1].get('messages', [])), reverse=True)
    
    for repo_name, data in sorted_repos:
        messages = data.get('messages', [])
        if not messages:
            continue
            
        md.append(f"## {repo_name}\n")
        
        # Sort messages by date (oldest to newest)
        sorted_messages = sorted(messages, key=lambda x: x['date'])
        
        for msg in sorted_messages:
            # Format date with time (HH:MM)
            if isinstance(msg['date'], datetime.datetime):
                date_str = msg['date'].strftime('%Y-%m-%d %H:%M')
            else:
                date_str = msg['date'].strftime('%Y-%m-%d')
            
            # Clean up message
            raw_lines = msg['message'].strip().split('\n')
            title = raw_lines[0].strip()
            
            md.append(f"- [{date_str}] {title}")
            
            if full_message and len(raw_lines) > 1:
                # Add body if exists
                body_lines = raw_lines[1:]
                # Filter out leading empty lines in body if any
                while body_lines and not body_lines[0].strip():
                    body_lines.pop(0)
                
                if body_lines:
                    # Append body lines with indentation
                    for line in body_lines:
                        # Escape leading # to prevent being interpreted as headers
                        escaped_line = line
                        stripped = line.lstrip()
                        if stripped.startswith('#'):
                            # Preserve leading whitespace, escape the #
                            leading_ws = line[:len(line) - len(stripped)]
                            escaped_line = leading_ws + '\\' + stripped
                        md.append(f"    {escaped_line}")
                    # md.append("") # optional spacing
    
    return "\n".join(md)

def generate_team_markdown(team_stats, since_date, until_date, group_by='user', full_message=False):
    """
    Generate markdown for team stats export.
    
    Args:
        team_stats: dict {author: {commits, added, deleted, repos: {...}, messages: []}}
        group_by: 'user' or 'repo'
        full_message: Include full commit body
    """
    md = []
    # Use a slightly different header level or text if it follows the table
    # But usually this function is self-contained. 
    # In main.py combined output, this header acts as a separator.
    md.append(f"# Team Activity Report ({since_date} to {until_date})\n")
    
    if group_by == 'user':
        # Group by user then repo
        for user, data in sorted(team_stats.items(), key=lambda x: x[1]['commits'], reverse=True):
            md.append(f"## {user}")
            md.append(f"**Commits:** {data['commits']} | **Changes:** +{data['added']} / -{data['deleted']}\n")
            
            # Show repos breakdown
            for repo, repo_data in sorted(data['repos'].items(), key=lambda x: x[1]['commits'], reverse=True):
                md.append(f"### {repo}")
                md.append(f"Commits: {repo_data['commits']} | +{repo_data['added']} / -{repo_data['deleted']}\n")
            
            # Messages for this user
            if data['messages']:
                md.append("#### Commits")
                sorted_msgs = sorted(data['messages'], key=lambda x: x['date'], reverse=True)
                for msg in sorted_msgs:
                    date_str = msg['date'].strftime('%Y-%m-%d %H:%M')
                    raw_lines = msg['message'].strip().split('\n')
                    title = raw_lines[0].strip()
                    md.append(f"- [{date_str}] ({msg['repo']}) {title}")
                    
                    if full_message and len(raw_lines) > 1:
                        body_lines = raw_lines[1:]
                        while body_lines and not body_lines[0].strip():
                            body_lines.pop(0)
                        if body_lines:
                            for line in body_lines:
                                escaped_line = line
                                stripped = line.lstrip()
                                if stripped.startswith('#'):
                                    leading_ws = line[:len(line) - len(stripped)]
                                    escaped_line = leading_ws + '\\' + stripped
                                md.append(f"    {escaped_line}")
            md.append("")
    else:
        # Group by repo then user
        repo_user_map = {}  # {repo: {user: {commits, added, deleted, messages}}}
        
        for user, data in team_stats.items():
            for repo, repo_data in data['repos'].items():
                if repo not in repo_user_map:
                    repo_user_map[repo] = {}
                repo_user_map[repo][user] = {
                    'commits': repo_data['commits'],
                    'added': repo_data['added'],
                    'deleted': repo_data['deleted'],
                    'messages': [m for m in data['messages'] if m.get('repo') == repo]
                }
        
        for repo in sorted(repo_user_map.keys()):
            users_data = repo_user_map[repo]
            total_commits = sum(u['commits'] for u in users_data.values())
            total_added = sum(u['added'] for u in users_data.values())
            total_deleted = sum(u['deleted'] for u in users_data.values())
            
            md.append(f"## {repo}")
            md.append(f"**Total:** {total_commits} commits | +{total_added} / -{total_deleted}\n")
            
            for user, udata in sorted(users_data.items(), key=lambda x: x[1]['commits'], reverse=True):
                md.append(f"### {user}")
                md.append(f"Commits: {udata['commits']} | +{udata['added']} / -{udata['deleted']}")
                
                if udata['messages']:
                    sorted_msgs = sorted(udata['messages'], key=lambda x: x['date'], reverse=True)
                    for msg in sorted_msgs:
                        date_str = msg['date'].strftime('%Y-%m-%d %H:%M')
                        raw_lines = msg['message'].strip().split('\n')
                        title = raw_lines[0].strip()
                        md.append(f"- [{date_str}] {title}")
                        
                        if full_message and len(raw_lines) > 1:
                            body_lines = raw_lines[1:]
                            while body_lines and not body_lines[0].strip():
                                body_lines.pop(0)
                            if body_lines:
                                for line in body_lines:
                                    escaped_line = line
                                    stripped = line.lstrip()
                                    if stripped.startswith('#'):
                                        leading_ws = line[:len(line) - len(stripped)]
                                        escaped_line = leading_ws + '\\' + stripped
                                    md.append(f"    {escaped_line}")
                md.append("")
    
    return "\n".join(md)

import os

# Default directory for exported reports
DEFAULT_EXPORT_DIR = "reports"

def write_export_file(content, since_date, until_date, output_filename=None):
    """
    Writes the content to a file. Avoids overwriting by appending a counter.
    Files are saved to 'reports/' directory by default.
    """
    # Determine target directory and filename
    if output_filename:
        # Check if user provided a path with directory
        dir_part = os.path.dirname(output_filename)
        file_part = os.path.basename(output_filename)
        
        if dir_part:
            # User specified a directory path
            target_dir = dir_part
        else:
            # No directory specified, use default
            target_dir = DEFAULT_EXPORT_DIR
        
        base_name, extension = os.path.splitext(file_part)
        if not extension:
            extension = ".md"
            file_part += extension
    else:
        # Default filename and directory
        target_dir = DEFAULT_EXPORT_DIR
        base_name = f"gh_stats_export_{since_date}_{until_date}"
        extension = ".md"
        file_part = f"{base_name}{extension}"
    
    # Ensure target directory exists
    if target_dir and not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # Build full path
    filename = os.path.join(target_dir, file_part) if target_dir else file_part
    
    # Avoid overwriting by appending counter
    counter = 1
    original_base = os.path.join(target_dir, base_name) if target_dir else base_name
    while os.path.exists(filename):
        filename = f"{original_base}_{counter}{extension}"
        counter += 1
        
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return filename
