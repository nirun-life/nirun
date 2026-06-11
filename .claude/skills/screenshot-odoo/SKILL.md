---
name: screenshot-odoo
description: >-
  Take screenshots of the running Nirun/Odoo app at http://localhost:16669. Use when asked to show the UI, verify a feature
  visually, take screenshots for a PR, or confirm a change works in the browser. Invoke as /screenshot-odoo [optional:
  comma-separated list of views to capture].
---

# Odoo Screenshot Skill

Takes screenshots of the Nirun Odoo app using Node Playwright (headless Chromium).

## Prerequisites

Requirements:

- Node.js 20 or newer
- A resolvable Node `playwright` package
- Chromium browser binaries installed for that Playwright version

Standard setup:

```bash
npm install --save-dev playwright
npx playwright install chromium
```

If your environment already bundles Playwright in a nonstandard location, set `PLAYWRIGHT_MODULE` to a path that Node can
`require(...)`.

Optional agent-centric setup:

```bash
npx playwright-cli --help
```

`playwright-cli` can help with browser tooling for some agents, but this helper script still runs against the Node `playwright`
library.

## Configuration

Environment variables:

- `ODOO_BASE_URL`: defaults to `http://localhost:16669`
- `ODOO_DB`: optional database name; recommended for multi-database Odoo instances
- `ODOO_LOGIN`: defaults to `admin`
- `ODOO_ADMIN_PWD`: required
- `ODOO_SHOTS_DIR`: optional output directory; defaults to an OS temp folder
- `PLAYWRIGHT_MODULE`: optional override when `playwright` is not on the normal Node resolution path

## Workflow

1. Read `.claude/skills/screenshot-odoo/odoo_screenshot.mjs`
2. Copy it to a temp file, filling in the `# ------- VIEWS -------` section
3. Export `ODOO_ADMIN_PWD` and any optional overrides such as `ODOO_DB`
4. Run the temp copy from a shell
5. Return the captured screenshots to the user using your runtime's normal file or inline-image mechanism
6. Ask user if there want to save into module's `/static/screenshot/`

## Script

Base script: `.claude/skills/screenshot-odoo/odoo_screenshot.mjs`

Helpers already defined there: `resolveConfig()`, `login()`, `dismiss()`, `screenshot()`, `actionId()`.

Add views inside `run()` after `await login(page)`:

```js
// Resolve action to numeric ID (required - hash URLs reject xml IDs)
const aid = await actionId(page, "ni_flag.ni_flag_action");

// Navigate and shoot
await page.goto(`${config.baseUrl}/web#action=${aid}`);
await page.waitForLoadState("domcontentloaded");
shots.push(await screenshot(page, config.outDir, "flag_list"));

// Form record
await page.goto(`${config.baseUrl}/web#action=${aid}&id=1&view_type=form`);
await page.waitForLoadState("domcontentloaded");
shots.push(await screenshot(page, config.outDir, "flag_form"));

// Pivot
await page.goto(`${config.baseUrl}/web#action=${aid}&view_type=pivot`);
await page.waitForLoadState("domcontentloaded");
shots.push(await screenshot(page, config.outDir, "flag_pivot"));

// Patient kanban
const patientActionId = await actionId(page, "ni_patient.patient_action");
await page.goto(`${config.baseUrl}/web#action=${patientActionId}&view_type=kanban`);
await page.waitForLoadState("domcontentloaded");
shots.push(await screenshot(page, config.outDir, "patient_kanban", 2500));
```

## Running

```bash
node /path/to/temp/odoo_ss.mjs
```

Output lines after `---` are absolute paths to saved PNGs.

Runtime notes:

- In Codex, prefer returning screenshots inline in the response or as local file links.
- In Claude, return screenshots using Claude's normal file-sharing path.

## Odoo Server

If the Odoo server is not already running, start it using the repo's normal Odoo command for your platform. In this repo, the
portable pattern is:

```bash
$ODOO_BIN -c odoo.conf --http-port=16669
```

Wait ~5 s before navigating.

## Known Issues

- `waitForLoadState("networkidle")` hangs because of Odoo long-polling. Use `"domcontentloaded"` plus an explicit wait.
- `#action=xml.id` does not work. Resolve the XML ID to a numeric action first with `actionId()`.
- Multi-database Odoo setups may reject valid credentials unless `ODOO_DB` is set.
- A custom action XML ID can still fail if the local Odoo registry is missing the target model. Try a core action first to
  separate environment issues from helper issues.
- `searchpanel` only accepts `many2one` or `selection`, never `many2many` or `one2many`.
- Dismiss startup dialogs before shooting. `dismiss()` is best-effort, not a guarantee.
- If Playwright cannot be imported, install the Node package or set `PLAYWRIGHT_MODULE`.

## Action XML IDs (project reference)

| View                | XML ID                                       |
| ------------------- | -------------------------------------------- |
| Patient list/kanban | `ni_patient.patient_action`                  |
| Encounter list      | `ni_patient.ni_encounter_action`             |
| Flags               | `ni_flag.ni_flag_action`                     |
| Flag Codes          | `ni_flag.ni_flag_code_action`                |
| Observations        | `ni_observation.ni_observation_sheet_action` |
| Conditions          | `ni_condition.ni_condition_action`           |
