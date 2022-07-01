#  Copyright (c) 2021 NSTDA

{
    "name": "Observation - RESTful API",
    "version": "13.0.0.3.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": [
        "nirun_observation",
        "nirun_patient_api",
        "base_rest",
        "base_rest_datamodel",
        "component",
    ],
    "external_dependencies": {"python": ["marshmallow", "marshmallow_objects"]},
    "application": False,
    "auto_install": True,
    "installable": True,
}
