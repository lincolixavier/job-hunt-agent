from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Issue:
    kind: str
    message: str
    line: int = 0
    col: int = 0

    def __str__(self) -> str:
        where = f"{self.line}:{self.col} " if self.line else ""
        return f"{where}[{self.kind}] {self.message}"


def _positions(text: str, pattern: re.Pattern):
    for m in pattern.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        col = m.start() - (text.rfind("\n", 0, m.start()) + 1) + 1
        yield m, line, col


def lint(
    text: str,
    banned_chars: list[str] | None = None,
    banned_phrases: list[str] | None = None,
    max_chars: int | None = None,
) -> list[Issue]:
    issues: list[Issue] = []
    for ch in banned_chars or []:
        for _, line, col in _positions(text, re.compile(re.escape(ch))):
            issues.append(Issue("char", f"banned character {ch!r} (U+{ord(ch[0]):04X})", line, col))
    for phrase in banned_phrases or []:
        pattern = re.compile(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", re.IGNORECASE)
        for m, line, col in _positions(text, pattern):
            issues.append(Issue("phrase", f"banned phrase {m.group(0)!r}", line, col))
    if max_chars is not None:
        length = len(text.strip())
        if length > max_chars:
            issues.append(
                Issue("length", f"{length} characters, limit is {max_chars} ({length - max_chars} over)")
            )
    return issues


def rules_from_profile(profile: dict, kind: str | None = None) -> dict:
    writing = profile.get("writing", {})
    limits = writing.get("limits", {})
    if kind and kind not in limits:
        raise KeyError(
            f"Unknown text kind `{kind}`. Defined in [writing.limits]: {', '.join(limits) or 'none'}."
        )
    return {
        "banned_chars": list(writing.get("banned_chars", [])),
        "banned_phrases": list(writing.get("banned_phrases", [])),
        "max_chars": limits.get(kind) if kind else None,
    }
