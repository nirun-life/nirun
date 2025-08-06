#  Copyright (c) 2023-2023. NSTDA

{
    "name": "Presense Link",
    "version": "13.0.0.1.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_patient"],
    "data": [
        "datas/ir_config_parameter_data.xml",
        "views/ni_patient_view.xml",
        "views/ni_encounter_view.xml",
    ],
    "external_dependencies": {
        "python": ["cryptography"]
    },
    "application": False,
    "auto_install": False,
    "installable": True,
}
