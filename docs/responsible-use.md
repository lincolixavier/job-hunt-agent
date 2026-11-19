# Responsible use

This project helps one person run a careful job search. It is not a mass-application bot, and it's designed to make that hard.

## What the defaults enforce

- **Honesty.** CVs and answers are built only from facts you wrote down. Inferred answers are flagged to you.
- **No duplicates.** The tracker refuses a posting it has seen, and by default a second role at the same company.
- **Human gates.** No email or message is sent without your explicit approval. The agent hands you anything involving logins, IDs, CAPTCHAs, videos, tests or personal stories.
- **No bot-check evasion.** The agent never solves CAPTCHAs or works around blocks. If a site blocks automation, you apply there yourself.

## What we ask of you

- **Apply where you'd actually take the job.** Recruiters are people; flooding them hurts everyone, including you.
- **Respect site terms.** Some job boards forbid automated access. Use their public APIs or apply manually there.
- **Outreach:** contact companies through addresses they publish for that purpose, once, and stop when asked. Follow the anti-spam and privacy laws that apply to you and your recipients (CAN-SPAM, GDPR, LGPD and others).
- **Own the result.** You are the applicant. Read what the agent prepared before it goes out, especially the first few times.

## Your data

Everything lives in `me/`, on your machine, gitignored. What leaves it is what your agent sends to its model provider and what you submit to employers. Check your agent's data-retention settings if that matters to you, and don't put secrets (passwords, ID numbers) anywhere in `me/`.
