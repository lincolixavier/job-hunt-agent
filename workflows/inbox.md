# Workflow: inbox

**Goal:** make the tracker reflect reality and surface what needs the user today.

**Done when:** every relevant new email is reflected in `me/tracker.csv`, `me/STATUS.md` is regenerated, and the user has a short list of actions with dates.

## Steps

1. **Window.** Find the most recent `updated` date in the tracker (`jobhunt track list`) and search the inbox from a day before it. Skip promotions and newsletters.

2. **Classify each relevant thread** and match it to a tracker entry (`jobhunt track find <company>`). Recruiters often write from the ATS domain (ashbyhq, lever, greenhouse, workable, teamtailor) with the company in the subject or body.

   | Email says | Stage | Note to add |
   |---|---|---|
   | Application received | unchanged | `ack` (only if useful) |
   | Interview invite or booking link | `interviewing` | who, format, date and time with timezone, or "needs booking: <link>" |
   | Calendar confirmation | `interviewing` | date, time, attendees |
   | Take-home, test, video, questionnaire | `pending` | what, deadline, link |
   | Rejection, role filled or frozen | `rejected` | reason if given |
   | Offer | `offer` | figures exactly as written |
   | Recruiter outreach for a new role | new `found` entry | source and contact |

   Use `jobhunt track set <id> --stage <stage> --note "<note>" --date <email date>`.

3. **Unknown company?** If an email mentions a process not in the tracker (the user applied themselves), add it with `--note "applied by you"`.

4. **Follow-ups.** `jobhunt status` lists applications with no news for 21+ days. Suggest follow-ups only for ones the user cares about; draft them on request.

5. **Report**, most urgent first:
   - Scheduled: date, time (user's timezone), company, who, format.
   - Needs you: tests, videos, bookings, replies, with deadlines and links.
   - Closed: one line, comma-separated.
   - Draft any reply the user needs to send, but never send it without an explicit yes.
