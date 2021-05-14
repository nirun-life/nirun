#  Copyright (c) 2021 Piruin P.

{
    "name": "Healthcare Services",
    "version": "13.0.0.1.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_patient"],
    "data": [
        "security/service_group.xml",
        "security/ir.model.access.csv",
        "data/service_category_data.xml",
        "views/service_category_views.xml",
        "views/service_timing_views.xml",
        "views/service_request_views.xml",
        "views/service_view.xml",
        "views/service_menus.xml",
    ],
    "application": True,
    "auto_install": False,
    "installable": True,
}
