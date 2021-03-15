#  Copyright (c) 2021 Piruin P.

{
    "name": "Patients - Contacts",
    "version": "13.0.0.1.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_patient"],
    "data": [
        "data/ni.patient.relationship.csv",
        "security/ir.model.access.csv",
        "views/patient_relationship_views.xml",
        "views/patient_contact_views.xml",
        "views/patient_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
