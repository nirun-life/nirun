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
        "ni_practitioner",
        "ni_communication",
        "ni_coverage",
    ],
    "data": [
        "data/ni_encounter_class_data.xml",
        "views/ni_encounter_class_views.xml",
        "reports/summary_report_templates.xml",
        "reports/summary_report.xml",
        "reports/medical_certificate_templates.xml",
        "reports/medical_certificate_report.xml",
        "reports/patient_signature_list_report_template.xml",
        "reports/patient_signature_list_report.xml",
        "views/res_company_views.xml",
    ],
    "assets": {
        "web.report_assets_pdf": ["ni_patient_summary_report/static/src/css/report.css"]
    },
    "application": False,
    "auto_install": False,
    "installable": True,
}
