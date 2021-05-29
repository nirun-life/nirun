#  Copyright (c) 2021 Piruin P.

{
    "name": "Nirun",
    "version": "13.0.0.2.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["base"],
    "data": [
        "security/nirun_group.xml",
        "security/ir.model.access.csv",
        "data/res_company_data.xml",
        "data/ni.quantity.unit.csv",
        "data/ni.timing.event.csv",
        "data/ni.timing.template.csv",
        "data/ni.timing.dow.csv",
        "views/quantity_unit_views.xml",
        "views/timing_views.xml",
        "views/timing_template_views.xml",
    ],
    "demo": ["security/nirun_group_demo.xml"],
    "application": False,
    "auto_install": False,
    "installable": True,
}
