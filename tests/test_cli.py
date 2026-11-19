import json

import pytest

from jobhunt.cli import EXIT_BLOCKED, EXIT_ERROR, EXIT_OK, EXIT_REVIEW, main


@pytest.fixture
def home(tmp_path, monkeypatch):
    path = tmp_path / "me"
    monkeypatch.setenv("JOBHUNT_HOME", str(path))
    monkeypatch.setenv("NO_COLOR", "1")
    assert main(["init"]) == EXIT_OK
    return path


def test_init_twice_needs_force(home, capsys):
    assert main(["init"]) == EXIT_ERROR
    assert "--force" in capsys.readouterr().err
    assert main(["init", "--force"]) == EXIT_OK


def test_screen_exit_codes(home, tmp_path):
    clean = tmp_path / "clean.md"
    clean.write_text("Remote. TypeScript.")
    bad = tmp_path / "bad.md"
    bad.write_text("Hybrid, 3 days in office.")
    assert main(["screen", str(clean)]) == EXIT_OK
    assert main(["screen", str(bad)]) == EXIT_BLOCKED
    assert main(["screen", str(clean), "--warn", "typescript"]) == EXIT_REVIEW


def test_screen_json(home, tmp_path, capsys):
    post = tmp_path / "p.md"
    post.write_text("Relocation to Berlin required.")
    main(["screen", str(post), "--json"])
    data = json.loads(capsys.readouterr().out)
    assert data["verdict"] == "reject"
    assert data["hits"][0]["term"] == "relocat*"


def test_lint_kind(home, tmp_path):
    note = tmp_path / "note.txt"
    note.write_text("x" * 250)
    assert main(["lint", str(note), "--kind", "linkedin_note"]) == EXIT_BLOCKED
    assert main(["lint", str(note)]) == EXIT_OK
    assert main(["lint", str(note), "--kind", "nope"]) == EXIT_ERROR


def test_track_flow(home, capsys):
    assert (
        main(["track", "add", "--company", "Acme", "--role", "Engineer", "--url", "https://x.io/1"])
        == EXIT_OK
    )
    assert main(["track", "add", "--company", "acme inc", "--role", "Other"]) == EXIT_BLOCKED
    assert main(["track", "find", "Acme"]) == EXIT_REVIEW
    assert main(["track", "find", "Globex"]) == EXIT_OK
    assert main(["track", "set", "acme-engineer", "--stage", "interviewing", "--note", "call Tue"]) == EXIT_OK
    assert main(["status"]) == EXIT_OK
    assert "Interviewing (1)" in (home / "STATUS.md").read_text()


def test_ask(home, capsys):
    assert main(["ask", "--posted", "90k-160k", "--period", "year"]) == EXIT_OK
    assert "125,000" in capsys.readouterr().out
    assert main(["ask", "--posted", "10-20", "--period", "hour"]) == EXIT_REVIEW


def test_cv_html_only(home):
    assert main(["cv", "build", "--html-only"]) == EXIT_OK
    assert list((home / "cvs").glob("*.html"))


def test_doctor_flags_example_persona(home, capsys):
    main(["doctor"])
    assert "example persona" in capsys.readouterr().out
