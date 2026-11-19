import json

import pytest

from jobhunt import fetch


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://jobs.ashbyhq.com/acme/1234-abcd/application", ("ashby", "acme", "1234-abcd")),
        ("jobs.lever.co/globex/9f8e/apply", ("lever", "globex", "9f8e")),
        ("https://job-boards.greenhouse.io/initech/jobs/555", ("greenhouse", "initech", "555")),
        ("https://boards.greenhouse.io/initech/jobs/555?gh_src=x", ("greenhouse", "initech", "555")),
        ("https://careers.example.com/jobs/1", ("web", "careers.example.com", "/jobs/1")),
    ],
)
def test_identify(url, expected):
    assert fetch.identify(url) == expected


def test_html_to_text_keeps_structure_and_drops_scripts():
    text = fetch.html_to_text(
        "<h2>Role</h2><script>x()</script><ul><li>TypeScript</li><li>Postgres</li></ul>"
    )
    assert "x()" not in text
    assert "Role" in text
    assert "- TypeScript" in text


def test_ashby_parsing(monkeypatch):
    board = {
        "jobs": [
            {
                "id": "j1",
                "title": "Senior Engineer",
                "location": "Remote",
                "isRemote": True,
                "employmentType": "FullTime",
                "descriptionPlain": "Build things.",
                "compensation": {"compensationTierSummary": "$90K – $160K"},
            }
        ]
    }
    monkeypatch.setattr(fetch, "_get", lambda url, timeout=20: json.dumps(board).encode())
    posting = fetch.fetch("https://jobs.ashbyhq.com/acme/j1")
    assert posting.title == "Senior Engineer"
    assert posting.workplace == "Remote"
    assert posting.compensation == "$90K – $160K"
    assert "Build things." in posting.to_markdown()


def test_ashby_missing_job_is_explained(monkeypatch):
    monkeypatch.setattr(fetch, "_get", lambda url, timeout=20: b'{"jobs": []}')
    with pytest.raises(fetch.FetchError, match="unlisted"):
        fetch.fetch("https://jobs.ashbyhq.com/acme/missing")


def test_lever_parsing(monkeypatch):
    job = {
        "text": "Frontend Engineer",
        "categories": {"location": "LATAM", "commitment": "Contract"},
        "descriptionPlain": "Intro.",
        "lists": [{"text": "You have", "content": "<li>React</li>"}],
        "additionalPlain": "Fully remote.",
        "salaryRange": {"min": 4000, "max": 5000, "currency": "USD", "interval": "per-month-salary"},
    }
    monkeypatch.setattr(fetch, "_get", lambda url, timeout=20: json.dumps(job).encode())
    posting = fetch.fetch("https://jobs.lever.co/globex/abc")
    assert posting.employment == "Contract"
    assert "- React" in posting.description
    assert posting.compensation.startswith("USD 4000-5000")


def test_greenhouse_unescapes_content(monkeypatch):
    job = {
        "title": "Staff Engineer",
        "location": {"name": "Remote"},
        "content": "&lt;p&gt;Hello &amp;amp; welcome&lt;/p&gt;",
    }
    monkeypatch.setattr(fetch, "_get", lambda url, timeout=20: json.dumps(job).encode())
    posting = fetch.fetch("https://job-boards.greenhouse.io/initech/jobs/1")
    assert posting.description == "Hello & welcome"
