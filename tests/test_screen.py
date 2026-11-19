from jobhunt.screen import PASS, REJECT, REVIEW, compile_term, screen


def test_spaces_and_hyphens_are_interchangeable():
    pattern = compile_term("on call")
    assert pattern.search("on-call rotation")
    assert pattern.search("ON CALL")
    assert pattern.search("oncall")


def test_word_boundaries_and_stems():
    assert not compile_term("java").search("JavaScript")
    assert compile_term("relocat*").search("Relocation package")
    assert not compile_term("relocat").search("relocation")


def test_clean_posting_passes():
    result = screen("Fully remote team, TypeScript and Postgres.", ["on call"], ["python"])
    assert result.verdict == PASS
    assert result.hits == []


def test_reject_beats_review():
    result = screen("Hybrid role, Python preferred.", ["hybrid"], ["python"])
    assert result.verdict == REJECT
    assert [h.kind for h in result.hits] == [REJECT, REVIEW]


def test_negated_reject_term_is_downgraded_to_review():
    result = screen("We have no on-call rotation at all.", ["on call"], [])
    assert result.verdict == REVIEW
    assert "negated" in result.hits[0].term


def test_mixed_negated_and_plain_mentions_still_reject():
    text = "No on-call in month one. After that, on-call every 6 weeks."
    assert screen(text, ["on call"], []).verdict == REJECT


def test_snippets_are_limited_and_contextual():
    text = " ".join(["we travel a lot."] * 10)
    hit = screen(text, [], ["travel"]).hits[0]
    assert len(hit.snippets) == 3
    assert "travel" in hit.snippets[0]
