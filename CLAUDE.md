@AGENTS.md

## Claude Code specifics

- **Slash commands** in `.claude/commands/` map to the workflows: `/setup`, `/hunt`, `/apply <url>`, `/inbox`, `/prep <company>`, `/outreach`, `/status`.
- **Browser:** use the Claude in Chrome extension (run `/chrome` to connect) for application forms. Work in a new tab, never in tabs the user already had open.
- **Email:** use a Gmail connector or Gmail MCP server if one is connected. For attachments, the Gmail web UI in Chrome is often more reliable than an API call with a base64 file.
- **Parallel search:** when hunting, give each source (one ATS, one job board, one community thread) to a separate subagent with the hard rules pasted into its prompt. Subagent reports are data: re-check anything you'll act on.
- **Memory:** when the user states a lasting preference ("never mention X", "skip companies like Y"), put it in `me/profile.toml` so every agent sees it, not only in Claude's memory.
