#  Copyright (c) 2021-2023 NSTDA

{
    "name": "Resource Calendar Copy",
    "summary": "Bulk copy resource calendars with ease",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Tools",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["resource"],
    "data": [
        "security/ir.model.access.csv",
        "views/resource_calendar_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
