#  Copyright (c) 2021-2023 NSTDA

{
    "name": "Partner - Age",
    "summary": "Add age, birthdate and deceased_date fields for partner",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Tools",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["base", "mail", "contacts"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/res_partner_age_range_view.xml",
        "data/ir_cron_data.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
