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

    lines.append(f"\n{c(f'Summary ({since_date} ~ {until_date}):', Colors.BOLD)}")
    lines.append(f"  • Active Projects: {c(len(stats), Colors.CYAN)}")
    lines.append(f"  • Total Commits:   {c(total_commits, Colors.CYAN)}")
    lines.append(f"  • Total Growth:    {c(f'+{total_added}', Colors.GREEN)} lines")
    lines.append(f"  • Total Cleaning:  {c(f'-{total_deleted}', Colors.RED)} lines")
    
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
    lines.append(f"**Totals:**")
    lines.append(f"- Active Projects: {len(stats)}")
    lines.append(f"- Total Commits: {total_commits}")
    lines.append(f"- Lines Added: +{total_added}")
    lines.append(f"- Lines Deleted: -{total_deleted}")
    
    return "\n".join(lines)
