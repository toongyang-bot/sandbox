# UOB IT Service Desk (Singapore) — Training Demo

A self-contained, single-page mockup of an internal IT support service desk,
styled as a "UOB Bank" training/demo. Built for UI demonstration and training
purposes only — see the disclaimer in the footer.

> **Training demo — not affiliated with or endorsed by United Overseas Bank
> Limited.**

## What's in here

- **`index.html`** — the entire site: sticky nav + hero, a fully validated IT
  support ticket form, an FAQ accordion with live search, and a footer. All
  CSS and JS are inlined; there is no build step and no external
  dependencies.
- A modern grey (slate) design system with a single blue accent, localized
  for Singapore (locale badge, Singapore Time labeling, SG toll-free hotline
  format).
- A client-side security check (math captcha + honeypot field) on the ticket
  form to deter naive automated spam submissions. This is a lightweight,
  demo-appropriate deterrent only — the page makes no network calls, so
  there's no backend to verify a real CAPTCHA against.

## Running it

No install, no server. Just open `index.html` in a browser (double-click it,
or open the file directly via a `file://` URL).

## How the ticket form works

- All required fields are validated on blur and on submit, with inline error
  messages and a focus jump to the first invalid field.
- Corporate email is restricted to `@uobgroup.com` for the demo.
- The description field is scanned client-side for anything that looks like
  a password/OTP/credential and warns the user never to include one.
- On successful submission, a mock ticket reference
  (`UOB-ITSD-YYYYMMDD-####`) and an SLA response time are shown. Submitted
  tickets are kept in an in-memory JavaScript array only — nothing is
  written to `localStorage`/`sessionStorage`, and nothing is sent over the
  network.

## Project tooling

- `.claude/commands/publish-to-github.md` — a project-level Claude Code
  command that security-scans the repo, pushes it to GitHub, updates this
  README, sets up GitHub Pages via Actions, and updates the repo's About
  section.
- `.mcp.json` — a project-level Playwright MCP server for browser-based
  checks (e.g. screenshots) of this page.
- `.claude/skills/` — `frontend-design`, `ui-ux-pro-max`, and
  `cybersecurity-analyst` skills used to inform the visual design and
  security posture of this project.
