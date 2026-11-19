# Security policy

## Supported versions

The latest release on `main` gets fixes. Older tags don't.

## Reporting a vulnerability

Please **don't open a public issue**. Use GitHub's private vulnerability reporting: **Security → Report a vulnerability** on this repository. You'll get an acknowledgement within 7 days and a status update at least every 14 days until it's resolved.

## What counts

This project runs an AI agent with access to a browser, email and your personal data, so we care about more than code bugs:

- Ways the CLI could leak data from `me/` (network calls, file writes outside the workspace, log output).
- Workflow or `AGENTS.md` wording that could lead an agent to send data, submit forms or follow instructions from untrusted content (postings, emails, web pages) without the user's approval.
- Prompt-injection patterns seen in real postings that our instructions don't cover. Please share the pattern (redacted), not a working exploit against a specific service.
- Unsafe handling of fetched content (`jobhunt fetch`) or generated HTML/PDF.

## Design guarantees

- The CLI has no runtime dependencies and makes network requests only in `jobhunt fetch`, to the URL you pass or the matching public ATS API.
- Generated CVs are static HTML with escaped content and no scripts.
- `me/` is gitignored by default.
- `AGENTS.md` forbids the agent from entering passwords, government IDs or payment data, solving CAPTCHAs, or sending anything without explicit approval.
