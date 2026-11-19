from __future__ import annotations

import re
from dataclasses import dataclass, field

PASS, REVIEW, REJECT = "pass", "review", "reject"


@dataclass
class Hit:
    term: str
    kind: str
    snippets: list[str] = field(default_factory=list)


@dataclass
class Result:
    verdict: str
    hits: list[Hit]

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "hits": [{"term": h.term, "kind": h.kind, "snippets": h.snippets} for h in self.hits],
        }


def compile_term(term: str) -> re.Pattern:
    stem = term.endswith("*")
    core = term.rstrip("*").strip()
    words = [re.escape(w) for w in re.split(r"[\s\-]+", core) if w]
    body = r"[\s\-]*".join(words)
    prefix = r"\b" if core[:1].isalnum() else ""
    suffix = "" if stem or not core[-1:].isalnum() else r"\b"
    return re.compile(prefix + body + suffix, re.IGNORECASE)


def snippet(text: str, start: int, end: int, radius: int = 70) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    chunk = text[left:right].replace("\n", " ")
    return f"{'…' if left else ''}{chunk.strip()}{'…' if right < len(text) else ''}"


NEGATION = re.compile(r"\b(no|not|non|without|never|zero|nor|free of)\b[\w\s,/-]{0,20}$", re.IGNORECASE)


def negated(text: str, start: int) -> bool:
    return bool(NEGATION.search(text[max(0, start - 30) : start]))


def find(text: str, terms: list[str], kind: str, limit: int = 3) -> list[Hit]:
    hits = []
    for term in terms:
        matches = list(compile_term(term).finditer(text))
        if not matches:
            continue
        plain = [m for m in matches if not negated(text, m.start())]
        if kind == REJECT and not plain:
            hits.append(
                Hit(
                    f"{term} (negated, confirm)",
                    REVIEW,
                    [snippet(text, m.start(), m.end()) for m in matches[:limit]],
                )
            )
        else:
            hits.append(
                Hit(term, kind, [snippet(text, m.start(), m.end()) for m in (plain or matches)[:limit]])
            )
    return hits


def screen(text: str, reject: list[str], warn: list[str]) -> Result:
    hits = find(text, reject, REJECT) + find(text, warn, REVIEW)
    kinds = {h.kind for h in hits}
    verdict = REJECT if REJECT in kinds else REVIEW if REVIEW in kinds else PASS
    return Result(verdict, sorted(hits, key=lambda h: h.kind != REJECT))


def rules_from_profile(profile: dict) -> tuple[list[str], list[str]]:
    rules = profile.get("screen", {})
    return list(rules.get("reject", [])), list(rules.get("warn", []))
