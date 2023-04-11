#  Copyright (c) 2021-2023 NSTDA

{
    "name": "Partner - Gender",
    "summary": "Add gender field to partner also default gender by selected title",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Tools",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["base"],
    "data": [
        "data/res_partner_tiltle_data.xml",
        "views/res_partner_views.xml",
        "views/res_partner_title_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
    "post_init_hook": "post_init_hook",
}
