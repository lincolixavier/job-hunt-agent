from __future__ import annotations

import html
import json
import re
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from urllib.parse import urlparse

from jobhunt import __version__

USER_AGENT = f"jobhunt/{__version__} (+https://github.com/lincolixavier/job-hunt-agent)"
BLOCK_TAGS = {
    "p",
    "div",
    "br",
    "li",
    "ul",
    "ol",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "tr",
    "section",
    "article",
}
SKIP_TAGS = {"script", "style", "noscript", "svg", "head"}


class FetchError(Exception):
    pass


@dataclass
class Posting:
    url: str
    source: str
    company: str = ""
    title: str = ""
    location: str = ""
    workplace: str = ""
    employment: str = ""
    compensation: str = ""
    description: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def to_markdown(self) -> str:
        meta = [
            ("Company", self.company),
            ("Location", self.location),
            ("Workplace", self.workplace),
            ("Employment", self.employment),
            ("Compensation", self.compensation),
            ("Source", f"{self.source} · {self.url}"),
        ]
        lines = [f"# {self.title or 'Untitled posting'}", ""]
        lines += [f"- **{k}:** {v}" for k, v in meta if v]
        lines += ["", self.description.strip(), ""]
        return "\n".join(lines)


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.chunks: list[str] = []
        self.skip = 0
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        if tag in SKIP_TAGS:
            self.skip += 1
        if tag in BLOCK_TAGS:
            self.chunks.append("\n")
        if tag == "li":
            self.chunks.append("- ")

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in SKIP_TAGS and self.skip:
            self.skip -= 1
        if tag in BLOCK_TAGS:
            self.chunks.append("\n")

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if not self.skip:
            self.chunks.append(data)


def html_to_text(markup: str) -> str:
    parser = _TextExtractor()
    parser.feed(markup)
    text = "".join(parser.chunks)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def identify(url: str) -> tuple[str, str, str]:
    parsed = urlparse(url if "://" in url else f"https://{url}")
    host = parsed.netloc.lower()
    parts = [p for p in parsed.path.split("/") if p]
    if host == "jobs.ashbyhq.com" and len(parts) >= 2:
        return "ashby", parts[0], parts[1]
    if host in {"jobs.lever.co", "jobs.eu.lever.co"} and len(parts) >= 2:
        return "lever", parts[0], parts[1]
    if host.endswith("greenhouse.io") and "jobs" in parts:
        idx = parts.index("jobs")
        if idx >= 1 and idx + 1 < len(parts):
            return "greenhouse", parts[idx - 1], parts[idx + 1]
    return "web", host, parsed.path


def _get(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        raise FetchError(f"HTTP {exc.code} for {url}") from None
    except urllib.error.URLError as exc:
        raise FetchError(f"Could not reach {url}: {exc.reason}") from None


def _json(url: str) -> dict | list:
    try:
        return json.loads(_get(url))
    except json.JSONDecodeError:
        raise FetchError(f"Expected JSON from {url}") from None


def from_ashby(url: str, org: str, job_id: str) -> Posting:
    board = _json(f"https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=true")
    job = next((j for j in board.get("jobs", []) if j.get("id") == job_id), None)
    if not job:
        raise FetchError(
            f"Ashby board `{org}` has no public job {job_id} (closed or unlisted). Open it in a browser."
        )
    comp = (job.get("compensation") or {}).get("compensationTierSummary") or ""
    return Posting(
        url=url,
        source="ashby",
        company=org,
        title=job.get("title", ""),
        location=job.get("location", ""),
        workplace=job.get("workplaceType") or ("Remote" if job.get("isRemote") else ""),
        employment=job.get("employmentType", ""),
        compensation=comp,
        description=job.get("descriptionPlain") or html_to_text(job.get("descriptionHtml", "")),
    )


def from_lever(url: str, org: str, job_id: str) -> Posting:
    job = _json(f"https://api.lever.co/v0/postings/{org}/{job_id}?mode=json")
    cats = job.get("categories", {})
    sections = [job.get("descriptionPlain", "")]
    for block in job.get("lists", []):
        sections.append(f"{block.get('text', '')}\n{html_to_text(block.get('content', ''))}")
    sections.append(job.get("additionalPlain", ""))
    salary = job.get("salaryRange") or {}
    comp = ""
    if salary.get("min"):
        comp = f"{salary.get('currency', '')} {salary['min']}-{salary.get('max', '')} {salary.get('interval', '')}"
    return Posting(
        url=url,
        source="lever",
        company=org,
        title=job.get("text", ""),
        location=cats.get("location", ""),
        workplace=job.get("workplaceType", ""),
        employment=cats.get("commitment", ""),
        compensation=comp.strip(),
        description="\n\n".join(s.strip() for s in sections if s and s.strip()),
    )


def from_greenhouse(url: str, org: str, job_id: str) -> Posting:
    job = _json(f"https://boards-api.greenhouse.io/v1/boards/{org}/jobs/{job_id}")
    return Posting(
        url=url,
        source="greenhouse",
        company=org,
        title=job.get("title", ""),
        location=(job.get("location") or {}).get("name", ""),
        description=html_to_text(html.unescape(job.get("content", ""))),
    )


def from_web(url: str) -> Posting:
    raw = _get(url).decode("utf-8", errors="ignore")
    parser = _TextExtractor()
    parser.feed(raw)
    text = html_to_text(raw)
    if len(text) < 300:
        raise FetchError("Page has almost no text without JavaScript. Open it in a browser instead.")
    return Posting(url=url, source="web", title=parser.title.strip(), description=text)


def fetch(url: str) -> Posting:
    source, org, job_id = identify(url)
    if source == "ashby":
        return from_ashby(url, org, job_id)
    if source == "lever":
        return from_lever(url, org, job_id)
    if source == "greenhouse":
        return from_greenhouse(url, org, job_id)
    return from_web(url)
