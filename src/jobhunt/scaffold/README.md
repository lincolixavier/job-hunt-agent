# Your workspace

Private by default: this folder is in `.gitignore`. Nothing here is committed unless you change that.

| Path | What it is | Who edits it |
|---|---|---|
| `profile.toml` | Contact, hard rules, screening keywords, salary policy, writing rules | You (or the setup workflow) |
| `cv.toml` | Your CV as data: every fact once, plus 2-3 base angles | You, reviewed by you |
| `base/` | Your current CV as PDF, the source the agent reads facts from | You |
| `targets/<slug>.toml` | Per-posting tailoring (headline, summary, bullet order) | The agent |
| `postings/` | Saved text of every posting you screened (they get taken down) | `jobhunt fetch --save` |
| `cvs/` | Generated HTML + PDF, one per posting | `jobhunt cv build` |
| `tracker.csv` | Every posting found, applied, skipped or closed | `jobhunt track` |
| `STATUS.md` | Readable dashboard | `jobhunt status` |
| `log/` | One markdown file per batch or outreach round | The agent |
| `cv.css` (optional) | Your CV styling; create it with `jobhunt cv css` | You |
