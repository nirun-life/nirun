#  Copyright (c) 2021-2023 NSTDA

{
    "name": "ICD-10-TM",
    "summary": "International Classification of diseases and Related Health Problems, 10th Revision, Thai Modification",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["ni_condition"],
    "data": [
        "security/ir.model.access.csv",
        "views/ni_condition_code_views.xml",
        "views/ni_condition_chapter_views.xml",
        "views/ni_condition_block_views.xml",
        "data/ni_coding_system_data.xml",
        "data/ni.condition.chapter.csv",
        "data/ni.condition.block.csv",
        "data/ni.condition.code.csv",
        "data/ni_encounter_diagnosis_role_data.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
