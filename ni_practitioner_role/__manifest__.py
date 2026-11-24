#  Copyright (c) 2023 NSTDA

{
    "name": "Practitioner Role",
    "summary": "User role and permission management for practitioners",
    "version": "19.0.1.0.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": [
        "auth_signup",
        "base_user_role",
        "ni_partner_mobile",
        "ni_partner_title",
        "ni_practitioner",
    ],
    "external_dependencies": {"python": ["qrcode"]},
    "data": [
        "views/res_user_role_views.xml",
        "views/res_user_views.xml",
        "security/ir_rule.xml",
        "views/ni_practitioner_role_template.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
