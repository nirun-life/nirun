#  Copyright (c) 2021 Piruin P.

{
    "name": "Partner Age",
    "summary": "Add age, birthdate and deceased_date fields for partner",
    "version": "13.0.0.3.0",
    "development_status": "Alpha",
    "category": "Tools",
    "author": "Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["base", "mail", "contacts"],
    "data": [
        "security/ir.model.access.csv",
        "views/partner_views.xml",
        "views/partner_age_range_view.xml",
        "data/cron.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
