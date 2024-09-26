#  Copyright (c) 2021-2023 NSTDA

{
    "name": "Document Reference",
    "version": "16.0.0.2.1",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["ni_patient"],
    "data": [
        "security/ir.model.access.csv",
        "security/ni_document_ref_rule.xml",
        "data/ni_document_ref_category_data.xml",
        "data/ni_document_ref_type_data.xml",
        "data/ir_sequence_data.xml",
        "views/ni_document_ref_category_views.xml",
        "views/ni_document_ref_type_views.xml",
        "views/ni_document_ref_views.xml",
        "views/ni_document_ref_menu.xml",
        "views/ni_encounter_views.xml",
        "reports/ni_document_ref_report.xml",
        "reports/ni_document_ref_templates.xml",
        "reports/summary_report.xml",
        "views/hr_job_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/ni_document_ref/static/src/scss/kanban.scss",
        ],
    },
    "demo": [],
    "application": False,
    "auto_install": False,
    "installable": True,
}
