#  Copyright (c) 2023 NSTDA

{
    "name": "Appointment - Website",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["ni_appointment", "website", "partner_location"],
    "data": [
        "data/website_data.xml",
        "views/ni_appointment_template.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
