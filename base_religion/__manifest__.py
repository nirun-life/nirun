#  Copyright (c) 2021 NSTDA

{
    "name": "Religions",
    "version": "13.0.0.1.1",
    "development_status": "Alpha",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "data/res_religion_data.xml",
        "views/res_religion_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}