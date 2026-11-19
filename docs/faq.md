# FAQ

**Will this apply to hundreds of jobs for me?**
No, by design. It applies to postings that pass your rules, one at a time, and stops at anything that needs you. Expect a handful of good applications per session, not a flood.

**Do I need Claude?**
No. Claude Code is the default and best tested. Any agent that can read `AGENTS.md`, run shell commands and (for applying) drive a browser works. See [agents.md](agents.md).

**Does it work in my country / language?**
The tools are language-neutral: rules, keywords, salary currency and writing rules are all in `profile.toml`. Write your CV facts in the language you apply in. If you apply in two languages, keep two bases with translated summaries; bullets can be translated in the target file.

**The CV doesn't look like mine.**
`jobhunt cv css` copies the stylesheet to `me/cv.css`. Change fonts, spacing, colors. The HTML structure is simple on purpose.

**My CV goes to two pages.**
`cv build` exits with an error. Remove a bullet or shorten the summary in that target. Don't shrink the font: recruiters read on phones.

**Why TOML and CSV and not a database or a web app?**
They're readable by you, your agent, git and a spreadsheet, with zero setup. A job search is a few hundred rows.

**Can the agent log in to LinkedIn / Workday for me?**
No. It never handles passwords. It prepares the CV and answers and tells you exactly what to paste.

**Where's my data?**
In `me/`, locally. Nothing is uploaded by the CLI. The `fetch` command only downloads public postings.

**How do I update?**
`git pull`. Your `me/` folder is untouched. If a release changes the profile format, the changelog says how to migrate, and `jobhunt doctor` will flag problems.
