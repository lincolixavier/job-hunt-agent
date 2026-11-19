from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

FIELDS = [
    "id",
    "company",
    "role",
    "url",
    "portal",
    "stage",
    "applied_on",
    "salary_ask",
    "cv",
    "notes",
    "updated",
]
STAGES = ["found", "pending", "applied", "interviewing", "offer", "rejected", "skipped", "withdrawn"]
ACTIVE = {"found", "pending", "applied", "interviewing", "offer"}
COMPANY_SUFFIXES = r"\b(inc|llc|ltd|ltda|gmbh|s\.?a|corp|co|labs?|technologies|tech|group|hq)\b\.?"


class TrackerError(Exception):
    pass


class DuplicateError(TrackerError):
    def __init__(self, message: str, existing: dict):
        super().__init__(message)
        self.existing = existing


def today() -> str:
    return date.today().isoformat()


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "item"


def company_key(name: str) -> str:
    raw = re.sub(r"[^a-z0-9]", "", name.lower())
    key = re.sub(r"[^a-z0-9]", "", re.sub(COMPANY_SUFFIXES, "", name.lower()))
    return key or raw


def url_key(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url if "://" in url else f"https://{url}")
    path = re.sub(r"/(apply|application|applications/new)/?$", "", parsed.path.rstrip("/"))
    return f"{parsed.netloc.lower().removeprefix('www.')}{path.lower()}"


@dataclass
class Tracker:
    path: Path

    def load(self) -> list[dict]:
        if not self.path.exists():
            return []
        with self.path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        return [{f: row.get(f, "") or "" for f in FIELDS} for row in rows]

    def save(self, rows: list[dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        tmp.replace(self.path)

    def find(self, query: str) -> list[dict]:
        rows = self.load()
        q = query.strip()
        qkey = company_key(q)
        ukey = url_key(q) if ("/" in q or "." in q) else ""

        def matches(row: dict) -> bool:
            if ukey and url_key(row["url"]) == ukey:
                return True
            if qkey and qkey in company_key(row["company"]):
                return True
            return q.lower() in row["role"].lower() or q.lower() == row["id"]

        return [row for row in rows if matches(row)]

    def get(self, row_id: str) -> dict:
        for row in self.load():
            if row["id"] == row_id:
                return row
        raise TrackerError(f"No entry with id {row_id!r}. Try `jobhunt track find <company>`.")

    def add(
        self,
        company: str,
        role: str,
        url: str = "",
        stage: str = "applied",
        portal: str = "",
        salary_ask: str = "",
        cv: str = "",
        note: str = "",
        one_per_company: bool = True,
        force: bool = False,
        on: str | None = None,
    ) -> dict:
        check_stage(stage)
        rows = self.load()
        when = on or today()
        if url:
            same_url = [r for r in rows if url_key(r["url"]) == url_key(url)]
            if same_url:
                raise DuplicateError(
                    f"Already tracked: {same_url[0]['id']} ({same_url[0]['stage']}).", same_url[0]
                )
        if one_per_company and not force:
            ck = company_key(company)
            same_co = [r for r in rows if company_key(r["company"]) == ck and r["stage"] not in {"skipped"}]
            if same_co:
                r = same_co[0]
                raise DuplicateError(
                    f"{company} already has {r['id']} ({r['stage']}). One role per company; pass --force to override.",
                    r,
                )
        base = slugify(f"{company}-{role}")
        ids = {r["id"] for r in rows}
        row_id, n = base, 2
        while row_id in ids:
            row_id, n = f"{base}-{n}", n + 1
        row = {
            "id": row_id,
            "company": company,
            "role": role,
            "url": url,
            "portal": portal,
            "stage": stage,
            "applied_on": when if stage in {"applied", "interviewing", "offer"} else "",
            "salary_ask": salary_ask,
            "cv": cv,
            "notes": f"{when}: {note}" if note else "",
            "updated": when,
        }
        rows.append(row)
        self.save(rows)
        return row

    def update(
        self,
        row_id: str,
        stage: str | None = None,
        note: str | None = None,
        on: str | None = None,
        **fields: str,
    ) -> dict:
        rows = self.load()
        when = on or today()
        for row in rows:
            if row["id"] != row_id:
                continue
            if stage:
                check_stage(stage)
                if stage in {"applied", "interviewing", "offer"} and not row["applied_on"]:
                    row["applied_on"] = when
                row["stage"] = stage
            for key, value in fields.items():
                if value is not None and key in FIELDS and key not in {"id", "notes", "updated"}:
                    row[key] = value
            if note:
                row["notes"] = f"{row['notes']} | {when}: {note}" if row["notes"] else f"{when}: {note}"
            row["updated"] = when
            self.save(rows)
            return row
        raise TrackerError(f"No entry with id {row_id!r}.")


def check_stage(stage: str) -> None:
    if stage not in STAGES:
        raise TrackerError(f"Unknown stage {stage!r}. Use one of: {', '.join(STAGES)}.")


def days_since(iso: str, ref: date | None = None) -> int | None:
    try:
        return ((ref or date.today()) - date.fromisoformat(iso)).days
    except ValueError:
        return None


def last_note(notes: str) -> str:
    return notes.split(" | ")[-1] if notes else ""


def _link(row: dict) -> str:
    label = f"{row['company']}, {row['role']}"
    return f"[{label}]({row['url']})" if row["url"] else label


def _table(rows: list[dict], cols: list[tuple[str, callable]]) -> list[str]:
    head = "| " + " | ".join(c for c, _ in cols) + " |"
    sep = "|" + "---|" * len(cols)
    body = ["| " + " | ".join(str(fn(r)).replace("|", "/") for _, fn in cols) + " |" for r in rows]
    return [head, sep, *body]


def render_status(rows: list[dict], stale_days: int = 21, ref: date | None = None) -> str:
    by_stage: dict[str, list[dict]] = {s: [] for s in STAGES}
    for row in rows:
        by_stage.setdefault(row["stage"], []).append(row)
    for group in by_stage.values():
        group.sort(key=lambda r: r["updated"], reverse=True)

    applied = by_stage["applied"]
    stale = [r for r in applied if (days_since(r["updated"], ref) or 0) >= stale_days]
    counts = ", ".join(f"{s} {len(by_stage[s])}" for s in STAGES if by_stage[s])
    out = [
        "# Job hunt status",
        "",
        f"Updated {(ref or date.today()).isoformat()}. {len(rows)} tracked: {counts or 'nothing yet'}.",
        "",
        "Generated by `jobhunt status` from tracker.csv. Edit the tracker, not this file.",
    ]

    sections = [
        ("Offers", by_stage["offer"]),
        ("Interviewing", by_stage["interviewing"]),
        ("Needs you", by_stage["pending"]),
    ]
    for title, group in sections:
        if group:
            out += ["", f"## {title} ({len(group)})", ""]
            out += _table(
                group,
                [
                    ("Role", _link),
                    ("Latest", lambda r: last_note(r["notes"])),
                    ("Updated", lambda r: r["updated"]),
                ],
            )

    if applied:
        out += ["", f"## Applied, waiting ({len(applied)})", ""]
        if stale:
            out += [
                f"{len(stale)} without news for {stale_days}+ days. Consider a follow-up or closing them.",
                "",
            ]
        out += _table(
            applied,
            [
                ("Role", _link),
                ("Applied", lambda r: r["applied_on"]),
                ("Portal", lambda r: r["portal"]),
                ("Ask", lambda r: r["salary_ask"]),
            ],
        )

    if by_stage["found"]:
        out += ["", f"## Found, not applied ({len(by_stage['found'])})", ""]
        out += _table(by_stage["found"], [("Role", _link), ("Notes", lambda r: last_note(r["notes"]))])

    closed = by_stage["rejected"] + by_stage["withdrawn"]
    if closed:
        out += ["", f"## Closed ({len(closed)})", ""]
        out.append(", ".join(f"{r['company']} ({r['stage']}, {r['updated']})" for r in closed) + ".")

    if by_stage["skipped"]:
        out += ["", f"## Skipped ({len(by_stage['skipped'])})", ""]
        out += [
            f"- {r['company']}, {r['role']}: {last_note(r['notes']) or 'no reason logged'}"
            for r in by_stage["skipped"]
        ]

    return "\n".join(out) + "\n"
