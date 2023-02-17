#  Copyright (c) 2021-2023. NSTDA

{
    "name": "Nirun - DOP",
    "version": "13.0.0.1.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "OPL-1",
    "maintainers": ["piruin"],
    "depends": [
        "nirun",
        "nirun_patient",
        "nirun_careplan",
        "nirun_medication",
        "nirun_medication_condition",
    ],
    "data": [
        # "views/patient_views.xml",
        "views/careplan_views.xml",
        "views/encounter_views.xml",
        "views/condition_views.xml",
        "views/goal_views.xml",
        "views/medication_statement_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
