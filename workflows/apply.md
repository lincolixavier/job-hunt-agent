# Workflow: apply

**Goal:** submit a tailored, truthful application, or hand it to the user with everything prepared.

**Input:** one or more posting URLs (pasted by the user or shortlisted by `hunt`).

**Done when:** each posting is `applied` (success screen seen) or `pending` (with the exact blocker and link), and the user got a short report.

## Steps

For each posting, in order:

1. **Duplicate check.** `jobhunt track find <url>` and `jobhunt track find <company>`. If it's already applied, stop and tell the user (include the date). If another role at the same company is active and `one_per_company` is on, ask before continuing.

2. **Read it.** `jobhunt fetch <url> --save me/postings/<slug>.md` (skip if `hunt` already saved it) or open it. Run `jobhunt screen`. Re-check every hard rule against the full text. If it fails one, log `skipped` with the evidence and move on.

3. **Tailor the CV.**
   - `jobhunt cv new <company>-<role> --base <closest base> --company ... --role ... --url ...`
   - In the target file, write a `headline` and 2-3 sentence `summary` aimed at this posting: name the 2-3 things they ask for that the user has actually done, using facts from `cv.toml` only.
   - Reorder `experience` bullets so the most relevant come first. Add skills only if they're in `cv.toml` or the base.
   - `jobhunt cv build <slug>`. Must be within the page limit. Open the HTML or PDF and read it once.

4. **Prepare answers.**
   - Salary: `jobhunt ask --posted "<range from posting>" --period <period of the form field> [--currency X]`. If it exits 3 (below target), ask the user before applying.
   - Free-text questions: draft from `cv.toml` facts, run `jobhunt lint - --kind form_answer`, keep it short. If a question needs a story or opinion you don't have, leave it to the user.
   - Note every inferred answer (start date, years with X, "are you comfortable with Y").

5. **Fill the form.** Check `docs/portals.md` for the portal's quirks first. Upload the generated PDF. Use only `profile.toml` contact data. Follow the hard safety rules in `AGENTS.md`: anything requiring login, an ID, a video, a test or a personal story goes to `pending`.

6. **Submit once.** Click submit a single time. Wait for and confirm the success message (or confirmation email). If the click seems to do nothing, check for validation errors on the page before trying again; never resubmit blindly.

7. **Log.**
   - Submitted: `jobhunt track add --company ... --role ... --url ... --portal <ats> --ask "<what you typed>" --cv <pdf name> --note "<inferred answers, if any>"`
   - Handed off: `--stage pending --note "<blocker>: <what's ready, e.g. CV path, drafted answers>"`
   - Append the posting to the current `me/log/` file.

8. **Report** with the format in `AGENTS.md`, then `jobhunt status`.

## Applying by email

Some postings say "send your CV to jobs@company.com". Draft subject and body (lint them), show the user recipient, subject, body and attachment, and send only after an explicit yes. Then verify it's in Sent and log it with `--portal email`.
