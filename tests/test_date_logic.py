import pytest
import datetime
from datetime import date, timedelta
from gh_stats.date_parser import parse_relative_date, parse_date_range

# Helper to freeze time would be nice, but for now we'll calculate relative to today
# or mock datetime.date.today if we want to be precise. 
# For simple relative tests, we can just assert the delta.

def test_parse_relative_date_keywords():
    today = date.today()
    assert parse_relative_date("today") == today
    assert parse_relative_date("now") == today

def test_parse_relative_date_compact():
    assert parse_relative_date("20230101") == date(2023, 1, 1)

def test_parse_relative_date_last_n():
    today = date.today()
    
    # last3days = today - 3 days
    assert parse_relative_date("last3days") == today - timedelta(days=3)
    
    # last1week = today - 1 week
    assert parse_relative_date("last1week") == today - timedelta(weeks=1)
    
    # last1month approx 30 days
    assert parse_relative_date("last1month") == today - timedelta(days=30)

def test_parse_relative_date_ytdlp_style():
    today = date.today()
    
    # today-2days
    assert parse_relative_date("today-2days") == today - timedelta(days=2)
    
    # now+1week
    assert parse_relative_date("now+1week") == today + timedelta(weeks=1)

def test_parse_relative_date_invalid():
    with pytest.raises(ValueError, match="Unknown date format"):
        parse_relative_date("invalid-date")

def test_parse_date_range_keywords():
    today = date.today()
    
    # today
    assert parse_date_range("today") == (today, today)
    
    # yesterday
    yesterday = today - timedelta(days=1)
    assert parse_date_range("yesterday") == (yesterday, yesterday)

def test_parse_date_range_thisweek():
    today = date.today()
    start, end = parse_date_range("thisweek")
    assert end == today
    # Start should be Monday of this week
    assert start.weekday() == 0 
    assert (today - start).days < 7

def test_parse_date_range_lastweek():
    today = date.today()
    start, end = parse_date_range("lastweek")
    # Last week Monday to Sunday
    assert start.weekday() == 0
    assert end.weekday() == 6
    assert (end - start).days == 6
    # End should be before this week's start (roughly)
    # Just checking it's in the past
    assert end < today

def test_parse_date_range_thismonth():
    today = date.today()
    start, end = parse_date_range("thismonth")
    assert end == today
    assert start.day == 1
    assert start.month == today.month

def test_parse_date_range_lastmonth():
    today = date.today()
    start, end = parse_date_range("lastmonth")
    
    # Last day of last month
    first_of_this = today.replace(day=1)
    expected_end = first_of_this - timedelta(days=1)
    expected_start = expected_end.replace(day=1)
    
    assert start == expected_start
    assert end == expected_end

def test_parse_date_range_fallthrough_relative():
    # If not a keyword, it tries parse_relative_date for start, and today for end
    today = date.today()
    start, end = parse_date_range("last3days") # returns start=today-3days, end=today
    
    assert end == today
    assert start == today - timedelta(days=3)

def test_parse_date_range_invalid():
    with pytest.raises(ValueError):
        parse_date_range("not-a-range")
