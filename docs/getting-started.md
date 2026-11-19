# Getting started

About 20 minutes, most of it spent answering your agent's setup questions.

## 1. Requirements

| Need | Why | Check |
|---|---|---|
| Python 3.11+ | runs the `jobhunt` CLI (no extra packages) | `python3 --version` |
| Chrome, Chromium, Edge or Brave | prints CVs to PDF (headless) | `jobhunt doctor` |
| An AI coding agent | drives the workflows | Claude Code is the default; see [other agents](agents.md) |
| A browser tool for the agent | fills application forms | Claude in Chrome, or Playwright MCP |
| An email tool for the agent (optional) | reads replies, sends approved emails | Gmail connector or any email MCP server |

`pdfinfo` (from poppler) is optional; it makes page counting exact. Without it, `jobhunt` parses the PDF itself.

## 2. Install

```bash
git clone https://github.com/OWNER/job-hunt-agent.git
cd job-hunt-agent
make setup              # creates .venv and installs jobhunt + dev tools
source .venv/bin/activate
jobhunt --version
```

No `make`? Use `python3 -m venv .venv && .venv/bin/pip install -e .`. Don't want to install anything? Every command works as `bin/jobhunt ...` from the repo root.

Windows: use `py -m venv .venv`, `.venv\Scripts\pip install -e .`, then `jobhunt` from that venv. If your browser is in a custom location, set `JOBHUNT_CHROME` to its full path.

## 3. Create your workspace

```bash
jobhunt init        # creates me/ from the example persona
jobhunt doctor      # tells you what's still missing
```

Put your current CV (PDF or text) in `me/base/`. Everything under `me/` is gitignored.

## 4. Let the agent set you up

Open your agent in the repo folder:

```bash
claude              # or codex, gemini, cursor-agent, aider...
```

Then run `/setup` (Claude Code) or say "follow workflows/setup.md". The agent reads your CV, asks about your hard rules, salary and writing preferences, fills `me/profile.toml` and `me/cv.toml`, and builds a first CV for you to review.

**Review that first PDF carefully.** Every tailored CV is built from the same facts, so fixing them once fixes them everywhere.

## 5. Daily loop

| You say | What happens |
|---|---|
| `/hunt 15 frontend` | Finds and screens postings, shortlists the ones that pass every rule |
| `/apply <url>` | Tailors a CV, fills the form, submits once, logs it (or hands it to you) |
| `/inbox` | Reads new email, updates the tracker, lists what needs you |
| `/prep Acme` | Builds an interview brief from the posting, emails and your CV |
| `/outreach` | Finds prospects for freelance work and drafts messages for approval |
| `/status` | Regenerates `me/STATUS.md` |

Without slash commands, say the same thing in plain words; `AGENTS.md` tells the agent which workflow to follow.

## Customizing

- **Rules:** edit `me/profile.toml`. `[screen]` keywords change what `jobhunt screen` flags; `[search].hard_rules` is what the agent reads.
- **CV look:** `jobhunt cv css`, then edit `me/cv.css`.
- **Workspace location:** `--home <dir>` or `JOBHUNT_HOME=<dir>`, e.g. to keep it in a private synced folder.
