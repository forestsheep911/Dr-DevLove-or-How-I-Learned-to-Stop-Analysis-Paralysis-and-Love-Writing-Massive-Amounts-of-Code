from collections import defaultdict
import datetime

def generate_markdown(stats, since_date, until_date):
    """
    Generates a Markdown string from the commit statistics.
    
    Args:
        stats: Dictionary containing commit data. 
               Expected structure: {repo_full_name: {'messages': [{'date': ..., 'message': ...}], ...}}
        since_date: Start date of the range
        until_date: End date of the range
        
    Returns:
        str: Formatted Markdown string
    """
    md = []
    md.append(f"# GitHub Activity Report ({since_date} to {until_date})\n")
    
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
            date_str = msg['date'].strftime('%Y-%m-%d')
            # Clean up message: take first line, strip whitespace
            clean_msg = msg['message'].strip().split('\n')[0]
            md.append(f"- [{date_str}] {clean_msg}")
        
        md.append("") # Empty line between repos
        
    return "\n".join(md)

def write_export_file(content, since_date, until_date):
    """
    Writes the content to a file.
    """
    filename = f"gh_stats_export_{since_date}_{until_date}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return filename
