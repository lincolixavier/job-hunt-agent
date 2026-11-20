# Contributing

Thanks for helping. This project gets better mostly through field experience: a portal that changed, a source that works, a workflow step that agents keep getting wrong.

## Ways to help

| Contribution | How |
|---|---|
| A portal behaves differently than `docs/portals.md` says | [Portal quirk issue](https://github.com/lincolixavier/job-hunt-agent/issues/new?template=portal_quirk.yml) or a PR to the doc |
| A workflow step agents get wrong | PR to `workflows/` with what went wrong and how the new wording prevents it |
| A bug in the CLI | [Bug report](https://github.com/lincolixavier/job-hunt-agent/issues/new?template=bug_report.yml), ideally with a failing test |
| A new CLI feature | Open a [feature request](https://github.com/lincolixavier/job-hunt-agent/issues/new?template=feature_request.yml) first so we can agree on scope |
| Docs for another agent | PR to `docs/agents.md` |

**Never include personal data** (your CV, tracker, emails, real recruiter names) in issues, PRs or test fixtures. Use the fictional persona from `src/jobhunt/scaffold/`.

## Development

```bash
make setup                 # .venv with jobhunt in editable mode + pytest + ruff
source .venv/bin/activate
make check                 # lint + format check + tests; CI runs the same
make fmt                   # auto-format and auto-fix
```

Optional: `pre-commit install` runs ruff on every commit.

### Ground rules for code

- **Standard library only** at runtime. Dev tools (pytest, ruff) are fine. If you think a dependency is worth it, make the case in an issue first.
- **Python 3.11+.** CI tests 3.11 to 3.13 on Linux and macOS.
- **Every behavior has a test.** Tests use `tmp_path` and the scaffold workspace; network calls are monkeypatched. Tests needing a browser skip themselves when none is installed.
- **Stable exit codes** (`0` ok, `1` error, `2` usage, `3` review, `4` blocked). Workflows depend on them; changing one is a breaking change.
- **Clear errors.** When config is wrong, say which file, which key, and what the valid options are.
- **No explanatory comments.** Prefer clear names; put the "why" in the PR description.

### Ground rules for workflows and AGENTS.md

- Write for a capable model with no context: explicit steps, a clear "done when", concrete commands.
- Safety rules only get stricter. PRs that loosen human gates (sending, submitting, credentials, CAPTCHAs) won't be merged.
- Keep `AGENTS.md` agent-neutral. Claude-specific notes go in `CLAUDE.md`; other agents' notes go in `docs/agents.md`.

## Pull requests

1. Fork, branch from `main` (`fix/lever-location`, `feat/track-export`).
2. Keep PRs focused. Update `CHANGELOG.md` under "Unreleased".
3. Use [Conventional Commits](https://www.conventionalcommits.org/) for titles (`feat:`, `fix:`, `docs:`, `chore:`).
4. `make check` must pass.
5. Fill in the PR template, including how you tested it.

## Releases

Maintainers tag `vX.Y.Z` following [Semantic Versioning](https://semver.org/). Changes to `profile.toml` or `cv.toml` formats are breaking and need a migration note in the changelog.

## Conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md). Be kind; many people here are in the middle of a stressful job search.
