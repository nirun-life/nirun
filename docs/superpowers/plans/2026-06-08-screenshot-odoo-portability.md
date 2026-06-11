<!-- Copyright (c) 2026 NSTDA -->

# Screenshot Odoo Portability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the `screenshot-odoo` skill portable across Codex and Claude by replacing the Python-only helper with a
cross-platform Node/Playwright helper and shared runtime-agnostic instructions.

**Architecture:** Keep a single skill entrypoint in `.claude/skills/screenshot-odoo/`. Replace `odoo_screenshot.py` with a Node
ESM helper that reads configuration from environment variables, uses OS temp paths, and fails loudly on configuration or action
lookup errors. Update `SKILL.md` to describe generic shell-based execution plus an optional `playwright-cli` path.

**Tech Stack:** Markdown skill docs, Node.js ESM, Playwright for Node

---

### Task 1: Plan And Branch Context

**Files:**

- Modify: `.claude/skills/screenshot-odoo/SKILL.md`
- Modify: `.claude/skills/screenshot-odoo/odoo_screenshot.py`
- Create: `docs/superpowers/plans/2026-06-08-screenshot-odoo-portability.md`

- [ ] **Step 1: Confirm the current branch and existing skill files**

Run: `git status --short --branch` Expected: branch is `16.0-imp-screenshot-skill` with no tracked changes to the skill files
yet.

- [ ] **Step 2: Record the implementation scope in this plan file**

Write this file so the shared-entrypoint design and validation steps are captured before code changes begin.

### Task 2: Replace The Helper Script

**Files:**

- Delete: `.claude/skills/screenshot-odoo/odoo_screenshot.py`
- Create: `.claude/skills/screenshot-odoo/odoo_screenshot.mjs`

- [ ] **Step 1: Write the helper with portable configuration**

Create a Node ESM helper that:

- reads `ODOO_BASE_URL`, `ODOO_LOGIN`, `ODOO_ADMIN_PWD`, and `ODOO_SHOTS_DIR`
- uses `os.tmpdir()` when `ODOO_SHOTS_DIR` is unset
- resolves file paths with `path`
- prints absolute screenshot paths after a `---` separator

- [ ] **Step 2: Make failure modes explicit**

Implement checks that:

- throw if `ODOO_ADMIN_PWD` is missing
- throw if the login request returns to `/web/login`
- throw if action lookup returns no numeric id
- surface RPC errors from `/web/action/load`

- [ ] **Step 3: Preserve the view-injection workflow**

Keep a `# ------- VIEWS -------` block so the skill can still copy the helper to a temp file and append task-specific captures.

### Task 3: Rewrite The Shared Skill Instructions

**Files:**

- Modify: `.claude/skills/screenshot-odoo/SKILL.md`

- [ ] **Step 1: Replace runtime-specific assumptions**

Remove Claude-only wording such as `Bash tool`, `SendUserFile`, and `desktop-commander`, and replace it with generic shell-based
instructions that work in Codex and Claude.

- [ ] **Step 2: Document portable setup**

Add:

- Node.js and Playwright prerequisites
- the standard Playwright browser install command
- environment variables for base URL, login, password, and output directory
- Codex and Claude output guidance as plain runtime notes

- [ ] **Step 3: Add an optional Playwright CLI note**

Document `playwright-cli` as an optional execution path for agents that already use it, without making it the primary
implementation path.

### Task 4: Validate The Skill

**Files:**

- Test: `.claude/skills/screenshot-odoo/odoo_screenshot.mjs`
- Test: `.claude/skills/screenshot-odoo/SKILL.md`

- [ ] **Step 1: Run a syntax-level validation**

Run: `node --check .claude/skills/screenshot-odoo/odoo_screenshot.mjs` Expected: exit code `0`

- [ ] **Step 2: Run a live capture against local Odoo**

Use a temp copy of the helper with a known XML action such as `ni_flag.ni_flag_action`, set `ODOO_ADMIN_PWD`, and run the script
with Playwright available. Expected: one or more `OK <name>` lines and absolute PNG paths after `---`

- [ ] **Step 3: Confirm the doc matches reality**

Re-read `SKILL.md` and ensure the documented commands and environment variables match the helper that was validated.
