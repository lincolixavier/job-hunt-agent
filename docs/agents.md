# Using other agents

Claude Code is the default and the most tested, but nothing here is Claude-specific except `CLAUDE.md` and `.claude/`. The contract is:

- **Instructions:** `AGENTS.md` (+ the file in `workflows/` the request calls for).
- **Tools the agent must have:** a shell (for `jobhunt`), file read/write, web search/fetch. For applying: a browser it can drive. For the inbox: email access.

| Agent | Instructions | Browser | Notes |
|---|---|---|---|
| Claude Code | `CLAUDE.md` imports `AGENTS.md`; slash commands in `.claude/commands/` | Claude in Chrome (`/chrome`) | Subagents make `/hunt` fast. |
| OpenAI Codex CLI | Reads `AGENTS.md` natively | Playwright MCP | Ask for a workflow by name: "follow workflows/apply.md for <url>". |
| Gemini CLI | Add `{"context": {"fileName": ["AGENTS.md", "GEMINI.md"]}}` to `.gemini/settings.json` | Playwright MCP | |
| Cursor | Reads `AGENTS.md`; or add a rule that points to it | Playwright MCP or the built-in browser | |
| Aider | `aider --read AGENTS.md --read workflows/apply.md` | none built in | Good for `setup` and drafting; apply by hand. |
| GitHub Copilot (agent mode) | Reads `AGENTS.md` | Playwright MCP | |

Tool support changes quickly; check your agent's docs if a file isn't picked up. A one-line fallback that works everywhere: start the session with "Read AGENTS.md and follow it."

## Browser automation without Claude in Chrome

[Playwright MCP](https://github.com/microsoft/playwright-mcp) gives any MCP-capable agent a real browser:

```json
{
  "mcpServers": {
    "playwright": { "command": "npx", "args": ["@playwright/mcp@latest"] }
  }
}
```

Use a dedicated browser profile, stay logged out of sites you don't want the agent touching, and keep the safety rules in `AGENTS.md` (no CAPTCHAs, no passwords, no IDs).

## Email

Any email MCP server works if it can search, read, and (optionally) send. Without one, run `inbox` by pasting the relevant emails into the chat; the agent still updates the tracker.

## Model choice

The workflows are written to be followed by mid-size models, but tailoring and form-filling are judgment-heavy. Use the strongest model you can for `apply`, `prep` and `outreach`; a cheaper one is fine for `inbox` and `status`.
