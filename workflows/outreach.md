# Workflow: outreach

**Goal:** short, personal messages to people or companies who might hire the user directly (freelance, contract, or for the user's own studio), sent only with approval and never twice.

**Input:** what the user offers (e.g. "contract full-stack work", "my studio builds MVPs"), target profile (stage, sector, region), and how many.

**Done when:** each message is sent and verified, or the user declined it, and everything is logged.

## Steps

1. **Find prospects.** Good signals: a funding announcement in the last 1-3 months, a public post asking for help ("looking for a contractor", "who's hiring" threads), a product that obviously needs what the user offers. For each, note the signal with its link.

2. **Find a public contact.** Use the company's own site (contact page, footer, imprint/legal page, careers page) or a public post by a founder. Prefer generic addresses (hello@, contact@) or the one a founder published for this purpose. Do not guess addresses, scrape personal data, or use contacts from leaked or paid lists. No public contact: list it as "LinkedIn only" or "form only" for the user.

3. **Dedupe.** `jobhunt track find <company>` for each. Track prospects with `--stage found --portal outreach` so the next round skips them.

4. **Draft.** One message per prospect:
   - Hook: the specific signal ("saw the seed round", "saw you're building X").
   - One sentence on what the user has done that maps to their need, with one concrete proof (a product, a number, a link from `cv.toml` or the user).
   - A small ask: a 20-minute call, or a reply.
   - Under ~90 words for email; within `[writing].limits.linkedin_note` for connection notes.
   - Lint every draft: `jobhunt lint - --kind linkedin_note` or `--kind cover_note`.
   - Write them all to `me/log/<date>-outreach.md` (prospect, address, subject, body).

5. **Approve.** Show the user the list (address, subject, first line) and the file path. Send nothing until they say yes. Apply their edits to every affected draft, then re-lint.

6. **Send one at a time.** After each send, verify it in Sent before moving on. If a send is uncertain, check Sent before retrying. Never send to anyone the user removed.

7. **Log.** `jobhunt track set <id> --stage applied --note "outreach sent to <address>"`, mark the log file as sent, and report the count. Replies are handled by the `inbox` workflow.

## Etiquette

- One message per company, ever, unless they reply.
- No attachments in cold email unless the user asks.
- Respect opt-outs immediately: mark the entry `withdrawn` with the reason.
- Follow the anti-spam laws that apply to the user and the recipient (e.g. CAN-SPAM, GDPR, LGPD). When in doubt, write fewer, better messages.
