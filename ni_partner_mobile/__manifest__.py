#  Copyright (c) 2026 NSTDA
#  Based on res.partner mobile from Odoo 18.0 (Odoo S.A., LGPL-3).

{
    "name": "Partner - Mobile",
    "summary": "Bring back the contact mobile number removed from Odoo 19",
    "version": "19.0.1.0.0",
    "development_status": "Alpha",
    "category": "Tools",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["phone_validation"],
    "data": [
        "views/res_partner_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
