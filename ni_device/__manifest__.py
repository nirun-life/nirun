#  Copyright (c) 2021-2023 NSTDA

{
    "name": "Device",
    "version": "16.0.0.3.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["ni_patient", "ni_observation"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/ni_device_views.xml",
        "views/ni_device_type_views.xml",
        "views/ni_device_request_views.xml",
        "views/ni_device_holder_views.xml",
        "views/ni_device_repair_views.xml",
        "views/ni_device_dispose_type_views.xml",
        "views/ni_device_menu.xml",
    ],
    "demo": [
        "demo/ni_device_type_demo.xml",
        "demo/ni_device_dispose_type_demo.xml",
    ],
    "assets": {"web.assets_backend": []},
    "application": False,
    "auto_install": False,
    "installable": True,
}
