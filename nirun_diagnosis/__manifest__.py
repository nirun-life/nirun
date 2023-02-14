#  Copyright (c) 2023-2023. NSTDA

{
    "name": "Diagnosis",
    "version": "13.0.0.1.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_patient", "nirun_condition", "nirun_procedure"],
    "data": [
        "data/diagnosis_role_data.xml",
        "security/ir.model.access.csv",
        "views/encounter_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
