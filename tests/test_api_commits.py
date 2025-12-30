import datetime
from datetime import date, timezone, timedelta
from unittest.mock import MagicMock
import pytest
from gh_stats.api import get_repo_commits

@pytest.fixture
def mock_run_cmd(mocker):
    return mocker.patch('gh_stats.api.run_gh_cmd')

def test_get_repo_commits_timezone_conversion(mock_run_cmd, mocker):
    """
    Verify that local dates are correctly converted to UTC ISO strings 
    based on system timezone.
    For this test, we force the system timezone to be UTC+8 (Asia/Shanghai).
    """
    
    # Mock datetime.datetime to control "now" and "astimezone"
    # This is tricky because datetime is a built-in type. 
    # Instead of mocking the class, we can mock the timezone logic inside the function if we refactor,
    # or we can rely on what the function uses: `datetime.datetime.now().astimezone().tzinfo`
    
    # Let's craft a fake timezone class
    class FakeTimezone(datetime.tzinfo):
        def utcoffset(self, dt):
            return timedelta(hours=8)
        def dst(self, dt):
            return timedelta(0)
        def tzname(self, dt):
            return "Fake+8"

    fake_tz = FakeTimezone()

    # We need to patch where `get_repo_commits` gets its local_tz.
    # It calls: local_tz = datetime.datetime.now().astimezone().tzinfo
    # We will patch `datetime.datetime` class within the module `gh_stats.api`
    
    # Since patching built-in datetime is hard, we'll assume the code uses `datetime.datetime`
    # A cleaner way usually is to wrap "get_local_tz" in a helper, but let's try patching first.
    
    # We will intercept the `datetime.datetime.now` call inside the module? 
    # No, it calls `datetime.datetime.now().astimezone().tzinfo`.
    
    # Easier strategy: Patch the `datetime` module imported in `gh_stats.api`.
    # BUT, `gh_stats.api` does `import datetime`.
    
    # Let's try to mock the `run_gh_cmd` and inspect the arguments it received.
    # We can infer the timezone conversion from the arguments.
    
    # However, to Deterministically test it, we must control the timezone.
    # Attempting to mock `datetime` in the target module.
    
    mock_dt = mocker.patch('gh_stats.api.datetime')
    # Restore the real datetime classes we need
    mock_dt.date = datetime.date
    mock_dt.time = datetime.time
    mock_dt.timedelta = datetime.timedelta
    mock_dt.timezone = datetime.timezone
    
    # Mock datetime.datetime
    # We need a real datetime class that has our mocked method
    class MockDatetime(datetime.datetime):
        @classmethod
        def now(cls):
            # Return a naive time that when astimezone() is called, returns our fake tz
            dt = datetime.datetime(2023, 1, 1, 12, 0, 0)
            # We mock the return value of astimezone() on this instance
            mock_inst = MagicMock(wraps=dt)
            
            # Setup the chain: .astimezone() -> object with .tzinfo
            mock_tz_container = MagicMock()
            mock_tz_container.tzinfo = fake_tz
            
            # When astimezone() is called (with no args), return the container that holds our tz
            mock_inst.astimezone.return_value = mock_tz_container
            return mock_inst

        # We also need combine to work as expected
        @classmethod
        def combine(cls, date, time, tzinfo=None):
            return datetime.datetime.combine(date, time, tzinfo=tzinfo)

    mock_dt.datetime = MockDatetime
    
    # Setup the return for run_gh_cmd so loop terminates
    mock_run_cmd.return_value = []
    
    # Execute
    input_since = date(2024, 1, 1)
    input_until = date(2024, 1, 1)
    
    get_repo_commits(
        repo_full_name="user/repo", 
        author="user", 
        since_date=input_since, 
        until_date=input_until
    )
    
    # Assert
    # Access the arguments passed to run_gh_cmd
    # call_args is (args, kwargs)
    # args[0] is the command list: ['api', 'repos/...?since=...&until=...']
    
    assert mock_run_cmd.called
    cmd_args = mock_run_cmd.call_args[0][0]
    api_url = cmd_args[1]
    
    # Extract since and until from URL
    # format: since=YYYY-MM-DDTHH:MM:SZ
    import re
    since_match = re.search(r'since=([^&]+)', api_url).group(1)
    until_match = re.search(r'until=([^&]+)', api_url).group(1)
    
    # Logic verification:
    # Local: 2024-01-01 00:00:00 (UTC+8) -> Reference Point
    # UTC:   2023-12-31 16:00:00Z
    
    # Local: 2024-01-01 23:59:59.999 (UTC+8)
    # UTC:   2024-01-01 15:59:59Z
    
    assert since_match == "2023-12-31T16:00:00Z"
    # Precision might vary, usually until is set to max time.
    # 23:59:59 in UTC+8 is 15:59:59 in UTC.
    assert until_match.startswith("2024-01-01T15:59:59")

def test_get_repo_commits_query_construction(mock_run_cmd):
    """
    Verify the query parameters are constructed correctly (author, page, per_page).
    """
    mock_run_cmd.return_value = [] # Return empty to stop loop
    
    get_repo_commits("user/repo", "dev_user", date(2024,1,1), date(2024,1,1))
    
    cmd_args = mock_run_cmd.call_args[0][0]
    url = cmd_args[1]
    
    assert "repos/user/repo/commits" in url
    assert "author=dev_user" in url
    assert "per_page=100" in url
    assert "page=1" in url
