from datetime import date

import pytest

from jobhunt.tracker import DuplicateError, Tracker, TrackerError, company_key, render_status, url_key


def test_company_key_ignores_suffixes_and_case():
    assert company_key("Acme Inc.") == company_key("ACME") == "acme"
    assert company_key("Tech") == "tech"


def test_url_key_ignores_apply_suffix_and_www():
    assert url_key("https://jobs.lever.co/acme/1/apply") == url_key("jobs.lever.co/acme/1")
    assert url_key("https://www.example.com/jobs/1/") == url_key("https://example.com/jobs/1")


def test_add_blocks_same_url(tmp_path):
    t = Tracker(tmp_path / "t.csv")
    t.add("Acme", "Engineer", url="https://jobs.ashbyhq.com/acme/1")
    with pytest.raises(DuplicateError):
        t.add("Other", "Engineer", url="https://jobs.ashbyhq.com/acme/1/application", force=True)


def test_one_per_company_unless_forced_or_skipped(tmp_path):
    t = Tracker(tmp_path / "t.csv")
    t.add("Acme Inc", "Engineer")
    with pytest.raises(DuplicateError):
        t.add("ACME", "Staff Engineer")
    assert t.add("ACME", "Staff Engineer", force=True)["id"] == "acme-staff-engineer"
    t.add("Beta", "Engineer", stage="skipped")
    assert t.add("Beta", "Frontend")["stage"] == "applied"


def test_update_appends_dated_notes_and_sets_applied_on(tmp_path):
    t = Tracker(tmp_path / "t.csv")
    row = t.add("Acme", "Engineer", stage="found", on="2026-01-01")
    assert row["applied_on"] == ""
    t.update(row["id"], stage="applied", note="sent", on="2026-01-02")
    row = t.update(row["id"], note="recruiter replied", on="2026-01-05")
    assert row["applied_on"] == "2026-01-02"
    assert row["notes"] == "2026-01-02: sent | 2026-01-05: recruiter replied"
    with pytest.raises(TrackerError):
        t.update(row["id"], stage="ghosted")


def test_find_by_company_role_and_url(tmp_path):
    t = Tracker(tmp_path / "t.csv")
    t.add("Acme", "Platform Engineer", url="https://jobs.lever.co/acme/9")
    assert len(t.find("acme")) == 1
    assert len(t.find("platform")) == 1
    assert len(t.find("https://jobs.lever.co/acme/9/apply")) == 1
    assert t.find("globex") == []


def test_ids_are_unique(tmp_path):
    t = Tracker(tmp_path / "t.csv")
    a = t.add("Acme", "Engineer", force=True)
    b = t.add("Acme", "Engineer", force=True)
    assert a["id"] != b["id"]


def test_status_groups_and_flags_stale(tmp_path):
    t = Tracker(tmp_path / "t.csv")
    t.add("Old", "Engineer", on="2026-01-01")
    t.add("Fresh", "Engineer", on="2026-02-01")
    t.add("Need", "Engineer", stage="pending", note="record a Loom")
    t.add("Gone", "Engineer", stage="rejected")
    text = render_status(t.load(), stale_days=21, ref=date(2026, 2, 5))
    assert "## Needs you (1)" in text
    assert "## Applied, waiting (2)" in text
    assert "1 without news for 21+ days" in text
    assert "Gone (rejected" in text
