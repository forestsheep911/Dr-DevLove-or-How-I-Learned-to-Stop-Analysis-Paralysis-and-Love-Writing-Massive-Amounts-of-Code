from datetime import date
from src.gh_stats.exporter import generate_markdown

def test_generate_markdown_simple():
    stats = {
        'owner/repo-a': {
            'messages': [
                {'date': date(2023, 1, 1), 'message': 'Initial commit'},
                {'date': date(2023, 1, 2), 'message': 'Fix bug\n\nMore details'}
            ]
        },
        'owner/repo-b': {
            'messages': [
                {'date': date(2023, 1, 1), 'message': 'Update readme'}
            ]
        }
    }
    
    md = generate_markdown(stats, date(2023, 1, 1), date(2023, 1, 31))
    
    assert "# GitHub Activity Report" in md
    assert "## owner/repo-a" in md
    assert "- [2023-01-01] Initial commit" in md
    assert "- [2023-01-02] Fix bug" in md  # Should check it uses first line only
    assert "## owner/repo-b" in md
    
def test_generate_markdown_empty():
    stats = {}
    md = generate_markdown(stats, date(2023, 1, 1), date(2023, 1, 1))
    assert "# GitHub Activity Report" in md
    assert "##" not in md
