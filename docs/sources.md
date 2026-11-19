# Where to find postings

Use several kinds of sources; each finds companies the others miss. Prefer sources with posting dates and direct ATS links.

## ATS boards (direct, structured, fresh)

Search the web restricted to the ATS domain plus your role and constraints, e.g.:

```
site:jobs.ashbyhq.com "senior full stack" remote
site:jobs.lever.co "frontend" "LATAM"
site:job-boards.greenhouse.io "product engineer" "remote"
site:apply.workable.com "senior software engineer" remote
```

Then screen each hit with `jobhunt fetch` + `jobhunt screen`. When a company looks good, list its whole board:

- Ashby: `https://api.ashbyhq.com/posting-api/job-board/<org>?includeCompensation=true`
- Lever: `https://api.lever.co/v0/postings/<org>?mode=json`
- Greenhouse: `https://boards-api.greenhouse.io/v1/boards/<org>/jobs`

## Community threads

- **Hacker News "Who is hiring?"** (first weekday of each month) and **"Freelancer? Seeking freelancer?"**. Searchable through the Algolia API: `https://hn.algolia.com/api/v1/search?tags=story,author_whoishiring` to find the thread, then `https://hn.algolia.com/api/v1/items/<id>` for every comment. Many posts say "email us", which suits the email path in `workflows/apply.md`.
- Language or framework communities (Discord/Slack job channels, newsletters). Ask the user which ones they're in.

## Remote job boards

General: We Work Remotely, Remote OK, Remotive, Working Nomads, Himalayas, Wellfound (account needed to apply). Region-focused boards exist for most regions (e.g. Getonbrd for Latin America); ask the user which ones matter for where they can be hired. Many boards block automated access. If fetching fails, use web search results and the company's own ATS link instead.

## LinkedIn

Searching and reading postings works without login through the public guest pages (`linkedin.com/jobs/view/<id>`). Applying needs the user. LinkedIn is most useful to find companies; then apply on their own ATS when possible, which is usually better anyway.

## Direct-to-company (outreach)

For freelance or contract work: funding announcements (startup news sites, investor portfolio pages), "looking for a contractor" posts, and product launches. See `workflows/outreach.md`.

## Signals worth reading for

| Good | Needs a closer look |
|---|---|
| Salary range posted | "Competitive salary" only |
| Explicit list of countries they hire from | "Remote" with a city in the location field |
| Posted in the last 2 weeks | Older than 30 days |
| Named hiring manager or team | Agency reposts with no company name |
| Stack listed concretely | "Any language" plus a long list of buzzwords |
