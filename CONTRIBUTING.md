# Contributing

Thanks for contributing to Nirun. This project follows the [Code of Conduct](CODE_OF_CONDUCT.md).

## Table of Contents

- [Development Setup](#development-setup)
- [Making a Change](#making-a-change)
- [Code Style](#code-style)
- [Commit Messages](#commit-messages)
- [Pull Requests](#pull-requests)
- [Reporting Issues](#reporting-issues)
- [Security Issues](#security-issues)

## Development Setup

**Runtime:** Odoo 16.0, Python 3.10.

**Local:** Install [Odoo 16.0](https://www.odoo.com/documentation/16.0/administration/on_premise/source.html), then create an
`odoo.conf` pointing `addons_path` at your local Odoo installation and this repo. `odoo.conf` is untracked (gitignored) since it
holds machine-specific paths and credentials. Sample:

```ini
[options]
addons_path = /path/to/odoo/addons,/path/to/nirun
admin_passwd = change-me
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
dbfilter = nirun.*
http_port = 8069
without_demo = all
```

Use a virtualenv rather than installing dependencies into your system Python. Create it once inside your Odoo source checkout
and install Odoo's own dependencies:

```bash
# one-time setup
cd /path/to/odoo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then, whenever you work on this repo, activate that same venv, install this repo's dependencies, and run `odoo-bin` from the
Odoo checkout against this repo's `odoo.conf`:

```bash
source /path/to/odoo/.venv/bin/activate
pip install -r requirements.txt
pip install -r test-requirements.txt
python /path/to/odoo/odoo-bin -c odoo.conf -u <module_name>
```

Install pre-commit hooks:

```
pre-commit install
```

**Docker:** A `Dockerfile` is provided as a ready-to-run alternative if you don't want a local install. It requires a reachable
PostgreSQL instance (see Requirements in [README.md](README.md)):

```bash
docker build -t nirun .
docker run -p 8069:8069 nirun
```

## Making a Change

1. Create a branch off the version branch you're targeting (e.g. `16.0`).
2. Make your change. Prefer editing existing modules over adding new ones.
3. Add or update the `README.md` in any module you change — purpose, main models/views, and dependencies should reflect the
   current code.
4. Run tests for the affected module(s):
   ```bash
   (venv) python /path/to/odoo/odoo-bin -c odoo.conf -i module_name --test-enable
   ```
5. Run `pre-commit run --all-files` before opening a PR.

## Code Style

Full reference:
[Odoo 16.0 Coding Guidelines](https://www.odoo.com/documentation/16.0/contributing/development/coding_guidelines.html).

**TL;DR:**

- Module layout: business logic lives in `models/`, `views/`, `data/`, `controllers/`, `static/`; optional `wizard/` (transient
  models), `report/`, `tests/`.
- Python: prefer many small, single-responsibility methods over few large ones; imports ordered stdlib → odoo → odoo-addons,
  alphabetized within each group; never call `cr.commit()` inside business logic; always wrap user-facing strings with `_()`,
  never concatenate translated strings.
- Model attribute order:
  1. Private attributes (`_name`, `_description`, `_inherit`, `_sql_constraints`, …)
  2. Default methods and `default_get`
  3. Field declarations
  4. Compute, inverse, and search methods, in the same order as their field declarations
  5. Selection methods (methods returning computed values for selection fields)
  6. `@api.constrains` and `@api.onchange` methods
  7. CRUD methods (ORM overrides)
  8. Action methods
  9. Other business methods
- Naming: models are singular (`res.partner`, not `res.partners`); XML ids follow `<model>_menu`, `<model>_view_<type>`,
  `<model>_action`; inherited views reuse the parent record's XML id with an `.inherit.<detail>` suffix.
- CSS/SCSS: 4-space indent; order properties outside-in (position first, decorative rules like `font`/`filter` last); scoped
  SCSS/CSS variables go at the top of a block followed by a blank line; prefix classes with `o_<module_name>` (avoid id
  selectors); CSS variables are for contextual, component-local adaptation, not a global design system.

All formatting is enforced via pre-commit. Run manually with `pre-commit run --all-files`.

- **Python:** black (line length 88), autoflake, isort, flake8 (max line 120), pylint-odoo
- **XML:** prettier with `--print-width=120`
- **JavaScript:** eslint
- isort import order: `FUTURE, STDLIB, THIRDPARTY, ODOO, ODOO_ADDONS, FIRSTPARTY, LOCALFOLDER`
- All files must have LF line endings and no trailing whitespace

Manifests require: `license` key (LGPL-3 or OPL-1), `author` must include "NSTDA".

All new files must include a copyright header at the top:

```python
#  Copyright (c) <year> NSTDA
```

## Commit Messages

Use the [Odoo convention](https://www.odoo.com/documentation/16.0/contributing/development/git_guidelines.html#):
`[TAG] module: short description`, e.g. `[FIX] ni_patient: prevent crash on missing address`. Common tags: `FIX`, `IMP`, `ADD`,
`REF`, `REM`, `CLN`. Keep the subject under 72 characters, imperative mood, no trailing period.

```
[FIX] website: remove unused alert div, fixes look of input-group-btn

 Bootstrap's CSS depends on the input-group-btn
 element being the first/last child of its parent.
 This was not the case because of the invisible
 and useless alert.

 Closes #22954
```

**Note:** Do not add AI attribution (e.g. `Co-Authored-By: Claude`) or any AI-tool byline to commit messages.

## Pull Requests

Fill in the [PR template](.github/pull_request_template.md): what changed, why (link the issue with `Closes #`), scope,
risk/impact, how you tested it, and whether the module `README.md` needs updating.

- Keep PRs focused on one change.
- Squash your own intermediate/fixup commits before requesting review — the commit history should show the minimum necessary
  commits, not your back-and-forth while developing. Use `git rebase -i HEAD~N` (N = number of commits) and mark all but the
  first as `fixup`.
- Ensure CI (pre-commit + tests) passes before requesting review.

## Reporting Issues

Open a GitHub issue using the matching template — each type has its own required fields:

- **Bug** — unexpected behavior or regression
- **Change Request** — requirement change, scope adjustment, or behavior update
- **Task** — new feature, improvement, or research note

## Security Issues

Do not open a public issue. See [SECURITY.md](SECURITY.md) for how to report a vulnerability.
