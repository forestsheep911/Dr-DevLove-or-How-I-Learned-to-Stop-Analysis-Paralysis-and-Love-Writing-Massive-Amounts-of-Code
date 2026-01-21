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
    
    total_commits = total_added = total_deleted = 0
    total_days = (until_date - since_date).days + 1
    all_active_repos = set()
    table_rows = []
    
    for user, data in sorted(team_stats.items(), key=lambda x: x[1]['commits'], reverse=True):
        total_commits += data['commits']
        total_added += data['added']
        total_deleted += data['deleted']
        
        # Collect active repos
        all_active_repos.update(data.get('repos', {}).keys())
        
        net_growth = data['added'] - data['deleted']
        total_changes = data['added'] + data['deleted']
        
        # Calculate active days for this user
        user_dates = set()
        for msg in data.get('messages', []):
            if 'date' in msg:
                user_dates.add(msg['date'].date())
        active_days = len(user_dates)
        active_pct = (active_days / total_days * 100) if total_days > 0 else 0
        active_str = f"{active_days}/{total_days} ({active_pct:.0f}%)"
        
        table_rows.append(f"| {user} | {data['commits']} | +{data['added']} | -{data['deleted']} | {net_growth:+} | {total_changes} | {active_str} |")

    # Team Totals Section (Moved to top)
    total_changes = total_added + total_deleted
    net_growth = total_added - total_deleted
    
    lines.append(f"**Team Totals:**")
    lines.append(f"- Contributors: {len(team_stats)}")
    lines.append(f"- Active Repos: {len(all_active_repos)}")
    lines.append(f"- Total Commits: {total_commits}")
    lines.append(f"- Total Changes: {total_changes} lines")
    lines.append(f"- Net Growth: {net_growth:+} lines")
    lines.append(f"- Lines Added: +{total_added}")
    lines.append(f"- Lines Deleted: -{total_deleted}")
    lines.append("")
    
    # Table Header & Content
    lines.append("| Contributor | Commits | Added | Deleted | Net Growth | Total Changes | Active Days |")
    lines.append("|:------------|--------:|------:|--------:|-----------:|--------------:|:------------|")
    lines.extend(table_rows)
    
    return "\n".join(lines)

def print_highlights(highlights):
    """Print highlights to console."""
    if not highlights:
        return
        
    def c(text, color):
        return f"{color}{text}{Colors.ENDC}"
        
    print(f"\n{Colors.BOLD}✨ Highlights:{Colors.ENDC}")
    
    if 'streak' in highlights:
        s = highlights['streak']
        start = s['start'].strftime('%Y-%m-%d')
        end = s['end'].strftime('%Y-%m-%d')
        print(f"  🔥 {Colors.BOLD}Longest Streak:{Colors.ENDC}      {c(s['days'], Colors.CYAN)} days ({start} ~ {end})")
        
    if 'best_day' in highlights:
        b = highlights['best_day']
        print(f"  🏆 {Colors.BOLD}Most Productive Day:{Colors.ENDC} {b['date']} ({c(b['changes'], Colors.CYAN)} lines changed, {b['commits']} commits)")
        
    if 'favorite_weekday' in highlights:
        w = highlights['favorite_weekday']
        pct = w['changes'] / w['total_changes'] * 100 if w.get('total_changes') else 0
        print(f"  📅 {Colors.BOLD}Favorite Weekday:{Colors.ENDC}    {c(w['day'], Colors.CYAN)} ({pct:.0f}% of changes)")
        
    if 'best_repo' in highlights:
        r = highlights['best_repo']
        print(f"  ❤️  {Colors.BOLD}Repo Love:{Colors.ENDC}           {c(r['name'], Colors.CYAN)} ({c(r['commits'], Colors.CYAN)} commits)")

    if 'longest_break' in highlights:
        b = highlights['longest_break']
        start = b['start'].strftime('%Y-%m-%d')
        end = b['end'].strftime('%Y-%m-%d')
        print(f"  🛌 {Colors.BOLD}Longest Break:{Colors.ENDC}       {c(b['days'], Colors.CYAN)} days ({start} ~ {end})")


def _calculate_project_breakdown(team_stats):
    """
    Calculate project-level breakdown with primary contributor detection.
    Returns list of (repo, total_commits, contributor_count, primary_contributor_or_none)
    """
    # Aggregate by repo
    repo_stats = {}  # {repo: {total_commits, total_changes, contributors: {user: changes}}}
    
    for user, data in team_stats.items():
        for repo, repo_data in data.get('repos', {}).items():
            if repo not in repo_stats:
                repo_stats[repo] = {'commits': 0, 'changes': 0, 'contributors': {}}
            repo_stats[repo]['commits'] += repo_data['commits']
            changes = repo_data['added'] + repo_data['deleted']
            repo_stats[repo]['changes'] += changes
            repo_stats[repo]['contributors'][user] = changes
    
    result = []
    for repo, stats in sorted(repo_stats.items(), key=lambda x: x[1]['commits'], reverse=True):
        contributors = stats['contributors']
        sorted_contributors = sorted(contributors.items(), key=lambda x: x[1], reverse=True)
        
        primary = None
        if len(sorted_contributors) >= 2:
            first_changes = sorted_contributors[0][1]
            second_changes = sorted_contributors[1][1]
            # First place > 150% of second place
            if second_changes > 0 and first_changes > second_changes * 1.5:
                pct = (first_changes / stats['changes'] * 100) if stats['changes'] > 0 else 0
                primary = (sorted_contributors[0][0], pct)
        elif len(sorted_contributors) == 1:
            # Only one contributor
            primary = (sorted_contributors[0][0], 100.0)
        
        result.append((repo, stats['commits'], len(contributors), primary))
    
    return result


def _calculate_participant_breakdown(team_stats, since_date, until_date):
    """
    Calculate participant-level breakdown (no code stats).
    Returns list of (user, project_count, commits, active_days_str)
    """
    total_days = (until_date - since_date).days + 1
    result = []
    
    for user, data in sorted(team_stats.items(), key=lambda x: x[1]['commits'], reverse=True):
        project_count = len(data.get('repos', {}))
        commits = data['commits']
        
        # Calculate active days
        user_dates = set()
        for msg in data.get('messages', []):
            if 'date' in msg:
                d = msg['date']
                if hasattr(d, 'date'):
                    user_dates.add(d.date())
                else:
                    user_dates.add(d)
        active_days = len(user_dates)
        active_pct = (active_days / total_days * 100) if total_days > 0 else 0
        active_str = f"{active_days}/{total_days} ({active_pct:.0f}%)"
        
        result.append((user, project_count, commits, active_str))
    
    return result


def _render_console_portraits(lines, team_stats, all_repos, use_colors):
    """Helper to render portraits to console."""
    def c(text, color):
        return f"{color}{text}{Colors.ENDC}" if use_colors else str(text)

    # Team Portrait
    from .portrait import generate_team_portrait
    team_portrait = generate_team_portrait(team_stats)
    
    lines.append("")
    lines.append(f"{c('🎨 Team Portrait:', Colors.BOLD)}")
    
    # Weekday Stats
    lines.append(f"  {c('📅 Work Week Rhythm:', Colors.BOLD)}")
    days_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
    sorted_days = sorted(team_portrait['weekday_stats'].items(), key=lambda x: x[1], reverse=True)
    if sorted_days:
        best_day = sorted_days[0]
        lines.append(f"    • Most Active: {c(days_map[best_day[0]], Colors.CYAN)} ({best_day[1]} commits)")
    
    # Hour Stats
    lines.append(f"  {c('⏰ Peak Hours:', Colors.BOLD)}")
    sorted_hours = sorted(team_portrait['hour_stats'].items(), key=lambda x: x[1], reverse=True)
    if sorted_hours:
        top_3_hours = sorted_hours[:3]
        hours_str = ", ".join([f"{h:02d}:00" for h, count in top_3_hours])
        lines.append(f"    • Top Times: {c(hours_str, Colors.CYAN)}")
        
    # Granularity
    lines.append(f"  {c('📏 Commit Granularity:', Colors.BOLD)}")
    avg_lines = team_portrait['avg_lines_per_commit']
    lines.append(f"    • Avg Lines/Commit: {c(f'{avg_lines:.1f}', Colors.CYAN)}")

    # Repo Portrait
    from .portrait import generate_repo_portrait
    repo_portrait = generate_repo_portrait(team_stats, len(all_repos)) 
    
    lines.append("")
    lines.append(f"{c('🖼️ Repo Portrait:', Colors.BOLD)}")
    
    r = repo_portrait
    if r['net_growth_champion'][0]:
        growth_val = r['net_growth_champion'][1]
        lines.append(f"  • {c('🌲 Growth Champion:', Colors.BOLD)}   {r['net_growth_champion'][0]} ({c(f'+{growth_val}', Colors.GREEN)} net)")
    if r['refactor_champion'][0]:
        lines.append(f"  • {c('🔧 Refactor Champion:', Colors.BOLD)} {r['refactor_champion'][0]} ({c(r['refactor_champion'][1], Colors.CYAN)} changes)")
    if r['slimming_champion'][0]:
        slimming_val = r['slimming_champion'][1]
        lines.append(f"  • {c('📉 Slimming Champion:', Colors.BOLD)} {r['slimming_champion'][0]} ({c(f'{slimming_val}', Colors.RED)} net)")


def generate_org_summary_output(team_stats, since_date, until_date, org_name, show_arena=False, arena_top=5, use_colors=True):
    """Generate console output for org-summary mode."""
    lines = []
    
    def c(text, color):
        return f"{color}{text}{Colors.ENDC}" if use_colors else str(text)
    
    # 1. Totals Section
    total_commits = sum(d['commits'] for d in team_stats.values())
    total_added = sum(d['added'] for d in team_stats.values())
    total_deleted = sum(d['deleted'] for d in team_stats.values())
    total_changes = total_added + total_deleted
    net_growth = total_added - total_deleted
    
    # Count active repos
    all_repos = set()
    for data in team_stats.values():
        all_repos.update(data.get('repos', {}).keys())
    
    lines.append("")
    lines.append(f"{c(f'=== Org Summary: {org_name} ({since_date} ~ {until_date}) ===', Colors.BOLD)}")
    lines.append("")
    lines.append(f"{c('📊 Totals:', Colors.BOLD)}")
    lines.append(f"  • Active Projects: {c(len(all_repos), Colors.CYAN)}")
    lines.append(f"  • Contributors:    {c(len(team_stats), Colors.CYAN)}")
    lines.append(f"  • Total Commits:   {c(total_commits, Colors.CYAN)}")
    lines.append(f"  • Total Changes:   {c(total_changes, Colors.CYAN)} lines")
    lines.append(f"  • Net Growth:      {c(f'{net_growth:+}', Colors.GREEN if net_growth >= 0 else Colors.RED)} lines")
    lines.append(f"  • Lines Added:     {c(f'+{total_added}', Colors.GREEN)}")
    lines.append(f"  • Lines Deleted:   {c(f'-{total_deleted}', Colors.RED)}")
    
    # 2. Project Breakdown
    lines.append("")
    lines.append(f"{c('📦 Project Breakdown:', Colors.BOLD)}")
    project_data = _calculate_project_breakdown(team_stats)
    for repo, commits, contrib_count, primary in project_data:
        primary_str = ""
        if primary:
            primary_str = f" → {c(f'@{primary[0]}', Colors.CYAN)} ({primary[1]:.0f}%)"
        lines.append(f"  • {repo}: {commits} commits, {contrib_count} contributors{primary_str}")
    
    # 3. Portraits (Moved here)
    _render_console_portraits(lines, team_stats, all_repos, use_colors)

    # 4. Participant Breakdown
    lines.append("")
    lines.append(f"{c('👥 Participant Breakdown:', Colors.BOLD)}")
    participant_data = _calculate_participant_breakdown(team_stats, since_date, until_date)
    for user, proj_count, commits, active_str in participant_data:
        lines.append(f"  • @{user}: {proj_count} projects, {commits} commits, Active: {active_str}")
    
    # 4. Arena (if enabled)
    if show_arena:
        from .arena import generate_arena_rankings
        rankings = generate_arena_rankings(team_stats, since_date, until_date)
        
        lines.append("")
        lines.append(f"{c('🏟️ Arena:', Colors.BOLD)}")
        
        # Helper for slicing: None means all
        def top_n(lst):
            return lst[:arena_top] if arena_top else lst
        
        # Commit Champions
        lines.append(f"\n  {c('🏆 Commit Champions:', Colors.BOLD)}")
        for i, (user, count) in enumerate(top_n(rankings['commit_ranking']), 1):
            lines.append(f"    {i}. @{user}: {count} commits")
            
        # Repo Hunter (New)
        lines.append(f"\n  {c('🐙 Repo Hunter (Project Coverage):', Colors.BOLD)}")
        for i, (user, count) in enumerate(top_n(rankings['active_repos_ranking']), 1):
            lines.append(f"    {i}. @{user}: {c(count, Colors.CYAN)} repos")
        
        # Net Growth (New)
        lines.append(f"\n  {c('🌲 Net Code Growth:', Colors.BOLD)}")
        for i, (user, net) in enumerate(top_n(rankings['net_growth_ranking']), 1):
            color = Colors.GREEN if net >= 0 else Colors.RED
            lines.append(f"    {i}. @{user}: {c(f'{net:+}', color)} lines")
        
        # Code Additions
        lines.append(f"\n  {c('📈 Code Additions:', Colors.BOLD)}")
        for i, (user, added) in enumerate(top_n(rankings['additions_ranking']), 1):
            lines.append(f"    {i}. @{user}: +{added} lines")
        
        # Code Deletions
        lines.append(f"\n  {c('📉 Code Deletions:', Colors.BOLD)}")
        for i, (user, deleted) in enumerate(top_n(rankings['deletions_ranking']), 1):
            lines.append(f"    {i}. @{user}: -{deleted} lines")
        
        # Total Changes
        lines.append(f"\n  {c('📊 Total Changes:', Colors.BOLD)}")
        for i, (user, changes) in enumerate(top_n(rankings['total_changes_ranking']), 1):
            lines.append(f"    {i}. @{user}: {changes} lines")
        
        # Longest Streak
        if rankings['longest_streak_ranking']:
            lines.append(f"\n  {c('🔥 Longest Streak:', Colors.BOLD)}")
            for i, (user, days, start, end) in enumerate(top_n(rankings['longest_streak_ranking']), 1):
                lines.append(f"    {i}. @{user}: {days} days ({start} ~ {end})")
                
        # Active Days (New)
        lines.append(f"\n  {c('📅 Most Consistent (Active Days):', Colors.BOLD)}")
        for i, (user, days) in enumerate(top_n(rankings['active_days_ranking']), 1):
            lines.append(f"    {i}. @{user}: {c(days, Colors.CYAN)} days")
        
        # Avg Commit Size
        lines.append(f"\n  {c('📊 Avg Commit Size (lines/commit):', Colors.BOLD)}")
        for i, (user, avg) in enumerate(top_n(rankings['avg_commit_size_ranking']), 1):
            lines.append(f"    {i}. @{user}: {avg} lines")


    
    return "\n".join(lines)


def generate_org_summary_markdown(team_stats, since_date, until_date, org_name, show_arena=False, arena_top=5):
    """Generate markdown output for org-summary mode."""
    lines = []
    
    # 1. Totals Section
    total_commits = sum(d['commits'] for d in team_stats.values())
    total_added = sum(d['added'] for d in team_stats.values())
    total_deleted = sum(d['deleted'] for d in team_stats.values())
    total_changes = total_added + total_deleted
    net_growth = total_added - total_deleted
    
    all_repos = set()
    for data in team_stats.values():
        all_repos.update(data.get('repos', {}).keys())
    
    lines.append(f"# Org Summary: {org_name} ({since_date} ~ {until_date})\n")
    
    lines.append("**Totals:**")
    lines.append(f"- Active Projects: {len(all_repos)}")
    lines.append(f"- Contributors: {len(team_stats)}")
    lines.append(f"- Total Commits: {total_commits}")
    lines.append(f"- Total Changes: {total_changes} lines")
    lines.append(f"- Net Growth: {net_growth:+} lines")
    lines.append(f"- Lines Added: +{total_added}")
    lines.append(f"- Lines Deleted: -{total_deleted}")
    lines.append("")
    
    # 2. Project Breakdown
    lines.append("## 📦 Project Breakdown\n")
    lines.append("| Project | Commits | Contributors | Primary Contributor |")
    lines.append("|:--------|--------:|-------------:|:--------------------|")
    
    project_data = _calculate_project_breakdown(team_stats)
    for repo, commits, contrib_count, primary in project_data:
        primary_str = "-"
        if primary:
            primary_str = f"@{primary[0]} ({primary[1]:.0f}%)"
        lines.append(f"| {repo} | {commits} | {contrib_count} | {primary_str} |")
    lines.append("")

    # 3. Portraits (Moved here)
    # Team Portrait
    from .portrait import generate_team_portrait
    team_portrait = generate_team_portrait(team_stats)
    
    lines.append("## 🎨 Team Portrait\n")
    
    # Weekday Stats
    lines.append("### 📅 Work Week Rhythm\n")
    days_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
    sorted_days = sorted(team_portrait['weekday_stats'].items(), key=lambda x: x[1], reverse=True)
    
    if sorted_days:
        lines.append("| Weekday | Commits |")
        lines.append("|:--------|--------:|")
        for day, count in sorted_days:
            lines.append(f"| {days_map[day]} | {count} |")
        lines.append("")
    
    # Hour Stats
    lines.append("### ⏰ Peak Hours\n")
    sorted_hours = sorted(team_portrait['hour_stats'].items(), key=lambda x: x[1], reverse=True)
    
    if sorted_hours:
        lines.append("| Hour | Commits |")
        lines.append("|-----:|--------:|")
        for hour, count in sorted_hours[:5]: # Top 5 hours
            lines.append(f"| {hour:02d}:00 | {count} |")
        lines.append("")
        
    lines.append(f"- **Avg Lines/Commit:** {team_portrait['avg_lines_per_commit']:.1f}")
    lines.append("")

    # Repo Portrait
    from .portrait import generate_repo_portrait
    repo_portrait = generate_repo_portrait(team_stats, len(all_repos)) 
    
    lines.append("## 🖼️ Repo Portrait\n")
    r = repo_portrait
    
    lines.append("| Category | Repository | Metric |")
    lines.append("|:---------|:-----------|:-------|")
    
    if r['net_growth_champion'][0]:
        lines.append(f"| 🌲 Growth Champion | {r['net_growth_champion'][0]} | +{r['net_growth_champion'][1]} lines |")
        
    if r['refactor_champion'][0]:
        lines.append(f"| 🔧 Refactor Champion | {r['refactor_champion'][0]} | {r['refactor_champion'][1]} changes |")
        
    if r['slimming_champion'][0]:
        lines.append(f"| 📉 Slimming Champion | {r['slimming_champion'][0]} | {r['slimming_champion'][1]} lines |")
        
    lines.append(f"| 💤 Idle Repos | (Calculated vs Active) | {r['idle_repos_count']} repos |")
    lines.append("")
    
    # 4. Participant Breakdown
    lines.append("## 👥 Participant Breakdown\n")
    lines.append("| Contributor | Projects | Commits | Active Days |")
    lines.append("|:------------|:---------|--------:|:------------|")
    
    participant_data = _calculate_participant_breakdown(team_stats, since_date, until_date)
    for user, proj_count, commits, active_str in participant_data:
        lines.append(f"| @{user} | {proj_count} | {commits} | {active_str} |")
    lines.append("")
    
    # 4. Arena (if enabled)
    if show_arena:
        from .arena import generate_arena_rankings
        rankings = generate_arena_rankings(team_stats, since_date, until_date)
        
        # Helper for slicing: None means all
        def top_n(lst):
            return lst[:arena_top] if arena_top else lst
        
        lines.append("## 🏟️ Arena\n")
        
        # Commit Champions
        lines.append("### 🏆 Commit Champions\n")
        lines.append("| Rank | Contributor | Commits |")
        lines.append("|-----:|:------------|--------:|")
        for i, (user, count) in enumerate(top_n(rankings['commit_ranking']), 1):
            lines.append(f"| {i} | @{user} | {count} |")
        lines.append("")
        
        # Repo Hunter (New)
        lines.append("### 🐙 Repo Hunter (Project Coverage)\n")
        lines.append("| Rank | Contributor | Active Repos |")
        lines.append("|-----:|:------------|-------------:|")
        for i, (user, count) in enumerate(top_n(rankings['active_repos_ranking']), 1):
            lines.append(f"| {i} | @{user} | {count} |")
        lines.append("")
        
        # Net Growth (New)
        lines.append("### 🌲 Net Code Growth\n")
        lines.append("| Rank | Contributor | Net Growth |")
        lines.append("|-----:|:------------|-----------:|")
        for i, (user, net) in enumerate(top_n(rankings['net_growth_ranking']), 1):
            lines.append(f"| {i} | @{user} | {net:+} |")
        lines.append("")
        
        # Code Additions
        lines.append("### 📈 Code Additions\n")
        lines.append("| Rank | Contributor | Lines Added |")
        lines.append("|-----:|:------------|------------:|")
        for i, (user, added) in enumerate(top_n(rankings['additions_ranking']), 1):
            lines.append(f"| {i} | @{user} | +{added} |")
        lines.append("")
        
        # Code Deletions
        lines.append("### 📉 Code Deletions\n")
        lines.append("| Rank | Contributor | Lines Deleted |")
        lines.append("|-----:|:------------|--------------:|")
        for i, (user, deleted) in enumerate(top_n(rankings['deletions_ranking']), 1):
            lines.append(f"| {i} | @{user} | -{deleted} |")
        lines.append("")
        
        # Total Changes
        lines.append("### 📊 Total Changes\n")
        lines.append("| Rank | Contributor | Total Lines |")
        lines.append("|-----:|:------------|------------:|")
        for i, (user, changes) in enumerate(top_n(rankings['total_changes_ranking']), 1):
            lines.append(f"| {i} | @{user} | {changes} |")
        lines.append("")
        
        # Longest Streak
        if rankings['longest_streak_ranking']:
            lines.append("### 🔥 Longest Streak\n")
            lines.append("| Rank | Contributor | Days | Period |")
            lines.append("|-----:|:------------|-----:|:-------|")
            for i, (user, days, start, end) in enumerate(top_n(rankings['longest_streak_ranking']), 1):
                lines.append(f"| {i} | @{user} | {days} | {start} ~ {end} |")
            lines.append("")
            
        # Active Days (New)
        lines.append("### 📅 Most Consistent (Active Days)\n")
        lines.append("| Rank | Contributor | Days |")
        lines.append("|-----:|:------------|-----:|")
        for i, (user, days) in enumerate(top_n(rankings['active_days_ranking']), 1):
            lines.append(f"| {i} | @{user} | {days} |")
        lines.append("")
        
        # Avg Commit Size
        lines.append("### 📊 Avg Commit Size\n")
        lines.append("| Rank | Contributor | Lines/Commit |")
        lines.append("|-----:|:------------|-------------:|")
        for i, (user, avg) in enumerate(top_n(rankings['avg_commit_size_ranking']), 1):
            lines.append(f"| {i} | @{user} | {avg} |")
        lines.append("")


    
    return "\n".join(lines)

