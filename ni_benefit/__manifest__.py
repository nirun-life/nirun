#  Copyright (c) 2024 NSTDA

{
    "name": "Nirun - Benefit",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["ni_patient"],
    "data": [
        "security/ir.model.access.csv",
        "data/ni_benefit_data.xml",
        "views/ni_benefit_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
