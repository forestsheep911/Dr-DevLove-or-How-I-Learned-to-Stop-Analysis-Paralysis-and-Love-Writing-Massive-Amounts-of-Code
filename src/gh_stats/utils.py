import datetime
import re

def parse_relative_date(date_str):
    """
    Parse relative dates like 'today-2days', 'now-1week', '3days'.
    Returns a datetime.date object.
    """
    today = datetime.date.today()
    if date_str == 'today' or date_str == 'now':
        return today
    
    # YYYYMMDD format (new)
    compact_match = re.match(r'^(\d{4})(\d{2})(\d{2})$', date_str)
    if compact_match:
        return datetime.date(int(compact_match.group(1)), int(compact_match.group(2)), int(compact_match.group(3)))

    # Simple N[days|weeks|months|years] (e.g. "3days" -> 3 days ago)
    simple_match = re.match(r'^(\d+)(day|week|month|year)s?$', date_str)
    if simple_match:
        num = int(simple_match.group(1))
        unit = simple_match.group(2)
        if unit == 'day': delta = datetime.timedelta(days=num)
        elif unit == 'week': delta = datetime.timedelta(weeks=num)
        elif unit == 'month': delta = datetime.timedelta(days=num*30) # approx
        elif unit == 'year': delta = datetime.timedelta(days=num*365) # approx
        return today - delta

    # yt-dlp style: (today|now)-N[unit]
    match = re.match(r'^(today|now)([-+])(\d+)(day|week|month|year)s?$', date_str)
    if match:
        op = match.group(2)
        num = int(match.group(3))
        unit = match.group(4)
        
        if unit == 'day': delta = datetime.timedelta(days=num)
        elif unit == 'week': delta = datetime.timedelta(weeks=num)
        elif unit == 'month': delta = datetime.timedelta(days=num*30)
        elif unit == 'year': delta = datetime.timedelta(days=num*365)
        
        if op == '-': return today - delta
        else: return today + delta
        
    raise ValueError(f"Unknown date format: {date_str}")

def parse_date_range(range_str):
    today = datetime.date.today()
    
    # 今天
    if range_str == 'today':
        return today, today
    
    # 昨天
    elif range_str == 'yesterday':
        yesterday = today - datetime.timedelta(days=1)
        return yesterday, yesterday
    
    # 本周（从周一到今天）
    elif range_str in ['thisweek', 'week']:
        start = today - datetime.timedelta(days=today.weekday())
        return start, today
    
    # 上周（上周一到上周日）
    elif range_str == 'lastweek':
        last_monday = today - datetime.timedelta(days=today.weekday() + 7)
        last_sunday = last_monday + datetime.timedelta(days=6)
        return last_monday, last_sunday
    
    # 本月（从本月1号到今天）
    elif range_str in ['thismonth', 'month']:
        return today.replace(day=1), today
    
    # 上月（上月1号到上月最后一天）
    elif range_str == 'lastmonth':
        first_of_this_month = today.replace(day=1)
        last_day_of_last_month = first_of_this_month - datetime.timedelta(days=1)
        first_of_last_month = last_day_of_last_month.replace(day=1)
        return first_of_last_month, last_day_of_last_month
    
    # 季度
    elif range_str == 'quarter':
        quarter_month = ((today.month - 1) // 3) * 3 + 1
        return today.replace(month=quarter_month, day=1), today
    
    # 本年（从1月1日到今天）
    elif range_str in ['thisyear', 'year']:
        return today.replace(month=1, day=1), today
    
    # 去年（去年1月1日到去年12月31日）
    elif range_str == 'lastyear':
        last_year = today.year - 1
        return datetime.date(last_year, 1, 1), datetime.date(last_year, 12, 31)
    
    # Try parsing as relative date (e.g. "3days")
    try:
        start = parse_relative_date(range_str)
        return start, today
    except ValueError:
        pass
        
    raise ValueError(f"Unknown range: {range_str}")
