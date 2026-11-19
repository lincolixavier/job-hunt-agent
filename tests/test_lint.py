from jobhunt.lint import lint, rules_from_profile


def test_flags_banned_char_with_position():
    issues = lint("Hello\nthere — friend", banned_chars=["—"])
    assert len(issues) == 1
    assert (issues[0].line, issues[0].col) == (2, 7)


def test_phrases_are_case_insensitive_and_whole_word():
    issues = lint("I'm EXCITED TO apply. Leveraged nothing.", banned_phrases=["I'm excited to", "leverage"])
    assert [i.kind for i in issues] == ["phrase"]


def test_length_limit():
    assert lint("a" * 201, max_chars=200)[0].kind == "length"
    assert lint("a" * 200, max_chars=200) == []


def test_rules_from_profile_kind(ws):
    rules = rules_from_profile(ws.profile(), "linkedin_note")
    assert rules["max_chars"] == 200
    assert "—" in rules["banned_chars"]
