#  Copyright (c) 2021 NSTDA

{
    "name": "Patients Thai Localization",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "OPL-1",
    "maintainers": ["piruin"],
    "depends": ["ni_patient"],
    "data": [
        "security/res_group_data.xml",
        "security/ir.model.access.csv",
        "security/ir_rule_data.xml",
        "views/ni_patient_views.xml",
        "views/ni_patient_smartcard_views.xml",
        "views/menus.xml",
    ],
    "external_dependencies": {"python": ["stdnum"]},
    "application": False,
    "auto_install": False,
    "installable": True,
}
