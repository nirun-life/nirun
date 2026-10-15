#  Copyright (c) 2026 NSTDA
#  Based on res.partner.title from Odoo 18.0 (Odoo S.A., LGPL-3).

{
    "name": "Partner - Titles",
    "summary": "Bring back contact titles (Mister, Madam, ...) removed from Odoo 19",
    "version": "19.0.1.0.0",
    "development_status": "Alpha",
    "category": "Tools",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["contacts"],
    "data": [
        "security/ir.model.access.csv",
        "data/res_partner_title_data.xml",
        "views/res_partner_title_views.xml",
        "views/res_partner_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
