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
    "depends": [
        "ni_patient",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/ni_device_views.xml",
        "views/ni_device_type_views.xml",
        "views/ni_device_metric_views.xml",
        "views/ni_device_holder.xml",
        "views/ni_device_menu.xml",
    ],
    "demo": [
        "demo/ni_device_type_demo.xml",
        "demo/ni_device_metric_demo.xml",
    ],
    "assets": {"web.assets_backend": []},
    "application": True,
    "auto_install": False,
    "installable": True,
}
