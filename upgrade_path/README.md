# Upgrade path for OpenUpgrade

Extra migration scripts for core modules, used next to OpenUpgrade when a Nirun database
is upgraded from one version to the next. Odoo merges the scripts of every
`--upgrade-path` entry, so pass this folder after OpenUpgrade's own scripts:

```bash
--upgrade-path=<OpenUpgrade-19>/openupgrade_scripts/scripts,<nirun-19.0>/upgrade_path
```

| Script                                       | Why                                                                                                                                                                                                                                                                                                                            |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `base/19.0.1.3/post-nirun_partner_mobile.py` | Odoo 19 dropped the partner mobile. OpenUpgrade merges it into `phone`; `ni_patient` keeps it through `ni_partner_mobile`, so the original phone is restored from OpenUpgrade's legacy copy. Runs only when `ni_patient` is installed.                                                                                         |
| `base/19.0.1.3/pre-nirun_partner_title.py`   | Odoo 19 dropped partner titles. Hands the `res_partner_title` table, its xmlids and the `res_partner.title` column over to `ni_partner_title` (`title_id`) before that module is installed, so titles survive the 18→19 step. Runs only when `partner_gender` is installed.                                                    |
| `uom/19.0.1.0/post-nirun_uom_bigger.py`      | OpenUpgrade 19 converts user-created "bigger" units (no xmlid) with an inverted ratio (`relative_factor = factor` instead of `1 / factor`). Recomputes them from OpenUpgrade's legacy columns; units with an xmlid are left to their modules (`ni_observation` converts its own). Drop it once OCA/OpenUpgrade#6054 is merged. |

The scripts only run during an OpenUpgrade step; a normal module update ignores them.
