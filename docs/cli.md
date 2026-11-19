# CLI reference

`jobhunt [--home DIR] <command> ...`. The workspace defaults to `./me`, or `$JOBHUNT_HOME`. Every command has `-h`.

Exit codes: `0` ok · `1` error · `2` bad usage · `3` needs review · `4` blocked.

## Setup

| Command | Does |
|---|---|
| `jobhunt init [--force]` | Creates the workspace from the example persona. |
| `jobhunt doctor` | Checks Python, browser, workspace, config validity, base CV, and whether you replaced the example persona. |

## Postings

```bash
jobhunt fetch https://jobs.ashbyhq.com/acme/1234             # markdown to stdout
jobhunt fetch <url> --save me/postings/acme-senior.md        # keep a snapshot
jobhunt fetch <url> --json                                   # structured
```

Uses the public posting APIs of Ashby, Lever and Greenhouse; other URLs are fetched as plain HTML (pages that need JavaScript will tell you to use a browser).

```bash
jobhunt screen <url|file|->            # verdict + snippets, exit 0/3/4
jobhunt screen post.md --warn kafka    # extra terms for this run
jobhunt screen post.md --json
```

Terms come from `[screen]` in `profile.toml`. Matching is case-insensitive; spaces and hyphens are interchangeable; a trailing `*` matches stems. A reject term preceded by a negation ("no on-call") is downgraded to review so you can confirm it.

## CVs

```bash
jobhunt cv new acme-senior --base fullstack --company Acme --role "Senior Engineer" --url <url>
jobhunt cv build acme-senior            # HTML + PDF in me/cvs/, fails if over the page limit
jobhunt cv build                        # all targets
jobhunt cv build --html-only            # no browser needed
jobhunt cv list
jobhunt cv css                          # copy the stylesheet to me/cv.css to customize
```

A target file sets `base` and may override `headline`, `summary`, `skills` (table) and `experience` (table of experience id → list of bullet keys, in order). Unknown ids or keys fail with the list of valid ones.

## Salary

```bash
jobhunt ask --posted "90k-160k" --period year     # midpoint by default
jobhunt ask --track frontend --period hour        # no posted range: your target, converted
jobhunt ask --currency EUR                        # uses [salary.other.EUR]
```

Exit 3 when the ask is below your target. Periods convert with 160 hours or 20 days per month.

## Writing

```bash
jobhunt lint note.txt --kind linkedin_note        # limit from [writing.limits]
pbpaste | jobhunt lint - --max 300
```

Flags banned characters (with line:col), banned phrases (whole words, any case) and length.

## Tracker

```bash
jobhunt track find acme                           # run before every application
jobhunt track add --company Acme --role "Senior Engineer" --url <url> --portal ashby --ask "USD 125k/yr" --cv <file>
jobhunt track add --company Hooli --role Staff --stage pending --note "needs a Loom video"
jobhunt track set acme-senior-engineer --stage interviewing --note "Tech interview Thu 14:00"
jobhunt track list --stage applied --stage pending
jobhunt status [--print] [--stale-days 21]
```

Stages: `found`, `pending` (waiting on you), `applied`, `interviewing`, `offer`, `rejected`, `skipped`, `withdrawn`.

`add` refuses a URL that's already tracked and, when `one_per_company = true`, a second active role at the same company (`--force` overrides). Notes are appended with dates, so the `notes` column is the history of each application.
