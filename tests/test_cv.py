import pytest

from jobhunt.cv import build, contact_line, merge_target, new_target, output_stem, render_html
from jobhunt.pdf import find_chrome
from jobhunt.workspace import ConfigError


def test_scaffold_target_renders_html(ws):
    results = build(ws, pdf=False)
    html = results[0].html.read_text()
    assert "Alex Rivera" in html
    assert "rebuilt checkout" in html.lower()
    assert "<script" not in html


def test_target_overrides_base(ws):
    target = ws.target("example-acme-senior-fullstack")
    merged = merge_target(ws.cv(), target, "x")
    assert merged["headline"].startswith("Senior Full-Stack Engineer · Next.js")
    assert merged["skills"] == ws.cv()["bases"]["fullstack"]["skills"]


def test_unknown_bullet_is_a_clear_error(ws):
    cv = ws.cv()
    data = dict(cv["bases"]["fullstack"], experience={"northwind": ["does-not-exist"]})
    with pytest.raises(ConfigError, match="Available"):
        render_html(ws.profile()["person"], cv, data, "", "t")


def test_unknown_base_is_a_clear_error(ws):
    with pytest.raises(ConfigError, match="Available"):
        merge_target(ws.cv(), {"base": "nope"}, "t")


def test_html_is_escaped(ws):
    person = dict(ws.profile()["person"], name="<b>X</b>")
    html = render_html(person, ws.cv(), ws.cv()["bases"]["ai"], "", "t")
    assert "&lt;b&gt;X&lt;/b&gt;" in html


def test_contact_line_strips_scheme():
    line = contact_line(
        {"location": "Lisbon", "timezone": "UTC", "links": {"gh": "https://www.github.com/x/"}}
    )
    assert line == "Lisbon (UTC) · github.com/x"


def test_output_stem_is_filesystem_safe():
    assert output_stem("Ana María Ñ", "acme", {"file": "Acme / Senior"}) == "Ana_Mar_a_Acme_Senior"


def test_new_target_validates(ws):
    path = new_target(ws, "globex-frontend", "frontend", "Globex", "Frontend", "https://x")
    assert 'base = "frontend"' in path.read_text()
    with pytest.raises(ConfigError):
        new_target(ws, "Bad Slug", "frontend")
    with pytest.raises(ConfigError):
        new_target(ws, "ok-slug", "nope")


@pytest.mark.skipif(not find_chrome(), reason="no Chrome/Chromium available")
def test_pdf_is_one_page(ws):
    result = build(ws)[0]
    assert result.pdf.exists()
    assert result.pages == 1
    assert result.ok
