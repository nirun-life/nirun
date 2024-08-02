#  Copyright (c) 2021 NSTDA

{
    "name": "Related Person",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["ni_patient"],
    "data": [
        "data/ni.patient.relationship.csv",
        "security/ir.model.access.csv",
        "views/ni_patient_relationship_views.xml",
        "views/ni_patient_related_person.xml",
        "views/ni_patient_views.xml",
        # "views/ni_encounter_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
