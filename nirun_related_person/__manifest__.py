#  Copyright (c) 2021 NSTDA

{
    "name": "Related Person",
    "version": "13.0.0.3.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_patient"],
    "data": [
        "data/res.partner.relationship.csv",
        "security/ir.model.access.csv",
        "views/relationship_views.xml",
        "views/partner_views.xml",
        "views/patient_views.xml",
        "views/encounter_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
