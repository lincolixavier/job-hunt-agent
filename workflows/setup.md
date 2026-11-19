# Workflow: setup

**Goal:** turn the example workspace into the user's own, and get one CV they approve. Everything else scales from this, so take the time.

**Done when:** `jobhunt doctor` is all green, the user approved a generated PDF, and `profile.toml` reflects their real rules.

## Steps

1. **Workspace.** If `me/` doesn't exist, run `jobhunt init`. Run `jobhunt doctor` and fix what you can (missing browser: tell the user what to install).

2. **Read the CV.** Read every file in `me/base/`. If it's empty, ask the user to drop their CV (PDF or text) there, or to paste it. Don't continue without it.

3. **Interview the user.** Ask in one message, grouped, skipping what the CV already answers:
   - Name as it should appear, city and country, timezone, email, phone, links.
   - Target roles and seniority.
   - Hard rules: remote/hybrid/onsite, on-call, travel, contract types, countries they can be hired from, languages or stacks they won't take.
   - Companies to skip (current or past employers, ones they dislike).
   - Salary: currency, period, target per track (e.g. full-stack vs frontend), and the policy for posted ranges (midpoint, max, or always the target).
   - Writing: language for applications, words or phrases they never want to see, characters to avoid.
   - Which language you should use when talking to them.

4. **Fill `profile.toml`.** Replace the example persona entirely. Translate each hard rule into:
   - a plain-language line in `[search].hard_rules`, and
   - concrete keywords in `[screen].reject` (deal-breakers) or `[screen].warn` (needs reading). Use `*` for stems, e.g. `relocat*`.

5. **Fill `cv.toml`.** One `[[experience]]` per role with every fact from the CV as a short, keyed bullet. Rules:
   - One fact per bullet, numbers kept exactly as the user wrote them.
   - Keys are short and stable (`checkout`, `migration`, `mentoring`): targets reference them.
   - Ask about anything ambiguous instead of guessing.
   - Then write 2 or 3 `[bases.*]` (e.g. fullstack, frontend, AI) that pick and order bullets for each angle.

6. **First CV.** `jobhunt cv new first-review --base <main base>`, then `jobhunt cv build first-review`. Show the user the PDF path and ask for corrections. Iterate on `cv.toml` (facts) and the base (selection, order) until they say it's good. If they want a different look, `jobhunt cv css` and edit `me/cv.css`.

7. **Close.** Delete `me/targets/example-*.toml` and `first-review` if the user doesn't want to keep them. Run `jobhunt doctor`. Summarize the rules you stored in three or four lines and suggest the next step (`/hunt`).
