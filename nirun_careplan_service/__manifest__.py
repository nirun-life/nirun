#  Copyright (c) 2021 NSTDA

{
    "name": "Care Plans - Healthcare Services",
    "version": "13.0.0.3.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_careplan", "nirun_service"],
    "data": [
        "views/careplan_activity_views.xml",
        "views/service_request_views.xml",
        "views/service_category_views.xml",
        "wizard/activity_generator.xml",
    ],
    "application": False,
    "auto_install": True,
    "installable": False,
}
