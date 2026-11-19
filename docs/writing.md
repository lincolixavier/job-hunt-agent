# Writing that sounds like a person

Recruiters read hundreds of AI-polished messages a week. The ones that work are short, specific and a little plain.

## Rules

1. **Lead with the specific.** Their product, their posting, their problem. Then one fact about you that answers it.
2. **One proof beats five adjectives.** "Cut checkout drop-off by 18%" beats "results-driven engineer with a passion for UX".
3. **Short.** Form answers: 2-4 sentences unless they ask for more. Cold email: under ~90 words. LinkedIn connection note: 200 characters.
4. **Plain words.** No "leverage", "passionate", "excited to", "fast-paced", "synergy", "delve". Add your own pet hates to `[writing].banned_phrases`.
5. **No em dashes** by default. They read as machine-written to many people. Commas, periods and colons do the job.
6. **Only true things.** If you're tempted to round up, don't. If you didn't do it, don't imply it.
7. **End with a small ask.** A call, a reply, a question. Not "looking forward to hearing from you".

Check every draft: `jobhunt lint draft.txt --kind cover_note`.

## Before and after

**Form answer: "Why are you interested in this role?"**

> I'm incredibly excited about this opportunity to leverage my passion for building scalable products in a fast-paced environment.

> You're rebuilding checkout for small merchants. I did that at Northwind last year and cut drop-off by 18%, so I know where the edge cases hide.

**LinkedIn note (200 chars)**

> Hi! I came across your profile and would love to connect and learn more about the exciting work your team is doing in the fintech space!

> Saw Acme's seed round. I build LLM support assistants in production (35% of tickets resolved at Northwind). Happy to swap notes if you're hiring.

**Cold email**

> Subject: Partnership opportunity
>
> I hope this email finds you well. I wanted to reach out to introduce myself...

> Subject: Voice notes to timesheets
>
> Hi Dana, congrats on the round. You're building time entry from voice notes. I've shipped a speech-to-structured-data pipeline in production and could help you get it out faster. Worth a 20-minute call next week?

## When the user corrects a phrase

Add it to `[writing].banned_phrases` in `profile.toml` immediately, fix every pending draft that uses it, and re-lint. Corrections should never need repeating.
