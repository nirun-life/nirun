#  Copyright (c) 2021 NSTDA

{
    "name": "Partner Gender",
    "summary": "Add gender field to partner also default gender by selected title",
    "version": "13.0.0.2.0",
    "development_status": "Alpha",
    "category": "Tools",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["base"],
    "data": ["views/partner_views.xml", "views/partner_title_views.xml"],
    "application": False,
    "auto_install": False,
    "installable": True,
    "post_init_hook": "post_init_hook",
}
