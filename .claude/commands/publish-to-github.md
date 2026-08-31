---
description: Security-scan the project, push it to a GitHub repo, write/update the README, stand up GitHub Pages via Actions, and update the repo's About section with the Pages link.
argument-hint: [owner/repo or full github.com URL] [optional: branch]
---

You are publishing this project to GitHub for the user. `$1` is the target repo
(accept either `owner/repo` or a full `https://github.com/...` URL). `$2` is an
optional target branch (default to the repo's default branch). If `$1` is missing,
stop and ask the user for the repo before doing anything else.

Follow the steps below **in this exact order**. The security scan is a hard gate:
nothing gets pushed, committed to a remote, or otherwise sent off this machine until
it passes. This order intentionally differs from a plain reading of "push, then
scan" — scanning has to come before any upload for it to mean anything.

## Step 1 — Security scan (BLOCKING)

Before touching the network or GitHub in any way:

- If a `security-review` skill is available in this session, invoke it. Otherwise do
  the equivalent by hand.
- Diff/list everything that would be pushed (`git status`, `git diff`, and for a
  fresh repo, every tracked file) and scan it for:
  - API keys, access tokens, private keys/certs (`.pem`, `.key`), cloud credential
    files, `.env` files with real values, database connection strings with
    passwords, OAuth client secrets.
  - Anything that looks like a password, OTP, card number, or other credential
    (same pattern class as the credential-warning logic already in this repo's
    `index.html`, if present).
  - Internal-only hostnames/IPs, customer PII, or other data that has no reason to
    be in a public repo.
- Check whether `.gitignore` exists and actually excludes common secret locations
  (`.env*`, `*.pem`, `*.key`, `credentials.json`, `id_rsa*`, etc.). If it's missing
  or has gaps, add the missing entries before staging anything.
- If the scan finds anything concerning: **stop, do not push**, and report exactly
  what was found and where, so the user can decide (redact, remove, or confirm it's
  a fake/demo value that's fine to ship). Only continue past this step once the
  scan is clean or the user explicitly confirms the flagged items are safe to
  publish.

## Step 2 — Push the code to GitHub

- Resolve `$1` to `owner/repo`. If the repo doesn't exist yet, create it (ask the
  user whether it should be public or private if that isn't already obvious from
  context — GitHub Pages on the free plan needs a public repo).
- Attach/add the repo to this session if it isn't already (`add_repo` /
  equivalent), init git locally if needed, commit the current work with a clear
  message, and push to `$2` or the repo's default branch.
- Follow this project's normal git safety rules: never force-push over existing
  history without explicit permission, never skip hooks, and confirm with the user
  before anything destructive.

## Step 3 — Create/update the README

- Write or update `README.md` at the repo root so it actually describes this
  project: what it is, how to open/run it, and any notable constraints (e.g. "static
  single-file demo, no build step, open index.html directly" if that's what this
  project is).
- Keep it accurate to what's actually in the repo — don't invent features. Commit
  and push this alongside or right after Step 2.

## Step 4 — Set up GitHub Pages via a GitHub Actions workflow

- Add `.github/workflows/pages.yml` using the standard GitHub-provided pattern for
  deploying a static site via Actions (not "deploy from a branch"):
  - Trigger on push to the default branch (and `workflow_dispatch`).
  - `permissions: contents: read, pages: write, id-token: write`.
  - A `concurrency` group so overlapping runs don't clobber each other.
  - Build job: checkout, `actions/configure-pages@v5` (its `enablement` input
    defaults to true, which will turn on Pages with source "GitHub Actions" for a
    repo that has never had Pages configured — this is what lets this step work
    without a manual Settings change), `actions/upload-pages-artifact@v3` pointing
    at the site root (or build output dir, if this project has a build step).
  - Deploy job: `environment: github-pages`, `actions/deploy-pages@v4`.
- Commit and push the workflow. Note for the user that the first run may need the
  Actions tab open once to approve/confirm if this is the very first workflow in
  the repo, and that the resulting URL is `https://<owner>.github.io/<repo>/`
  (or the repo's custom domain if one is configured).
- If, after pushing, the workflow run shows Pages still isn't enabled (some org
  policies block Actions from touching Pages settings), fall back to giving the
  user the manual steps: repo → Settings → Pages → Source → "GitHub Actions".

## Step 5 — Update the repo's About section

- Set the repo description and the "Website" field to the GitHub Pages URL from
  Step 4 (and add relevant topics if it's obviously useful, e.g. `demo`,
  `static-site`).
- Search available tools for a repository-metadata-update capability (repo
  description/homepage/topics). If one exists, use it. If none is available in
  this session, don't skip the step — give the user the exact manual path instead:
  repo homepage → gear icon next to "About" → set Website to the Pages URL → Save,
  and mention topics can go in the same dialog.

## Wrap-up

Report back concisely: what was pushed, the README status, whether the security
scan flagged anything (and how it was resolved), the Pages workflow file added, the
live Pages URL once available, and whether the About section was updated
automatically or needs the manual step.
