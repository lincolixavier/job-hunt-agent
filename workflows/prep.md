# Workflow: prep

**Goal:** the user walks into the interview knowing the role, the people, their own best stories and the questions that protect their hard rules.

**Input:** company (and the interview stage if known).

**Done when:** `me/log/<date>-prep-<company>.md` exists and the user has the short version in chat.

## Steps

1. **Gather.** The tracker entry and notes, the saved posting in `me/postings/` (or `jobhunt fetch <url>` if it's still up), every email in the thread (format, interviewers, questions they sent in advance), and the company's own site. Look up interviewers only via what they published professionally (LinkedIn headline, talks, blog).

2. **Map the role to the user.** A table: what the posting asks for → the user's matching fact from `cv.toml` → gap (if any) and how to address it honestly.

3. **Questions they sent.** For each, a short answer outline in the user's voice, using facts from `cv.toml`. For behavioral questions ("a time when..."), use STAR (situation, task, action, result) and **ask the user for the real story** when `cv.toml` doesn't contain one. Offer candidate stories from their CV as prompts, never invented details.

4. **Stage-specific.**
   - Recruiter screen: pitch (30 seconds), motivation, salary answer from `jobhunt ask`, availability.
   - Hiring manager / peer: scope, how they work, what success looks like at 90 days.
   - Technical: likely topics from the stack and the format they described; a short refresher list, not a course.
   - Culture / people: values on their site, examples of feedback, conflict, ownership.
   - Executive: company direction, why now, how the role moves the business.

5. **Questions to ask.** Always include the ones that check the user's hard rules if the posting was ambiguous (on-call, travel, hiring country, contract type, stack they won't use), plus 2-3 genuine ones about the team.

6. **Write it up** in the log file and give the user a one-screen version: key facts, 3 stories to have ready, salary line, questions to ask, anything to clarify.
