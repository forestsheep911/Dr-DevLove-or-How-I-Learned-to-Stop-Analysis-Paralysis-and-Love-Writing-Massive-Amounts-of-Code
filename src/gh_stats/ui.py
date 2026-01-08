import sys

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    WARNING = '\033[93m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ENDC = '\033[0m'

def print_styled(text, color=Colors.ENDC, bold=False):
    style = color + (Colors.BOLD if bold else '')
    print(f"{style}{text}{Colors.ENDC}")

def print_progress(current, total, repo_name, status=""):
    bar_width = 20
    filled = int(bar_width * current / total) if total > 0 else 0
    bar = "█" * filled + "░" * (bar_width - filled)
    percent = int(100 * current / total) if total > 0 else 0
    # Truncate repo name if too long
    display_repo = repo_name[:30] + "..." if len(repo_name) > 33 else repo_name
    sys.stdout.write(f"\r{Colors.CYAN}[{bar}]{Colors.ENDC} {percent:3d}% │ {display_repo:<35} {status}\033[K")
    sys.stdout.flush()

def print_progress_done(message="Complete"):
    sys.stdout.write(f"\r{Colors.GREEN}[✔]{Colors.ENDC} {message}\033[K\n")
    sys.stdout.flush()

def generate_ascii_table(stats, since_date, until_date, use_colors=True):
    if not stats:
        return "No commits found in the specified range."

    lines = []
    lines.append("")
    
    # Helper for color
    def c(text, color):
        return f"{color}{text}{Colors.ENDC}" if use_colors else text
    
    # Helper to truncate long names with ellipsis in the middle
    def truncate_middle(s, max_len=50):
        if len(s) <= max_len:
            return s
        # Keep some chars from start and end, put ... in middle
        keep = (max_len - 3) // 2
        return s[:keep] + "..." + s[-(max_len - 3 - keep):]

    max_repo_len = max(len(r) for r in stats.keys())
    col_repo = min(max(max_repo_len + 2, 17), 52)  # Cap at 52 (50 + padding)
    col_commits = 10
    col_changes = 25

    def get_sep(chars):
        # chars: 0=left, 1=mid, 2=sep, 3=right
        if use_colors:
            return f"{Colors.BLUE}{chars[0]}{chars[1]*col_repo}{chars[2]}{chars[1]*col_commits}{chars[2]}{chars[1]*col_changes}{chars[3]}{Colors.ENDC}"
        else:
            return f"{chars[0]}{chars[1]*col_repo}{chars[2]}{chars[1]*col_commits}{chars[2]}{chars[1]*col_changes}{chars[3]}"

    lines.append(get_sep("┌─┬┐"))
    
    # Header
    h_repo = c(f"{'Repository':<{col_repo-1}}", Colors.BOLD)
    h_commits = c(f"{'Commits':<{col_commits-1}}", Colors.BOLD)
    h_changes = c(f"{'Changes':<{col_changes-1}}", Colors.BOLD)
    
    sep_char = c("│", Colors.BLUE)
    lines.append(f"{sep_char} {h_repo}{sep_char} {h_commits}{sep_char} {h_changes}{sep_char}")
    lines.append(get_sep("├─┼┤"))

    total_commits = total_added = total_deleted = 0
    
    for repo, data in sorted(stats.items(), key=lambda x: x[1]['commits'], reverse=True):
        total_commits += data['commits']
        total_added += data['added']
        total_deleted += data['deleted']
        
        if use_colors:
            changes_str = f"{Colors.GREEN}+{data['added']}{Colors.ENDC} / {Colors.RED}-{data['deleted']}{Colors.ENDC}"
        else:
            changes_str = f"+{data['added']} / -{data['deleted']}"
            
        visible_len = len(f"+{data['added']} / -{data['deleted']}")
        padding = col_changes - 1 - visible_len
        
        r_name = c(f"{truncate_middle(repo):<{col_repo-1}}", Colors.CYAN)
        c_count = f"{str(data['commits']):<{col_commits-1}}"
        
        lines.append(f"{sep_char} {r_name}{sep_char} {c_count}{sep_char} {changes_str}{' '*padding}{sep_char}")

    lines.append(get_sep("└─┴┘"))

    # Calculate additional metrics
    total_changes = total_added + total_deleted
    net_growth = total_added - total_deleted
    
    # Calculate active days
    all_dates = set()
    for data in stats.values():
        for msg in data.get('messages', []):
            if 'date' in msg:
                all_dates.add(msg['date'].date())
    active_days = len(all_dates)
    total_days = (until_date - since_date).days + 1
    active_pct = (active_days / total_days * 100) if total_days > 0 else 0

    lines.append(f"\n{c(f'Summary ({since_date} ~ {until_date}):', Colors.BOLD)}")
    lines.append(f"  • Active Projects: {c(len(stats), Colors.CYAN)}")
    lines.append(f"  • Total Commits:   {c(total_commits, Colors.CYAN)}")
    lines.append(f"  • Total Changes:   {c(total_changes, Colors.CYAN)} lines (added + deleted)")
    lines.append(f"  • Net Growth:      {c(f'{net_growth:+}', Colors.GREEN if net_growth >= 0 else Colors.RED)} lines")
    lines.append(f"  • Lines Added:     {c(f'+{total_added}', Colors.GREEN)}")
    lines.append(f"  • Lines Deleted:   {c(f'-{total_deleted}', Colors.RED)}")
    if active_days > 0:
        lines.append(f"  • Active Days:     {c(active_days, Colors.CYAN)} / {total_days} ({active_pct:.0f}%)")
    
    return "\n".join(lines)

def render_table(stats, since_date, until_date):
    print(generate_ascii_table(stats, since_date, until_date, use_colors=True))

def generate_markdown_table(stats, since_date, until_date):
    """Generate a proper Markdown table for file output."""
    if not stats:
        return "No commits found in the specified range."

    lines = []
    lines.append(f"## Summary ({since_date} ~ {until_date})\n")
    
    # Table header
    lines.append("| Repository | Commits | Changes |")
    lines.append("|:-----------|--------:|:--------|")
    
    total_commits = total_added = total_deleted = 0
    
    for repo, data in sorted(stats.items(), key=lambda x: x[1]['commits'], reverse=True):
        total_commits += data['commits']
        total_added += data['added']
        total_deleted += data['deleted']
        
        changes_str = f"+{data['added']} / -{data['deleted']}"
        lines.append(f"| {repo} | {data['commits']} | {changes_str} |")

    lines.append("")
    
    # Calculate additional metrics
    total_changes = total_added + total_deleted
    net_growth = total_added - total_deleted
    
    lines.append(f"**Totals:**")
    lines.append(f"- Active Projects: {len(stats)}")
    lines.append(f"- Total Commits: {total_commits}")
    lines.append(f"- Total Changes: {total_changes} lines")
    lines.append(f"- Net Growth: {net_growth:+} lines")
    lines.append(f"- Lines Added: +{total_added}")
    lines.append(f"- Lines Deleted: -{total_deleted}")
    
    return "\n".join(lines)

def generate_team_table(team_stats, since_date, until_date, use_colors=True):
    """Generate ASCII table for team stats (sorted by commits descending)."""
    if not team_stats:
        return "No commits found in the specified range."

    lines = []
    lines.append("")
    
    def c(text, color):
        return f"{color}{text}{Colors.ENDC}" if use_colors else text

    max_user_len = max(len(u) for u in team_stats.keys())
    col_user = min(max(max_user_len + 2, 15), 30)
    col_commits = 10
    col_changes = 25

    def get_sep(chars):
        if use_colors:
            return f"{Colors.BLUE}{chars[0]}{chars[1]*col_user}{chars[2]}{chars[1]*col_commits}{chars[2]}{chars[1]*col_changes}{chars[3]}{Colors.ENDC}"
        else:
            return f"{chars[0]}{chars[1]*col_user}{chars[2]}{chars[1]*col_commits}{chars[2]}{chars[1]*col_changes}{chars[3]}"

    lines.append(get_sep("┌─┬┐"))
    
    h_user = c(f"{'Contributor':<{col_user-1}}", Colors.BOLD)
    h_commits = c(f"{'Commits':<{col_commits-1}}", Colors.BOLD)
    h_changes = c(f"{'Changes':<{col_changes-1}}", Colors.BOLD)
    
    sep_char = c("│", Colors.BLUE)
    lines.append(f"{sep_char} {h_user}{sep_char} {h_commits}{sep_char} {h_changes}{sep_char}")
    lines.append(get_sep("├─┼┤"))

    total_commits = total_added = total_deleted = 0
    
    for user, data in sorted(team_stats.items(), key=lambda x: x[1]['commits'], reverse=True):
        total_commits += data['commits']
        total_added += data['added']
        total_deleted += data['deleted']
        
        if use_colors:
            changes_str = f"{Colors.GREEN}+{data['added']}{Colors.ENDC} / {Colors.RED}-{data['deleted']}{Colors.ENDC}"
        else:
            changes_str = f"+{data['added']} / -{data['deleted']}"
            
        visible_len = len(f"+{data['added']} / -{data['deleted']}")
        padding = col_changes - 1 - visible_len
        
        truncated_user = user[:col_user-3] + ".." if len(user) > col_user-1 else user
        u_name = c(f"{truncated_user:<{col_user-1}}", Colors.CYAN)
        c_count = f"{str(data['commits']):<{col_commits-1}}"
        
        lines.append(f"{sep_char} {u_name}{sep_char} {c_count}{sep_char} {changes_str}{' '*padding}{sep_char}")

    lines.append(get_sep("└─┴┘"))

    # Calculate additional metrics
    total_changes = total_added + total_deleted
    net_growth = total_added - total_deleted
    
    # Calculate active days for team
    all_dates = set()
    for data in team_stats.values():
        for msg in data.get('messages', []):
            if 'date' in msg:
                all_dates.add(msg['date'].date())
    active_days = len(all_dates)
    total_days = (until_date - since_date).days + 1
    active_pct = (active_days / total_days * 100) if total_days > 0 else 0

    lines.append(f"\n{c(f'Team Summary ({since_date} ~ {until_date}):', Colors.BOLD)}")
    lines.append(f"  • Contributors:    {c(len(team_stats), Colors.CYAN)}")
    lines.append(f"  • Total Commits:   {c(total_commits, Colors.CYAN)}")
    lines.append(f"  • Total Changes:   {c(total_changes, Colors.CYAN)} lines")
    lines.append(f"  • Net Growth:      {c(f'{net_growth:+}', Colors.GREEN if net_growth >= 0 else Colors.RED)} lines")
    lines.append(f"  • Lines Added:     {c(f'+{total_added}', Colors.GREEN)}")
    lines.append(f"  • Lines Deleted:   {c(f'-{total_deleted}', Colors.RED)}")
    if active_days > 0:
        lines.append(f"  • Active Days:     {c(active_days, Colors.CYAN)} / {total_days} ({active_pct:.0f}%)")
    
    return "\n".join(lines)

def generate_team_markdown_table(team_stats, since_date, until_date):
    """Generate Markdown table for team stats."""
    if not team_stats:
        return "No commits found in the specified range."

    lines = []
    lines.append(f"## Team Summary ({since_date} ~ {until_date})\n")
    
    lines.append("| Contributor | Commits | Changes |")
    lines.append("|:------------|--------:|:--------|")
    
    total_commits = total_added = total_deleted = 0
    
    for user, data in sorted(team_stats.items(), key=lambda x: x[1]['commits'], reverse=True):
        total_commits += data['commits']
        total_added += data['added']
        total_deleted += data['deleted']
        
        changes_str = f"+{data['added']} / -{data['deleted']}"
        lines.append(f"| {user} | {data['commits']} | {changes_str} |")

    lines.append("")
    
    # Calculate additional metrics
    total_changes = total_added + total_deleted
    net_growth = total_added - total_deleted
    
    lines.append(f"**Team Totals:**")
    lines.append(f"- Contributors: {len(team_stats)}")
    lines.append(f"- Total Commits: {total_commits}")
    lines.append(f"- Total Changes: {total_changes} lines")
    lines.append(f"- Net Growth: {net_growth:+} lines")
    lines.append(f"- Lines Added: +{total_added}")
    lines.append(f"- Lines Deleted: -{total_deleted}")
    
    return "\n".join(lines)
