from __future__ import annotations

import re
from dataclasses import dataclass

PER_MONTH = {"hour": 160.0, "day": 20.0, "month": 1.0, "year": 1 / 12}
POLICIES = ("midpoint", "max", "target")


class SalaryError(ValueError):
    pass


@dataclass
class Ask:
    amount: float
    period: str
    currency: str
    monthly: float
    target_monthly: float | None
    basis: str

    @property
    def below_target(self) -> bool:
        return self.target_monthly is not None and self.monthly < self.target_monthly

    def describe(self) -> str:
        line = f"Ask {self.currency} {fmt(self.amount)}/{self.period} ({self.basis})"
        if self.period != "month":
            line += f" ≈ {self.currency} {fmt(self.monthly)}/month"
        if self.below_target:
            line += f". Below your target of {self.currency} {fmt(self.target_monthly)}/month: decide before applying."
        return line


def fmt(value: float) -> str:
    return f"{value:,.0f}" if value >= 100 else f"{value:,.2f}"


def parse_amount(raw: str) -> float:
    s = raw.strip().lower().replace(" ", "")
    mult = 1.0
    if s.endswith("k"):
        mult, s = 1000.0, s[:-1]
    s = re.sub(r"[^\d.,]", "", s)
    if not s:
        raise SalaryError(f"Not a number: {raw!r}")
    thousands = re.fullmatch(r"\d{1,3}([.,]\d{3})+", s)
    s = re.sub(r"[.,]", "", s) if thousands else s.replace(",", ".")
    try:
        return float(s) * mult
    except ValueError:
        raise SalaryError(f"Not a number: {raw!r}") from None


def parse_range(raw: str) -> tuple[float, float]:
    pieces = [p for p in re.split(r"\s*(?:-|–|—|to|até|a)\s*", raw.strip()) if p]
    if len(pieces) == 1:
        value = parse_amount(pieces[0])
        return value, value
    if len(pieces) != 2:
        raise SalaryError(f"Use a range like 90k-160k, got {raw!r}")
    lo, hi = sorted((parse_amount(pieces[0]), parse_amount(pieces[1])))
    if hi >= 1000 and lo < hi / 100:
        lo *= 1000
    return lo, hi


def convert(amount: float, from_period: str, to_period: str) -> float:
    for p in (from_period, to_period):
        if p not in PER_MONTH:
            raise SalaryError(f"Unknown period {p!r}. Use one of: {', '.join(PER_MONTH)}.")
    monthly = amount * PER_MONTH[from_period]
    return monthly / PER_MONTH[to_period]


def compute_ask(
    salary: dict,
    track: str | None = None,
    posted: str | None = None,
    period: str | None = None,
    currency: str | None = None,
) -> Ask:
    base_currency = salary.get("currency", "USD")
    base_period = salary.get("period", "month")
    currency = (currency or base_currency).upper()
    targets = (
        salary.get("targets", {})
        if currency == base_currency.upper()
        else salary.get("other", {}).get(currency, {})
    )
    if not targets:
        raise SalaryError(f"No salary targets for {currency}. Add [salary.other.{currency}] to profile.toml.")
    track = track or next(iter(targets))
    if track not in targets:
        raise SalaryError(f"Unknown track {track!r}. Defined: {', '.join(targets)}.")
    target_monthly = convert(float(targets[track]), base_period, "month")
    policy = salary.get("policy", "midpoint")
    if policy not in POLICIES:
        raise SalaryError(f"[salary].policy must be one of {', '.join(POLICIES)}.")
    period = period or base_period

    if posted and policy != "target":
        lo, hi = parse_range(posted)
        amount = hi if policy == "max" else (lo + hi) / 2
        basis = f"{policy} of posted {fmt(lo)}-{fmt(hi)}" if lo != hi else "posted figure"
    else:
        amount = convert(target_monthly, "month", period)
        basis = f"your {track} target"
    monthly = convert(amount, period, "month")
    return Ask(amount, period, currency, monthly, target_monthly, basis)
