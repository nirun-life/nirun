#  Copyright (c) 2023 NSTDA

{
    "name": "Practitioner Role",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["base_user_role", "auth_signup", "hr"],
    "data": [
        # "security/ir.model.access.csv",
        "views/res_user_role_views.xml",
        "views/res_user_views.xml",
        "security/ir_rule.xml",
        "views/ni_practitioner_role_template.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
