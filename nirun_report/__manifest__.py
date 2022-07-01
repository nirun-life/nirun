#  Copyright (c) 2021 NSTDA

{
    "name": "Nirun Report",
    "version": "13.0.0.2.1",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_patient"],
    "data": [
        "security/ir.model.access.csv",
        "security/report_rule.xml",
        "data/ir_cron_data.xml",
        "data/ir_sequence_data.xml",
        "views/demographic_views.xml",
        "views/demographic_line_views.xml",
        "views/demographic_code_views.xml",
        "views/report_menu.xml",
    ],
    "demo": [],
    "application": True,
    "auto_install": False,
    "installable": True,
}
