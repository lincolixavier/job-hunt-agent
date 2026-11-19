from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from jobhunt import __version__, cv, fetch, lint, salary, screen, tracker
from jobhunt.pdf import PdfError, find_chrome
from jobhunt.workspace import ConfigError, Workspace, copy_default_css, init_workspace, resolve_home

EXIT_OK, EXIT_ERROR, EXIT_REVIEW, EXIT_BLOCKED = 0, 1, 3, 4

EPILOG = """\
Typical loop:
  jobhunt screen <url>                      check a posting against your hard rules
  jobhunt track find <company>              make sure you never apply twice
  jobhunt cv new acme-fullstack --base fullstack
  jobhunt cv build acme-fullstack           one-page PDF in me/cvs/
  jobhunt track add --company Acme --role "Senior Engineer" --url <url>
  jobhunt status                            rebuild me/STATUS.md

Exit codes: 0 ok, 1 error, 3 needs review, 4 blocked (reject, lint failure, duplicate).
Docs: docs/cli.md
"""


def _color(code: str, text: str) -> str:
    if os.environ.get("NO_COLOR") or not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


def ok(text: str) -> str:
    return _color("32", text)


def warn(text: str) -> str:
    return _color("33", text)


def bad(text: str) -> str:
    return _color("31", text)


def emit_json(data) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def workspace(args) -> Workspace:
    return Workspace(resolve_home(args.home))


def read_input(source: str) -> tuple[str, str]:
    if source == "-":
        return sys.stdin.read(), "stdin"
    if source.startswith(("http://", "https://")):
        posting = fetch.fetch(source)
        return posting.to_markdown(), posting.title or source
    path = Path(source)
    if not path.exists():
        raise ConfigError(f"{source}: not a URL, file or '-'")
    return path.read_text(encoding="utf-8"), path.name


def cmd_init(args) -> int:
    root = resolve_home(args.home)
    written = init_workspace(root, force=args.force)
    print(ok(f"Created {root} with {len(written)} starter files:"))
    for path in written:
        print(f"  {path.relative_to(root.parent)}")
    print(
        "\nNext:\n"
        f"  1. Drop your current CV (PDF) in {root.name}/base/\n"
        "  2. Open your coding agent here and run the setup workflow (Claude Code: /setup)\n"
        "  3. Run `jobhunt doctor` to check everything"
    )
    return EXIT_OK


def cmd_doctor(args) -> int:
    ws = workspace(args)
    checks: list[tuple[str, bool, str]] = []
    py_ok = sys.version_info >= (3, 11)
    checks.append(("Python 3.11+", py_ok, sys.version.split()[0]))
    chrome = find_chrome()
    checks.append(("Chrome/Chromium for PDFs", bool(chrome), chrome or "not found, set JOBHUNT_CHROME"))
    checks.append(
        ("Workspace", ws.exists(), str(ws.root) if ws.exists() else f"{ws.root} missing, run jobhunt init")
    )
    if ws.exists():
        for label, loader in (("profile.toml", ws.profile), ("cv.toml", ws.cv)):
            try:
                loader()
                checks.append((label, True, "valid"))
            except ConfigError as exc:
                checks.append((label, False, str(exc)))
        base_dir = ws.root / "base"
        has_base = base_dir.exists() and any(base_dir.iterdir())
        checks.append(
            (
                "Base CV in base/",
                has_base,
                "found" if has_base else "add your current CV so the agent can read it",
            )
        )
        placeholder = "Alex Rivera" in ws.profile_path.read_text(encoding="utf-8")
        checks.append(
            ("Profile filled in", not placeholder, "still the example persona" if placeholder else "yes")
        )
        targets = ws.target_slugs()
        checks.append(("CV targets", True, f"{len(targets)} defined"))
    failed = 0
    for label, passed, detail in checks:
        mark = ok("ok  ") if passed else bad("fix ")
        failed += not passed
        print(f"{mark} {label}: {detail}")
    return EXIT_OK if not failed else EXIT_ERROR


def cmd_fetch(args) -> int:
    posting = fetch.fetch(args.url)
    if args.json:
        emit_json(posting.to_dict())
    else:
        text = posting.to_markdown()
        if args.save:
            dest = Path(args.save)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding="utf-8")
            print(ok(f"Saved {args.save}"))
        else:
            print(text)
    return EXIT_OK


def cmd_screen(args) -> int:
    ws = workspace(args)
    reject, warn_terms = screen.rules_from_profile(ws.profile())
    reject += args.reject or []
    warn_terms += args.warn or []
    text, label = read_input(args.source)
    result = screen.screen(text, reject, warn_terms)
    if args.json:
        emit_json({"source": label, **result.to_dict()})
    else:
        color = {screen.PASS: ok, screen.REVIEW: warn, screen.REJECT: bad}[result.verdict]
        print(f"{label}\n{color(result.verdict.upper())}")
        for hit in result.hits:
            print(f"\n  [{hit.kind}] {hit.term}")
            for snip in hit.snippets:
                print(f"    {snip}")
        if result.hits:
            print(
                '\nKeyword hits are a filter, not a judgment. Read each snippet in context ("no on-call" is fine).'
            )
    return {screen.PASS: EXIT_OK, screen.REVIEW: EXIT_REVIEW, screen.REJECT: EXIT_BLOCKED}[result.verdict]


def cmd_cv_build(args) -> int:
    ws = workspace(args)
    results = cv.build(ws, args.slugs or None, pdf=not args.html_only)
    status = EXIT_OK
    for r in results:
        if args.html_only:
            print(f"{r.slug}: {r.html}")
            continue
        line = f"{r.slug}: {r.pdf.name} ({r.pages} page{'s' * (r.pages != 1)})"
        if r.ok:
            print(ok(line))
        else:
            print(bad(f"{line}, over the {r.max_pages}-page limit. Cut bullets or shorten the summary."))
            status = EXIT_BLOCKED
    return status


def cmd_cv_new(args) -> int:
    ws = workspace(args)
    path = cv.new_target(ws, args.slug, args.base, args.company or "", args.role or "", args.url or "")
    print(ok(f"Created {path}. Edit headline/summary, then: jobhunt cv build {args.slug}"))
    return EXIT_OK


def cmd_cv_list(args) -> int:
    ws = workspace(args)
    name = ws.profile()["person"]["name"]
    for slug in ws.target_slugs():
        target = ws.target(slug)
        pdf = ws.cvs_dir / f"{cv.output_stem(name, slug, target)}.pdf"
        mark = "built" if pdf.exists() else "not built"
        print(f"{slug:40} base={target.get('base', '?'):12} {mark}")
    return EXIT_OK


def cmd_cv_css(args) -> int:
    ws = workspace(args)
    if ws.css_override.exists() and not args.force:
        raise ConfigError(f"{ws.css_override} exists. Use --force to reset it.")
    copy_default_css(ws.css_override)
    print(ok(f"Wrote {ws.css_override}. Edit it; every build will use it."))
    return EXIT_OK


def cmd_lint(args) -> int:
    ws = workspace(args)
    try:
        rules = lint.rules_from_profile(ws.profile(), args.kind)
    except KeyError as exc:
        raise ConfigError(str(exc.args[0])) from None
    if args.max is not None:
        rules["max_chars"] = args.max
    text, label = read_input(args.source)
    issues = lint.lint(text, **rules)
    length = len(text.strip())
    if args.json:
        emit_json({"source": label, "chars": length, "issues": [i.__dict__ for i in issues]})
    elif issues:
        print(bad(f"{label}: {len(issues)} issue(s), {length} chars"))
        for issue in issues:
            print(f"  {issue}")
    else:
        limit = f" / {rules['max_chars']}" if rules["max_chars"] else ""
        print(ok(f"{label}: clean, {length}{limit} chars"))
    return EXIT_BLOCKED if issues else EXIT_OK


def cmd_ask(args) -> int:
    ws = workspace(args)
    result = salary.compute_ask(
        ws.profile().get("salary", {}), args.track, args.posted, args.period, args.currency
    )
    if args.json:
        emit_json({**result.__dict__, "below_target": result.below_target})
    else:
        print(warn(result.describe()) if result.below_target else result.describe())
    return EXIT_REVIEW if result.below_target else EXIT_OK


def _row_line(row: dict) -> str:
    return f"{row['id']:45} {row['stage']:12} {row['updated']:10} {row['company']}, {row['role']}"


def cmd_track_add(args) -> int:
    ws = workspace(args)
    one = ws.profile().get("search", {}).get("one_per_company", True)
    try:
        row = tracker.Tracker(ws.tracker_path).add(
            company=args.company,
            role=args.role,
            url=args.url or "",
            stage=args.stage,
            portal=args.portal or "",
            salary_ask=args.ask or "",
            cv=args.cv or "",
            note=args.note or "",
            one_per_company=one,
            force=args.force,
            on=args.date,
        )
    except tracker.DuplicateError as exc:
        print(bad(f"Not added: {exc}"))
        print(f"  {_row_line(exc.existing)}")
        return EXIT_BLOCKED
    print(ok(f"Added {row['id']} ({row['stage']})"))
    return EXIT_OK


def cmd_track_set(args) -> int:
    ws = workspace(args)
    row = tracker.Tracker(ws.tracker_path).update(
        args.id,
        stage=args.stage,
        note=args.note,
        on=args.date,
        url=args.url,
        portal=args.portal,
        salary_ask=args.ask,
        cv=args.cv,
    )
    print(ok(f"Updated {row['id']}: {row['stage']}"))
    return EXIT_OK


def cmd_track_find(args) -> int:
    ws = workspace(args)
    rows = tracker.Tracker(ws.tracker_path).find(args.query)
    if args.json:
        emit_json(rows)
    elif rows:
        print(warn(f"{len(rows)} match(es). Check before applying again:"))
        for row in rows:
            print(f"  {_row_line(row)}")
    else:
        print(ok(f"No entry matches {args.query!r}. Safe to proceed."))
    return EXIT_OK if not rows else EXIT_REVIEW


def cmd_track_list(args) -> int:
    ws = workspace(args)
    rows = tracker.Tracker(ws.tracker_path).load()
    if args.stage:
        rows = [r for r in rows if r["stage"] in args.stage]
    if args.json:
        emit_json(rows)
    else:
        for row in rows:
            print(_row_line(row))
        print(f"\n{len(rows)} entr{'y' if len(rows) == 1 else 'ies'}")
    return EXIT_OK


def cmd_status(args) -> int:
    ws = workspace(args)
    rows = tracker.Tracker(ws.tracker_path).load()
    text = tracker.render_status(rows, stale_days=args.stale_days)
    ws.status_path.write_text(text, encoding="utf-8")
    if args.print:
        print(text)
    else:
        print(ok(f"Wrote {ws.status_path} ({len(rows)} entries)"))
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jobhunt",
        description="Deterministic helpers for an AI-assisted job search. Your agent drives; these keep it honest.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"jobhunt {__version__}")
    parser.add_argument("--home", help="workspace folder (default: ./me or $JOBHUNT_HOME)")
    sub = parser.add_subparsers(dest="command", required=True, metavar="<command>")

    p = sub.add_parser("init", help="create your private workspace (me/) from the starter templates")
    p.add_argument("--force", action="store_true", help="overwrite existing starter files")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("doctor", help="check Python, browser, workspace and config")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser(
        "fetch", help="download a posting (Ashby, Lever, Greenhouse APIs; plain web as fallback)"
    )
    p.add_argument("url")
    p.add_argument("--json", action="store_true")
    p.add_argument("--save", metavar="FILE", help="write markdown to FILE")
    p.set_defaults(func=cmd_fetch)

    p = sub.add_parser("screen", help="check a posting (URL, file or -) against your hard rules")
    p.add_argument("source")
    p.add_argument("--reject", action="append", metavar="TERM", help="extra reject term (repeatable)")
    p.add_argument("--warn", action="append", metavar="TERM", help="extra review term (repeatable)")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_screen)

    p = sub.add_parser("cv", help="tailored one-page CVs")
    cv_sub = p.add_subparsers(dest="cv_command", required=True, metavar="<action>")
    q = cv_sub.add_parser("build", help="render targets to HTML + PDF and check the page count")
    q.add_argument("slugs", nargs="*", help="targets to build (default: all)")
    q.add_argument("--html-only", action="store_true", help="skip PDF printing")
    q.set_defaults(func=cmd_cv_build)
    q = cv_sub.add_parser("new", help="create targets/<slug>.toml for a posting")
    q.add_argument("slug")
    q.add_argument("--base", required=True, help="base profile from cv.toml [bases]")
    q.add_argument("--company")
    q.add_argument("--role")
    q.add_argument("--url")
    q.set_defaults(func=cmd_cv_new)
    q = cv_sub.add_parser("list", help="list targets and whether their PDF exists")
    q.set_defaults(func=cmd_cv_list)
    q = cv_sub.add_parser("css", help="copy the default stylesheet to me/cv.css to customize the look")
    q.add_argument("--force", action="store_true")
    q.set_defaults(func=cmd_cv_css)

    p = sub.add_parser("lint", help="check a text (file or -) against your writing rules")
    p.add_argument("source")
    p.add_argument("--kind", help="length limit from [writing.limits], e.g. linkedin_note")
    p.add_argument("--max", type=int, help="explicit character limit")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_lint)

    p = sub.add_parser("ask", help="salary to ask for, from your policy and the posted range")
    p.add_argument("--track", help="salary track from [salary.targets], e.g. fullstack")
    p.add_argument("--posted", help='posted figure or range, e.g. "90k-160k"')
    p.add_argument(
        "--period", choices=list(salary.PER_MONTH), help="period of the posted figure / form field"
    )
    p.add_argument("--currency", help="currency of the form field, e.g. EUR")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_ask)

    p = sub.add_parser("track", help="the application tracker (me/tracker.csv)")
    t_sub = p.add_subparsers(dest="track_command", required=True, metavar="<action>")
    q = t_sub.add_parser(
        "add", help="log a posting; refuses duplicates and a second role at the same company"
    )
    q.add_argument("--company", required=True)
    q.add_argument("--role", required=True)
    q.add_argument("--url")
    q.add_argument("--stage", default="applied", choices=tracker.STAGES)
    q.add_argument("--portal", help="ashby, lever, greenhouse, email, ...")
    q.add_argument("--ask", help="salary you asked for")
    q.add_argument("--cv", help="CV file sent")
    q.add_argument("--note")
    q.add_argument("--date", help="YYYY-MM-DD (default: today)")
    q.add_argument("--force", action="store_true", help="allow another role at the same company")
    q.set_defaults(func=cmd_track_add)
    q = t_sub.add_parser("set", help="update stage, add a dated note, or fix fields")
    q.add_argument("id")
    q.add_argument("--stage", choices=tracker.STAGES)
    q.add_argument("--note")
    q.add_argument("--url")
    q.add_argument("--portal")
    q.add_argument("--ask")
    q.add_argument("--cv")
    q.add_argument("--date")
    q.set_defaults(func=cmd_track_set)
    q = t_sub.add_parser("find", help="search by company, role, id or URL (run before every application)")
    q.add_argument("query")
    q.add_argument("--json", action="store_true")
    q.set_defaults(func=cmd_track_find)
    q = t_sub.add_parser("list", help="list entries")
    q.add_argument("--stage", action="append", choices=tracker.STAGES)
    q.add_argument("--json", action="store_true")
    q.set_defaults(func=cmd_track_list)

    p = sub.add_parser("status", help="regenerate me/STATUS.md from the tracker")
    p.add_argument("--stale-days", type=int, default=21)
    p.add_argument("--print", action="store_true", help="also print it")
    p.set_defaults(func=cmd_status)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (ConfigError, tracker.TrackerError, salary.SalaryError, fetch.FetchError, PdfError) as exc:
        print(bad(f"error: {exc}"), file=sys.stderr)
        return EXIT_ERROR
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
