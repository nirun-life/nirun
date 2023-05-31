#  Copyright (c) 2021-2023 NSTDA

{
    "name": "ICD-9-CM Classification of Procedure",
    "summary": """
    International Classification of diseases, 9th Revision, Clinical Modification
    """,
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["ni_procedure"],
    "data": [
        "security/ir.model.access.csv",
        "views/ni_condition_code_views.xml",
        "views/ni_condition_chapter_views.xml",
        "data/ni_coding_system_data.xml",
        "data/ni_procedure_chapter_data.xml",
        "data/ni_procedure_code_data.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
