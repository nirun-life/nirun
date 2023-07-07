#  Copyright (c) 2023 NSTDA

{
    "name": "Patients - Summary Report",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, DADOS, Harit, Kawin",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": [
        "ni_patient",
        "ni_allergy",
        "ni_observation",
        "ni_condition",
        "ni_procedure",
        "ni_medication",
        "ni_appointment",
    ],
    "data": [
        "views/ni_encounter_class_views.xml",
        "reports/summary_report_templates.xml",
        "reports/summary_report.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
