import pytest

from jobhunt.salary import SalaryError, compute_ask, convert, parse_amount, parse_range

SALARY = {
    "currency": "USD",
    "period": "month",
    "policy": "midpoint",
    "targets": {"fullstack": 6000, "frontend": 5500},
    "other": {"EUR": {"fullstack": 5500}},
}


@pytest.mark.parametrize(
    ("raw", "value"),
    [
        ("90k", 90000),
        ("4.5k", 4500),
        ("90,000", 90000),
        ("15.500", 15500),
        ("$120", 120),
        ("R$ 14.000", 14000),
    ],
)
def test_parse_amount(raw, value):
    assert parse_amount(raw) == value


def test_parse_range_variants():
    assert parse_range("90k-160k") == (90000, 160000)
    assert parse_range("90-160k") == (90000, 160000)
    assert parse_range("R$ 15.500 até R$ 20.000") == (15500, 20000)
    assert parse_range("5000") == (5000, 5000)


def test_convert_periods():
    assert convert(120000, "year", "month") == pytest.approx(10000)
    assert convert(6000, "month", "hour") == pytest.approx(37.5)


def test_midpoint_of_posted_range():
    ask = compute_ask(SALARY, "fullstack", "90k-160k", "year")
    assert ask.amount == 125000
    assert not ask.below_target


def test_flags_below_target():
    ask = compute_ask(SALARY, "fullstack", "18-20", "hour")
    assert ask.below_target


def test_no_range_uses_target_in_requested_period():
    ask = compute_ask(SALARY, "frontend", None, "year")
    assert ask.amount == pytest.approx(66000)


def test_other_currency_and_errors():
    assert compute_ask(SALARY, "fullstack", None, None, "eur").amount == 5500
    with pytest.raises(SalaryError):
        compute_ask(SALARY, "fullstack", None, None, "GBP")
    with pytest.raises(SalaryError):
        compute_ask(SALARY, "backend")
