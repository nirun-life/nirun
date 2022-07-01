#  Copyright (c) 2021 NSTDA

{
    "name": "Healthcare Services - Calendar",
    "version": "13.0.0.2.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_service", "calendar"],
    "data": [
        "data/calendar_data.xml",
        "views/calendar_views.xml",
        "views/service_views.xml",
        "views/service_menus.xml",
        "wizard/service_time_schedule.xml",
    ],
    "demo": [],
    "application": False,
    "auto_install": True,
    "installable": True,
}
