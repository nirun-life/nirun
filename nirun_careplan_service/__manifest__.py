#  Copyright (c) 2021 Piruin P.

{
    "name": "Care Plans - Healthcare Services",
    "version": "13.0.0.2.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_careplan", "nirun_service"],
    "data": [
        "views/careplan_activity_views.xml",
        "views/service_request_views.xml",
        "wizard/activity_generator.xml",
    ],
    "application": False,
    "auto_install": True,
    "installable": True,
}
