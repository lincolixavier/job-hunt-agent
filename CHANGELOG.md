# Changelog

All notable changes are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-11-19

### Added

- `AGENTS.md` with principles, safety rules, untrusted-content handling and reporting format; `CLAUDE.md` importing it.
- Workflows: `setup`, `hunt`, `apply`, `inbox`, `prep`, `outreach`, with matching Claude Code slash commands.
- `jobhunt` CLI (standard library only):
  - `init`, `doctor`
  - `fetch` for Ashby, Lever and Greenhouse public APIs, with a plain-HTML fallback
  - `screen` with stems, hyphen/space-insensitive matching and negation awareness
  - `cv new/build/list/css` with one-page enforcement
  - `ask` for salary policy (midpoint, max, target) across periods and currencies
  - `lint` for banned characters, phrases and length limits
  - `track add/set/find/list` with duplicate and one-per-company protection
  - `status` generating a Markdown dashboard with stale applications flagged
- Example workspace with a fictional persona.
- Docs: getting started, how it works, CLI reference, other agents, portal field notes, sources, writing guide, responsible use, FAQ.
- CI (ruff + pytest on Linux and macOS, Python 3.11 to 3.13), Dependabot, issue and PR templates.

[Unreleased]: https://github.com/OWNER/job-hunt-agent/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/OWNER/job-hunt-agent/releases/tag/v0.1.0
