#  Copyright (c) 2021-2023 NSTDA

{
    "name": "Organization",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": [
        "base",
        "ni_identifier",
        "ni_coding",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/res_company_type_data.xml",
        "views/res_company_views.xml",
        "views/res_company_type_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
