from __future__ import annotations

import html
import re
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

from jobhunt.pdf import html_to_pdf, page_count
from jobhunt.workspace import ConfigError, Workspace

OVERRIDABLE = ("headline", "summary", "skills", "experience")


@dataclass
class BuildResult:
    slug: str
    pdf: Path
    html: Path
    pages: int
    max_pages: int

    @property
    def ok(self) -> bool:
        return self.pages <= self.max_pages


def esc(value: str) -> str:
    return html.escape(str(value))


def merge_target(cv: dict, target: dict, slug: str) -> dict:
    bases = cv.get("bases", {})
    base_name = target.get("base")
    if not base_name:
        raise ConfigError(
            f"targets/{slug}.toml: missing `base` (one of: {', '.join(bases) or 'none defined'})."
        )
    if base_name not in bases:
        raise ConfigError(f"targets/{slug}.toml: unknown base `{base_name}`. Available: {', '.join(bases)}.")
    merged = dict(bases[base_name])
    merged.update({k: target[k] for k in OVERRIDABLE if k in target})
    missing = [k for k in OVERRIDABLE if k not in merged]
    if missing:
        raise ConfigError(f"base `{base_name}` + targets/{slug}.toml are missing: {', '.join(missing)}.")
    return merged


def experience_index(cv: dict) -> dict[str, dict]:
    return {item["id"]: item for item in cv.get("experience", [])}


def resolve_experience(cv: dict, picks: dict[str, list[str]], slug: str) -> list[tuple[dict, list[str]]]:
    index = experience_index(cv)
    out = []
    for exp_id, bullet_keys in picks.items():
        if exp_id not in index:
            raise ConfigError(f"{slug}: unknown experience id `{exp_id}`. Available: {', '.join(index)}.")
        item = index[exp_id]
        bullets = item.get("bullets", {})
        unknown = [k for k in bullet_keys if k not in bullets]
        if unknown:
            raise ConfigError(
                f"{slug}: experience `{exp_id}` has no bullet(s) {', '.join(unknown)}. "
                f"Available: {', '.join(bullets)}."
            )
        out.append((item, [bullets[k] for k in bullet_keys]))
    return out


def contact_line(person: dict) -> str:
    parts = []
    location = person.get("location")
    if location:
        tz = person.get("timezone")
        parts.append(f"{location} ({tz})" if tz else location)
    for key in ("email", "phone"):
        if person.get(key):
            parts.append(person[key])
    for url in person.get("links", {}).values():
        parts.append(re.sub(r"^https?://(www\.)?", "", url).rstrip("/"))
    return " · ".join(parts)


def load_css(ws: Workspace) -> str:
    if ws.css_override.exists():
        return ws.css_override.read_text(encoding="utf-8")
    return (resources.files("jobhunt") / "templates" / "cv.css").read_text(encoding="utf-8")


def render_html(person: dict, cv: dict, data: dict, css: str, slug: str = "cv") -> str:
    extras = cv.get("extras", {})
    parts = [
        f"<h1>{esc(person['name'])}</h1>",
        f"<div class='headline'>{esc(data['headline'])}</div>",
        f"<div class='contact'>{esc(contact_line(person))}</div>",
        f"<h2>Summary</h2><p>{esc(data['summary'])}</p>",
        "<h2>Skills</h2><div class='skills'>"
        + "".join(f"<div><b>{esc(k)}:</b> {esc(v)}</div>" for k, v in data["skills"].items())
        + "</div>",
        "<h2>Experience</h2>",
    ]
    for item, bullets in resolve_experience(cv, data["experience"], slug):
        items = "".join(f"<li>{esc(b)}</li>" for b in bullets)
        parts.append(
            "<div class='job'><div class='jobhead'>"
            f"<span>{esc(item['role'])} · {esc(item['company'])}</span>"
            f"<span class='dates'>{esc(item.get('dates', ''))}</span>"
            f"</div><ul>{items}</ul></div>"
        )
    if extras.get("earlier"):
        parts.append(f"<p class='small'>{esc(extras['earlier'])}</p>")
    tail = [extras[k] for k in ("languages", "education") if extras.get(k)]
    if tail:
        parts.append(
            "<h2>Languages & Education</h2>" + "".join(f"<p class='small'>{esc(t)}</p>" for t in tail)
        )
    title = esc(f"{person['name']} CV")
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>{title}</title><style>{css}</style></head><body>{''.join(parts)}</body></html>"
    )


def output_stem(person_name: str, slug: str, target: dict) -> str:
    who = re.sub(r"[^A-Za-z0-9]+", "_", person_name).strip("_")
    what = target.get("file") or slug
    what = re.sub(r"[^A-Za-z0-9._-]+", "_", what).strip("_")
    return f"{who}_{what}"


def build(ws: Workspace, slugs: list[str] | None = None, pdf: bool = True) -> list[BuildResult]:
    person = ws.profile()["person"]
    cv = ws.cv()
    max_pages = int(cv.get("layout", {}).get("max_pages", 1))
    css = load_css(ws)
    chosen = slugs or ws.target_slugs()
    if not chosen:
        raise ConfigError(f"No targets found in {ws.targets_dir}. Create one with `jobhunt cv new <slug>`.")
    ws.cvs_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for slug in chosen:
        target = ws.target(slug)
        data = merge_target(cv, target, slug)
        stem = output_stem(person["name"], slug, target)
        html_path = ws.cvs_dir / f"{stem}.html"
        pdf_path = ws.cvs_dir / f"{stem}.pdf"
        html_path.write_text(render_html(person, cv, data, css, slug), encoding="utf-8")
        pages = 0
        if pdf:
            html_to_pdf(html_path, pdf_path)
            pages = page_count(pdf_path)
        results.append(BuildResult(slug, pdf_path, html_path, pages, max_pages))
    return results


TARGET_TEMPLATE = """base = "{base}"
company = "{company}"
role = "{role}"
url = "{url}"

# Optional overrides. Anything left out comes from the base in cv.toml.
# headline = "Senior Full-Stack Engineer · TypeScript, React, Postgres"
# summary = "Two or three sentences aimed at this posting. Only facts from cv.toml."
# skills = {{ Languages = "TypeScript, SQL", Frontend = "React, Next.js" }}
# experience = {{ northwind = ["checkout", "perf"], bluefin = ["lead"] }}
"""


def new_target(ws: Workspace, slug: str, base: str, company: str = "", role: str = "", url: str = "") -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        raise ConfigError("Slug must be lowercase letters, digits and dashes, e.g. acme-senior-fullstack.")
    bases = ws.cv().get("bases", {})
    if base not in bases:
        raise ConfigError(f"Unknown base `{base}`. Available: {', '.join(bases)}.")
    path = ws.targets_dir / f"{slug}.toml"
    if path.exists():
        raise ConfigError(f"{path} already exists.")
    ws.targets_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(TARGET_TEMPLATE.format(base=base, company=company, role=role, url=url), encoding="utf-8")
    return path
