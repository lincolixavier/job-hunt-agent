# Workflow: hunt

**Goal:** a shortlist of postings that pass every hard rule, with the evidence, ready for `apply`.

**Input:** optionally a count (default 15), a role focus, or specific sources.

**Done when:** each candidate is in the tracker as `found` (shortlisted) or `skipped` (with reason), and the user has the shortlist.

## Steps

1. **Load context.** Read `me/profile.toml` (roles, hard rules, skip list) and `jobhunt track list` so you know what's already been seen.

2. **Search.** Use the sources in `docs/sources.md`, newest postings first (last 2-3 weeks). If your harness supports parallel subagents, give each source to one, with the hard rules and skip list pasted into its prompt, and ask each to return: company, title, URL, posting date, location text, salary text, and the exact sentence proving the remote/location policy.

3. **Dedupe.** For each candidate run `jobhunt track find <company>`. Drop anything already tracked unless the user asked to revisit it. Drop companies on the skip list.

4. **Screen.** For each remaining candidate:
   - `jobhunt fetch <url> --save me/postings/<slug>.md` (or open it in the browser if fetch fails and save the text there yourself). Postings get taken down; this snapshot is what you'll prep interviews from.
   - `jobhunt screen me/postings/<slug>.md`.
   - Read the full text anyway. Keywords miss things ("must overlap 9-5 PT", "quarterly team week in Lisbon", "this is a Python shop").
   - Check: seniority, location/hiring country, work mode, on-call, stack, contract type, salary if posted, posting still open.

5. **Decide.** For each posting, one of:
   - **shortlist:** passes every rule. `jobhunt track add --stage found --note "<why it fits, one line>"`.
   - **skip:** breaks a rule. `jobhunt track add --stage skipped --note "<rule broken, quoted evidence>"`. Logging skips stops you from re-screening them next batch.
   - **ask:** ambiguous (e.g. "remote-first with optional offsites"). Put it in the report with the quote and let the user decide.

6. **Report.** Write `me/log/<date>-batch-<n>.md` with the shortlist table (company, role, link, salary, fit note), the "ask" items with quotes, and the skip list with reasons. Show the user the shortlist and the ask items, in that order. Run `jobhunt status`.

## Tips

- Rules exhaust the market fast. When results dry up, tell the user which rule is filtering most and let them decide whether to relax it. Never relax it yourself.
- "Remote" in a title means little. Find the sentence that says where they hire and whether there are mandatory trips.
- A posting older than ~30 days on a fast-moving board is often closed; check before spending time.
