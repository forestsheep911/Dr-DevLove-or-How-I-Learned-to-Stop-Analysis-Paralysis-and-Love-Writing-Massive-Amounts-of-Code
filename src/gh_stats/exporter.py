from collections import defaultdict
import datetime

def generate_markdown(stats, since_date, until_date, full_message=False):
    """
    Generates a Markdown string from the commit statistics.
    
    Args:
        stats: Dictionary containing commit data. 
               Expected structure: {repo_full_name: {'messages': [{'date': ..., 'message': ...}], ...}}
        since_date: Start date of the range
        until_date: End date of the range
        full_message: If True, includes the full commit message body.
        
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

import os

def write_export_file(content, since_date, until_date, output_filename=None):
    """
    Writes the content to a file. Avoids overwriting by appending a counter.
    """
    if output_filename:
        # User specified filename
        base_name, extension = os.path.splitext(output_filename)
        if not extension:
             extension = ".md" 
             output_filename += extension
             filename = output_filename
        else:
            filename = output_filename
    else:
        # Default filename
        base_name = f"gh_stats_export_{since_date}_{until_date}"
        extension = ".md"
        filename = f"{base_name}{extension}"
    
    counter = 1
    # Check if we need to rename to avoid overwrite
    # Note: If user provided 'report.md', and it exists, we will try 'report_1.md'
    original_base = base_name
    while os.path.exists(filename):
        # Reconstruct filename with counter
        # Special handling if base_name already ends with active counter pattern could be nice but simple appending is safer and easier.
        filename = f"{original_base}_{counter}{extension}"
        counter += 1
        
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return filename
